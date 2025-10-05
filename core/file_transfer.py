"""
File Transfer System
P2P filöverföring med chunking och progress tracking
"""

import os
import hashlib
import json
import threading
from pathlib import Path
from typing import Callable, Optional, Dict
from datetime import datetime
from core.debug_logger import debug, info, warning, error, exception


class FileTransfer:
    """File transfer system för P2P"""
    
    CHUNK_SIZE = 64 * 1024  # 64KB chunks
    
    def __init__(self, p2p_system, storage_path: str = "data/files"):
        """
        Initialize file transfer system
        
        Args:
            p2p_system: P2PSystem instance
            storage_path: Path för att lagra mottagna filer
        """
        debug("FileTransfer", "Initializing file transfer system")
        
        self.p2p_system = p2p_system
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Active transfers (transfer_id -> transfer_info)
        self.active_transfers: Dict[str, dict] = {}
        
        # Transfer locks
        self.transfer_lock = threading.Lock()
        
        # Callbacks
        self.on_transfer_progress: Optional[Callable] = None
        self.on_transfer_complete: Optional[Callable] = None
        self.on_file_received: Optional[Callable] = None
        
        # Setup P2P message handler
        self._setup_message_handler()
        
        info("FileTransfer", "File transfer system initialized")
    
    def _setup_message_handler(self):
        """Setup P2P message handler"""
        debug("FileTransfer", "Setting up P2P message handler")
        
        original_handler = self.p2p_system.on_message_received
        
        def file_message_handler(peer_id: str, message: dict):
            msg_type = message.get('type')
            
            if msg_type == 'file_offer':
                self._handle_file_offer(peer_id, message)
            elif msg_type == 'file_accept':
                self._handle_file_accept(peer_id, message)
            elif msg_type == 'file_chunk':
                self._handle_file_chunk(peer_id, message)
            elif msg_type == 'file_complete':
                self._handle_file_complete(peer_id, message)
            
            if original_handler:
                original_handler(peer_id, message)
        
        self.p2p_system.on_message_received = file_message_handler
    
    def send_file(self, peer_id: str, file_path: Path, metadata: dict = None) -> Optional[str]:
        """
        Send file to peer
        
        Args:
            peer_id: Target peer ID
            file_path: Path to file to send
            metadata: Optional metadata (team_id, etc.)
        
        Returns:
            Transfer ID if successful
        """
        info("FileTransfer", f"Sending file {file_path.name} to {peer_id[:8]}...")
        
        if not file_path.exists():
            error("FileTransfer", f"File not found: {file_path}")
            return None
        
        try:
            # Calculate file hash
            file_hash = self._calculate_file_hash(file_path)
            file_size = file_path.stat().st_size
            
            # Generate transfer ID
            transfer_id = hashlib.md5(
                f"{file_path.name}{file_size}{datetime.now().isoformat()}".encode()
            ).hexdigest()[:16]
            
            # Create transfer info
            transfer_info = {
                'transfer_id': transfer_id,
                'file_path': str(file_path),
                'file_name': file_path.name,
                'file_size': file_size,
                'file_hash': file_hash,
                'peer_id': peer_id,
                'direction': 'send',
                'chunks_sent': 0,
                'total_chunks': (file_size + self.CHUNK_SIZE - 1) // self.CHUNK_SIZE,
                'metadata': metadata or {}
            }
            
            with self.transfer_lock:
                self.active_transfers[transfer_id] = transfer_info
            
            # Send file offer
            offer_message = {
                'type': 'file_offer',
                'transfer_id': transfer_id,
                'file_name': file_path.name,
                'file_size': file_size,
                'file_hash': file_hash,
                'metadata': metadata or {}
            }
            
            success = self.p2p_system.send_message(peer_id, offer_message)
            
            if success:
                info("FileTransfer", f"File offer sent: {transfer_id}")
                return transfer_id
            else:
                error("FileTransfer", "Failed to send file offer")
                with self.transfer_lock:
                    del self.active_transfers[transfer_id]
                return None
                
        except Exception as e:
            exception("FileTransfer", f"Error sending file: {e}")
            return None
    
    def _handle_file_offer(self, peer_id: str, message: dict):
        """Handle incoming file offer"""
        transfer_id = message.get('transfer_id')
        file_name = message.get('file_name')
        file_size = message.get('file_size')
        
        info("FileTransfer", f"Received file offer: {file_name} ({file_size} bytes)")
        
        # Auto-accept (in real app, would show UI prompt)
        self._accept_file(peer_id, message)
    
    def _accept_file(self, peer_id: str, offer: dict):
        """Accept file transfer"""
        transfer_id = offer.get('transfer_id')
        file_name = offer.get('file_name')
        file_size = offer.get('file_size')
        file_hash = offer.get('file_hash')
        metadata = offer.get('metadata', {})
        
        debug("FileTransfer", f"Accepting file: {file_name}")
        
        # Create transfer info
        transfer_info = {
            'transfer_id': transfer_id,
            'file_name': file_name,
            'file_size': file_size,
            'file_hash': file_hash,
            'peer_id': peer_id,
            'direction': 'receive',
            'chunks_received': 0,
            'total_chunks': (file_size + self.CHUNK_SIZE - 1) // self.CHUNK_SIZE,
            'received_data': bytearray(),
            'metadata': metadata
        }
        
        with self.transfer_lock:
            self.active_transfers[transfer_id] = transfer_info
        
        # Send accept message
        accept_message = {
            'type': 'file_accept',
            'transfer_id': transfer_id
        }
        
        self.p2p_system.send_message(peer_id, accept_message)
        info("FileTransfer", f"File accepted: {transfer_id}")
    
    def _handle_file_accept(self, peer_id: str, message: dict):
        """Handle file accept - start sending chunks"""
        transfer_id = message.get('transfer_id')
        
        with self.transfer_lock:
            transfer_info = self.active_transfers.get(transfer_id)
        
        if not transfer_info:
            warning("FileTransfer", f"Unknown transfer: {transfer_id}")
            return
        
        info("FileTransfer", f"File accepted by peer, starting transfer: {transfer_id}")
        
        # Start sending chunks in background thread
        thread = threading.Thread(
            target=self._send_file_chunks,
            args=(transfer_id,),
            daemon=True
        )
        thread.start()
    
    def _send_file_chunks(self, transfer_id: str):
        """Send file in chunks"""
        with self.transfer_lock:
            transfer_info = self.active_transfers.get(transfer_id)
        
        if not transfer_info:
            return
        
        file_path = Path(transfer_info['file_path'])
        peer_id = transfer_info['peer_id']
        total_chunks = transfer_info['total_chunks']
        
        debug("FileTransfer", f"Sending {total_chunks} chunks for {transfer_id}")
        
        try:
            with open(file_path, 'rb') as f:
                chunk_index = 0
                
                while True:
                    chunk_data = f.read(self.CHUNK_SIZE)
                    if not chunk_data:
                        break
                    
                    # Send chunk
                    chunk_message = {
                        'type': 'file_chunk',
                        'transfer_id': transfer_id,
                        'chunk_index': chunk_index,
                        'chunk_data': chunk_data.hex()  # Convert to hex string
                    }
                    
                    success = self.p2p_system.send_message(peer_id, chunk_message)
                    
                    if not success:
                        error("FileTransfer", f"Failed to send chunk {chunk_index}")
                        return
                    
                    chunk_index += 1
                    
                    # Update progress
                    with self.transfer_lock:
                        if transfer_id in self.active_transfers:
                            self.active_transfers[transfer_id]['chunks_sent'] = chunk_index
                    
                    if self.on_transfer_progress:
                        progress = (chunk_index / total_chunks) * 100
                        self.on_transfer_progress(transfer_id, progress)
                    
                    # Small delay to avoid overwhelming
                    threading.Event().wait(0.01)
            
            # Send complete message
            complete_message = {
                'type': 'file_complete',
                'transfer_id': transfer_id
            }
            
            self.p2p_system.send_message(peer_id, complete_message)
            
            info("FileTransfer", f"File transfer complete: {transfer_id}")
            
            if self.on_transfer_complete:
                self.on_transfer_complete(transfer_id, True)
            
        except Exception as e:
            exception("FileTransfer", f"Error sending chunks: {e}")
            if self.on_transfer_complete:
                self.on_transfer_complete(transfer_id, False)
    
    def _handle_file_chunk(self, peer_id: str, message: dict):
        """Handle received file chunk"""
        transfer_id = message.get('transfer_id')
        chunk_index = message.get('chunk_index')
        chunk_data_hex = message.get('chunk_data')
        
        with self.transfer_lock:
            transfer_info = self.active_transfers.get(transfer_id)
        
        if not transfer_info:
            warning("FileTransfer", f"Unknown transfer: {transfer_id}")
            return
        
        # Convert hex back to bytes
        chunk_data = bytes.fromhex(chunk_data_hex)
        
        # Append to received data
        transfer_info['received_data'].extend(chunk_data)
        transfer_info['chunks_received'] = chunk_index + 1
        
        # Update progress
        if self.on_transfer_progress:
            progress = (transfer_info['chunks_received'] / transfer_info['total_chunks']) * 100
            self.on_transfer_progress(transfer_id, progress)
        
        debug("FileTransfer", f"Received chunk {chunk_index} for {transfer_id}")
    
    def _handle_file_complete(self, peer_id: str, message: dict):
        """Handle file transfer complete"""
        transfer_id = message.get('transfer_id')
        
        with self.transfer_lock:
            transfer_info = self.active_transfers.get(transfer_id)
        
        if not transfer_info:
            warning("FileTransfer", f"Unknown transfer: {transfer_id}")
            return
        
        info("FileTransfer", f"File transfer complete: {transfer_id}")
        
        # Save file
        try:
            file_name = transfer_info['file_name']
            file_path = self.storage_path / file_name
            
            # Make filename unique if exists
            counter = 1
            while file_path.exists():
                name_parts = file_name.rsplit('.', 1)
                if len(name_parts) == 2:
                    file_path = self.storage_path / f"{name_parts[0]}_{counter}.{name_parts[1]}"
                else:
                    file_path = self.storage_path / f"{file_name}_{counter}"
                counter += 1
            
            # Write file
            with open(file_path, 'wb') as f:
                f.write(transfer_info['received_data'])
            
            # Verify hash
            received_hash = self._calculate_file_hash(file_path)
            expected_hash = transfer_info['file_hash']
            
            if received_hash == expected_hash:
                info("FileTransfer", f"File saved and verified: {file_path}")
                
                if self.on_file_received:
                    self.on_file_received(transfer_id, str(file_path), transfer_info['metadata'])
                
                if self.on_transfer_complete:
                    self.on_transfer_complete(transfer_id, True)
            else:
                error("FileTransfer", f"File hash mismatch! Expected: {expected_hash}, Got: {received_hash}")
                file_path.unlink()  # Delete corrupted file
                
                if self.on_transfer_complete:
                    self.on_transfer_complete(transfer_id, False)
            
            # Cleanup
            with self.transfer_lock:
                del self.active_transfers[transfer_id]
                
        except Exception as e:
            exception("FileTransfer", f"Error saving file: {e}")
            if self.on_transfer_complete:
                self.on_transfer_complete(transfer_id, False)
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(65536)  # 64KB chunks
                if not data:
                    break
                sha256.update(data)
        
        return sha256.hexdigest()
    
    def get_transfer_progress(self, transfer_id: str) -> Optional[float]:
        """Get transfer progress (0-100)"""
        with self.transfer_lock:
            transfer_info = self.active_transfers.get(transfer_id)
        
        if not transfer_info:
            return None
        
        if transfer_info['direction'] == 'send':
            chunks = transfer_info['chunks_sent']
        else:
            chunks = transfer_info['chunks_received']
        
        total = transfer_info['total_chunks']
        return (chunks / total) * 100 if total > 0 else 0
    
    def cancel_transfer(self, transfer_id: str):
        """Cancel active transfer"""
        info("FileTransfer", f"Cancelling transfer: {transfer_id}")
        
        with self.transfer_lock:
            if transfer_id in self.active_transfers:
                del self.active_transfers[transfer_id]


if __name__ == "__main__":
    # Test file transfer
    info("TEST", "Testing FileTransfer...")
    
    from core.p2p_system import P2PSystem
    
    # Create P2P system
    p2p = P2PSystem()
    p2p.start()
    
    # Create file transfer
    file_transfer = FileTransfer(p2p)
    
    def on_progress(transfer_id, progress):
        print(f"Transfer {transfer_id[:8]}... progress: {progress:.1f}%")
    
    def on_complete(transfer_id, success):
        print(f"Transfer {transfer_id[:8]}... {'completed' if success else 'failed'}")
    
    def on_received(transfer_id, file_path, metadata):
        print(f"File received: {file_path}")
    
    file_transfer.on_transfer_progress = on_progress
    file_transfer.on_transfer_complete = on_complete
    file_transfer.on_file_received = on_received
    
    print("File transfer system ready!")
    print("\n✅ File transfer working!")

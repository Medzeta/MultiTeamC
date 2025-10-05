"""
File Transfer Progress System
Visar progress bars för filöverföringar
"""

import threading
from typing import Dict, Optional, Callable
from datetime import datetime
from core.debug_logger import debug, info, warning, error


class FileProgress:
    """System för file transfer progress tracking"""
    
    def __init__(self):
        """Initialize file progress system"""
        debug("FileProgress", "Initializing file progress system")
        
        self.transfers: Dict[str, Dict] = {}  # transfer_id -> progress data
        self.lock = threading.Lock()
        
        # Callbacks
        self.on_progress_update: Optional[Callable] = None
        self.on_transfer_complete: Optional[Callable] = None
        self.on_transfer_failed: Optional[Callable] = None
        self.on_transfer_started: Optional[Callable] = None
        
        info("FileProgress", "File progress system initialized")
    
    def start_transfer(
        self,
        transfer_id: str,
        file_name: str,
        file_size: int,
        direction: str = 'upload'
    ):
        """
        Start tracking a file transfer
        
        Args:
            transfer_id: Unique transfer ID
            file_name: Name of file
            file_size: Total file size in bytes
            direction: 'upload' or 'download'
        """
        debug("FileProgress", f"Starting transfer tracking: {file_name} ({file_size} bytes) - {direction}")
        
        with self.lock:
            self.transfers[transfer_id] = {
                'file_name': file_name,
                'file_size': file_size,
                'bytes_transferred': 0,
                'direction': direction,
                'status': 'active',
                'start_time': datetime.now(),
                'progress_percent': 0,
                'speed_bps': 0,
                'eta_seconds': 0
            }
        
        # Callback
        if self.on_transfer_started:
            self.on_transfer_started(transfer_id, self.transfers[transfer_id])
        
        info("FileProgress", f"Transfer started: {transfer_id[:8]}... - {file_name}")
    
    def update_progress(self, transfer_id: str, bytes_transferred: int):
        """
        Update transfer progress
        
        Args:
            transfer_id: Transfer ID
            bytes_transferred: Total bytes transferred so far
        """
        if transfer_id not in self.transfers:
            warning("FileProgress", f"Transfer not found: {transfer_id[:8]}...")
            return
        
        with self.lock:
            transfer = self.transfers[transfer_id]
            
            # Update bytes
            old_bytes = transfer['bytes_transferred']
            transfer['bytes_transferred'] = bytes_transferred
            
            # Calculate progress percentage
            if transfer['file_size'] > 0:
                transfer['progress_percent'] = (bytes_transferred / transfer['file_size']) * 100
            else:
                transfer['progress_percent'] = 0
            
            # Calculate speed (bytes per second)
            elapsed = (datetime.now() - transfer['start_time']).total_seconds()
            if elapsed > 0:
                transfer['speed_bps'] = bytes_transferred / elapsed
                
                # Calculate ETA
                remaining_bytes = transfer['file_size'] - bytes_transferred
                if transfer['speed_bps'] > 0:
                    transfer['eta_seconds'] = remaining_bytes / transfer['speed_bps']
                else:
                    transfer['eta_seconds'] = 0
            
            debug("FileProgress", f"Progress update: {transfer_id[:8]}... - {transfer['progress_percent']:.1f}%")
        
        # Callback
        if self.on_progress_update:
            self.on_progress_update(transfer_id, self.transfers[transfer_id])
    
    def complete_transfer(self, transfer_id: str):
        """
        Mark transfer as complete
        
        Args:
            transfer_id: Transfer ID
        """
        if transfer_id not in self.transfers:
            warning("FileProgress", f"Transfer not found: {transfer_id[:8]}...")
            return
        
        debug("FileProgress", f"Completing transfer: {transfer_id[:8]}...")
        
        with self.lock:
            transfer = self.transfers[transfer_id]
            transfer['status'] = 'completed'
            transfer['progress_percent'] = 100
            transfer['bytes_transferred'] = transfer['file_size']
        
        # Callback
        if self.on_transfer_complete:
            self.on_transfer_complete(transfer_id, self.transfers[transfer_id])
        
        info("FileProgress", f"Transfer completed: {transfer_id[:8]}... - {transfer['file_name']}")
    
    def fail_transfer(self, transfer_id: str, error_message: str = ""):
        """
        Mark transfer as failed
        
        Args:
            transfer_id: Transfer ID
            error_message: Error message
        """
        if transfer_id not in self.transfers:
            warning("FileProgress", f"Transfer not found: {transfer_id[:8]}...")
            return
        
        error("FileProgress", f"Transfer failed: {transfer_id[:8]}... - {error_message}")
        
        with self.lock:
            transfer = self.transfers[transfer_id]
            transfer['status'] = 'failed'
            transfer['error'] = error_message
        
        # Callback
        if self.on_transfer_failed:
            self.on_transfer_failed(transfer_id, self.transfers[transfer_id])
        
        info("FileProgress", f"Transfer marked as failed: {transfer_id[:8]}...")
    
    def cancel_transfer(self, transfer_id: str):
        """
        Cancel a transfer
        
        Args:
            transfer_id: Transfer ID
        """
        if transfer_id not in self.transfers:
            warning("FileProgress", f"Transfer not found: {transfer_id[:8]}...")
            return
        
        debug("FileProgress", f"Cancelling transfer: {transfer_id[:8]}...")
        
        with self.lock:
            transfer = self.transfers[transfer_id]
            transfer['status'] = 'cancelled'
        
        info("FileProgress", f"Transfer cancelled: {transfer_id[:8]}...")
    
    def get_transfer(self, transfer_id: str) -> Optional[Dict]:
        """
        Get transfer data
        
        Args:
            transfer_id: Transfer ID
            
        Returns:
            Transfer data dict or None
        """
        with self.lock:
            return self.transfers.get(transfer_id)
    
    def get_active_transfers(self) -> Dict[str, Dict]:
        """Get all active transfers"""
        with self.lock:
            return {
                tid: data for tid, data in self.transfers.items()
                if data['status'] == 'active'
            }
    
    def get_all_transfers(self) -> Dict[str, Dict]:
        """Get all transfers"""
        with self.lock:
            return self.transfers.copy()
    
    def remove_transfer(self, transfer_id: str):
        """
        Remove transfer from tracking
        
        Args:
            transfer_id: Transfer ID
        """
        debug("FileProgress", f"Removing transfer: {transfer_id[:8]}...")
        
        with self.lock:
            if transfer_id in self.transfers:
                del self.transfers[transfer_id]
                info("FileProgress", f"Transfer removed: {transfer_id[:8]}...")
    
    def clear_completed(self):
        """Clear all completed transfers"""
        debug("FileProgress", "Clearing completed transfers")
        
        with self.lock:
            to_remove = [
                tid for tid, data in self.transfers.items()
                if data['status'] in ['completed', 'failed', 'cancelled']
            ]
            
            for tid in to_remove:
                del self.transfers[tid]
        
        info("FileProgress", f"Cleared {len(to_remove)} completed transfers")
    
    def format_size(self, bytes_size: int) -> str:
        """
        Format bytes to human readable size
        
        Args:
            bytes_size: Size in bytes
            
        Returns:
            Formatted string (e.g., "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} PB"
    
    def format_speed(self, bps: float) -> str:
        """
        Format speed to human readable
        
        Args:
            bps: Bytes per second
            
        Returns:
            Formatted string (e.g., "1.5 MB/s")
        """
        return f"{self.format_size(int(bps))}/s"
    
    def format_time(self, seconds: float) -> str:
        """
        Format seconds to human readable time
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted string (e.g., "2m 30s")
        """
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"

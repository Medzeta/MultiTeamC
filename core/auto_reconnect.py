"""
Auto-Reconnect System
Automatisk återanslutning vid disconnect
"""

import threading
import time
from typing import Dict, Optional, Callable, List
from datetime import datetime
from core.debug_logger import debug, info, warning, error


class AutoReconnect:
    """System för automatisk återanslutning"""
    
    def __init__(self, p2p_system, heartbeat_system=None):
        """
        Initialize auto-reconnect system
        
        Args:
            p2p_system: P2PSystem instance
            heartbeat_system: HeartbeatSystem instance (optional)
        """
        debug("AutoReconnect", "Initializing auto-reconnect system")
        
        self.p2p_system = p2p_system
        self.heartbeat_system = heartbeat_system
        self.running = False
        self.reconnect_thread = None
        
        # Settings
        self.check_interval = 60  # Check every 60 seconds
        self.max_retry_attempts = 5
        self.retry_delay = 10  # Wait 10 seconds between retries
        self.exponential_backoff = True
        
        # Tracking
        self.disconnected_peers: Dict[str, dict] = {}  # peer_id -> {last_seen, retry_count, last_retry}
        self.reconnect_queue: List[str] = []
        
        # Callbacks
        self.on_reconnect_success: Optional[Callable] = None
        self.on_reconnect_failed: Optional[Callable] = None
        self.on_reconnect_attempt: Optional[Callable] = None
        
        info("AutoReconnect", "Auto-reconnect system initialized")
    
    def start(self):
        """Start auto-reconnect system"""
        info("AutoReconnect", "Starting auto-reconnect system")
        
        if self.running:
            warning("AutoReconnect", "Auto-reconnect system already running")
            return
        
        self.running = True
        
        # Start reconnect thread
        self.reconnect_thread = threading.Thread(target=self._reconnect_loop, daemon=True)
        self.reconnect_thread.start()
        
        info("AutoReconnect", "Auto-reconnect system started")
    
    def stop(self):
        """Stop auto-reconnect system"""
        info("AutoReconnect", "Stopping auto-reconnect system")
        
        self.running = False
        
        if self.reconnect_thread:
            self.reconnect_thread.join(timeout=5)
        
        info("AutoReconnect", "Auto-reconnect system stopped")
    
    def _reconnect_loop(self):
        """Main reconnect loop"""
        debug("AutoReconnect", "Starting reconnect loop")
        
        while self.running:
            try:
                # Check for disconnected peers
                self._check_disconnected_peers()
                
                # Process reconnect queue
                self._process_reconnect_queue()
                
                # Wait before next check
                time.sleep(self.check_interval)
                
            except Exception as e:
                error("AutoReconnect", f"Error in reconnect loop: {e}")
                time.sleep(self.check_interval)
    
    def _check_disconnected_peers(self):
        """Check for disconnected peers that need reconnection"""
        debug("AutoReconnect", "Checking for disconnected peers")
        
        if not self.heartbeat_system:
            return
        
        # Get all peer statuses
        statuses = self.heartbeat_system.get_all_statuses()
        
        for peer_id, status in statuses.items():
            if not status['is_alive']:
                # Peer is dead, add to reconnect queue if not already there
                if peer_id not in self.disconnected_peers and peer_id not in self.reconnect_queue:
                    info("AutoReconnect", f"Peer {peer_id[:8]}... disconnected, adding to reconnect queue")
                    
                    self.disconnected_peers[peer_id] = {
                        'last_seen': datetime.now(),
                        'retry_count': 0,
                        'last_retry': None
                    }
                    
                    self.reconnect_queue.append(peer_id)
    
    def _process_reconnect_queue(self):
        """Process reconnect queue"""
        debug("AutoReconnect", f"Processing reconnect queue ({len(self.reconnect_queue)} peers)")
        
        if not self.reconnect_queue:
            return
        
        # Process each peer in queue
        for peer_id in list(self.reconnect_queue):
            if peer_id not in self.disconnected_peers:
                self.reconnect_queue.remove(peer_id)
                continue
            
            peer_info = self.disconnected_peers[peer_id]
            
            # Check if max retries reached
            if peer_info['retry_count'] >= self.max_retry_attempts:
                warning("AutoReconnect", f"Max retry attempts reached for {peer_id[:8]}...")
                
                # Remove from queue and tracking
                self.reconnect_queue.remove(peer_id)
                del self.disconnected_peers[peer_id]
                
                # Callback
                if self.on_reconnect_failed:
                    self.on_reconnect_failed(peer_id, peer_info['retry_count'])
                
                continue
            
            # Check if enough time has passed since last retry
            if peer_info['last_retry']:
                time_since_retry = (datetime.now() - peer_info['last_retry']).total_seconds()
                
                # Calculate delay with exponential backoff
                delay = self.retry_delay
                if self.exponential_backoff:
                    delay = self.retry_delay * (2 ** peer_info['retry_count'])
                
                if time_since_retry < delay:
                    debug("AutoReconnect", f"Too soon to retry {peer_id[:8]}... (waited {time_since_retry:.0f}s, need {delay}s)")
                    continue
            
            # Attempt reconnect
            self._attempt_reconnect(peer_id)
    
    def _attempt_reconnect(self, peer_id: str):
        """
        Attempt to reconnect to peer
        
        Args:
            peer_id: Peer ID
        """
        peer_info = self.disconnected_peers[peer_id]
        peer_info['retry_count'] += 1
        peer_info['last_retry'] = datetime.now()
        
        info("AutoReconnect", f"Attempting reconnect to {peer_id[:8]}... (attempt {peer_info['retry_count']}/{self.max_retry_attempts})")
        
        # Callback
        if self.on_reconnect_attempt:
            self.on_reconnect_attempt(peer_id, peer_info['retry_count'])
        
        try:
            # Try to reconnect
            success = self.p2p_system.connect_to_peer(peer_id)
            
            if success:
                info("AutoReconnect", f"Successfully reconnected to {peer_id[:8]}...")
                
                # Remove from queue and tracking
                self.reconnect_queue.remove(peer_id)
                del self.disconnected_peers[peer_id]
                
                # Add back to heartbeat tracking
                if self.heartbeat_system:
                    self.heartbeat_system.add_peer(peer_id)
                
                # Callback
                if self.on_reconnect_success:
                    self.on_reconnect_success(peer_id, peer_info['retry_count'])
            else:
                warning("AutoReconnect", f"Failed to reconnect to {peer_id[:8]}...")
                
        except Exception as e:
            error("AutoReconnect", f"Error reconnecting to {peer_id[:8]}...: {e}")
    
    def add_peer_to_reconnect(self, peer_id: str):
        """
        Manually add peer to reconnect queue
        
        Args:
            peer_id: Peer ID
        """
        info("AutoReconnect", f"Manually adding {peer_id[:8]}... to reconnect queue")
        
        if peer_id not in self.disconnected_peers:
            self.disconnected_peers[peer_id] = {
                'last_seen': datetime.now(),
                'retry_count': 0,
                'last_retry': None
            }
        
        if peer_id not in self.reconnect_queue:
            self.reconnect_queue.append(peer_id)
    
    def remove_peer_from_reconnect(self, peer_id: str):
        """
        Remove peer from reconnect queue
        
        Args:
            peer_id: Peer ID
        """
        info("AutoReconnect", f"Removing {peer_id[:8]}... from reconnect queue")
        
        if peer_id in self.reconnect_queue:
            self.reconnect_queue.remove(peer_id)
        
        if peer_id in self.disconnected_peers:
            del self.disconnected_peers[peer_id]
    
    def get_reconnect_status(self) -> dict:
        """Get reconnect status"""
        return {
            'queue_size': len(self.reconnect_queue),
            'disconnected_peers': len(self.disconnected_peers),
            'peers': {
                peer_id: {
                    'retry_count': info['retry_count'],
                    'last_retry': info['last_retry'].isoformat() if info['last_retry'] else None,
                    'last_seen': info['last_seen'].isoformat()
                }
                for peer_id, info in self.disconnected_peers.items()
            }
        }
    
    def force_reconnect_now(self, peer_id: str) -> bool:
        """
        Force immediate reconnect attempt
        
        Args:
            peer_id: Peer ID
            
        Returns:
            True if reconnect successful
        """
        info("AutoReconnect", f"Forcing immediate reconnect to {peer_id[:8]}...")
        
        try:
            success = self.p2p_system.connect_to_peer(peer_id)
            
            if success:
                info("AutoReconnect", f"Force reconnect successful: {peer_id[:8]}...")
                
                # Remove from tracking if exists
                if peer_id in self.reconnect_queue:
                    self.reconnect_queue.remove(peer_id)
                if peer_id in self.disconnected_peers:
                    del self.disconnected_peers[peer_id]
                
                return True
            else:
                warning("AutoReconnect", f"Force reconnect failed: {peer_id[:8]}...")
                return False
                
        except Exception as e:
            error("AutoReconnect", f"Error in force reconnect: {e}")
            return False

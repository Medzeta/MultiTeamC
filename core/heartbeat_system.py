"""
Heartbeat System
Håller P2P-anslutningar vid liv och detekterar disconnects
"""

import threading
import time
from typing import Dict, Optional, Callable
from datetime import datetime, timedelta
from core.debug_logger import debug, info, warning, error


class HeartbeatSystem:
    """System för heartbeat mellan peers"""
    
    def __init__(self, p2p_system):
        """
        Initialize heartbeat system
        
        Args:
            p2p_system: P2PSystem instance
        """
        debug("HeartbeatSystem", "Initializing heartbeat system")
        
        self.p2p_system = p2p_system
        self.running = False
        self.heartbeat_thread = None
        
        # Settings
        self.heartbeat_interval = 30  # Send heartbeat every 30 seconds
        self.timeout_threshold = 90  # Consider dead after 90 seconds
        
        # Peer heartbeat tracking
        self.last_heartbeat: Dict[str, datetime] = {}  # peer_id -> last heartbeat time
        self.missed_heartbeats: Dict[str, int] = {}  # peer_id -> missed count
        
        # Callbacks
        self.on_peer_timeout: Optional[Callable] = None
        self.on_peer_alive: Optional[Callable] = None
        
        info("HeartbeatSystem", "Heartbeat system initialized")
    
    def start(self):
        """Start heartbeat system"""
        info("HeartbeatSystem", "Starting heartbeat system")
        
        if self.running:
            warning("HeartbeatSystem", "Heartbeat system already running")
            return
        
        self.running = True
        
        # Start heartbeat thread
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
        
        info("HeartbeatSystem", "Heartbeat system started")
    
    def stop(self):
        """Stop heartbeat system"""
        info("HeartbeatSystem", "Stopping heartbeat system")
        
        self.running = False
        
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=5)
        
        info("HeartbeatSystem", "Heartbeat system stopped")
    
    def _heartbeat_loop(self):
        """Main heartbeat loop"""
        debug("HeartbeatSystem", "Starting heartbeat loop")
        
        while self.running:
            try:
                # Send heartbeats to all connected peers
                self._send_heartbeats()
                
                # Check for timeouts
                self._check_timeouts()
                
                # Wait before next heartbeat
                time.sleep(self.heartbeat_interval)
                
            except Exception as e:
                error("HeartbeatSystem", f"Error in heartbeat loop: {e}")
                time.sleep(self.heartbeat_interval)
    
    def _send_heartbeats(self):
        """Send heartbeat to all connected peers"""
        debug("HeartbeatSystem", "Sending heartbeats")
        
        peers = self.p2p_system.get_connected_peers()
        
        for peer in peers:
            peer_id = peer['id']
            
            try:
                # Send heartbeat message
                success = self.p2p_system.send_message(
                    peer_id,
                    {
                        'type': 'heartbeat',
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
                if success:
                    debug("HeartbeatSystem", f"Heartbeat sent to {peer_id[:8]}...")
                else:
                    # Increment missed count
                    self.missed_heartbeats[peer_id] = self.missed_heartbeats.get(peer_id, 0) + 1
                    warning("HeartbeatSystem", f"Failed to send heartbeat to {peer_id[:8]}...")
                    
            except Exception as e:
                error("HeartbeatSystem", f"Error sending heartbeat to {peer_id[:8]}...: {e}")
                self.missed_heartbeats[peer_id] = self.missed_heartbeats.get(peer_id, 0) + 1
    
    def _check_timeouts(self):
        """Check for peer timeouts"""
        debug("HeartbeatSystem", "Checking for timeouts")
        
        now = datetime.now()
        timeout_threshold = timedelta(seconds=self.timeout_threshold)
        
        for peer_id, last_time in list(self.last_heartbeat.items()):
            time_since_last = now - last_time
            
            if time_since_last > timeout_threshold:
                warning("HeartbeatSystem", f"Peer {peer_id[:8]}... timed out")
                
                # Remove from tracking
                del self.last_heartbeat[peer_id]
                if peer_id in self.missed_heartbeats:
                    del self.missed_heartbeats[peer_id]
                
                # Callback
                if self.on_peer_timeout:
                    self.on_peer_timeout(peer_id)
    
    def record_heartbeat(self, peer_id: str):
        """
        Record heartbeat from peer
        
        Args:
            peer_id: Peer ID
        """
        debug("HeartbeatSystem", f"Recording heartbeat from {peer_id[:8]}...")
        
        # Update last heartbeat time
        self.last_heartbeat[peer_id] = datetime.now()
        
        # Reset missed count
        if peer_id in self.missed_heartbeats:
            del self.missed_heartbeats[peer_id]
        
        # Callback
        if self.on_peer_alive:
            self.on_peer_alive(peer_id)
    
    def get_peer_status(self, peer_id: str) -> dict:
        """
        Get peer heartbeat status
        
        Args:
            peer_id: Peer ID
            
        Returns:
            Status dict with last_heartbeat, missed_count, is_alive
        """
        last_heartbeat = self.last_heartbeat.get(peer_id)
        missed_count = self.missed_heartbeats.get(peer_id, 0)
        
        is_alive = False
        if last_heartbeat:
            time_since = datetime.now() - last_heartbeat
            is_alive = time_since.total_seconds() < self.timeout_threshold
        
        return {
            'last_heartbeat': last_heartbeat.isoformat() if last_heartbeat else None,
            'missed_count': missed_count,
            'is_alive': is_alive,
            'seconds_since_last': (datetime.now() - last_heartbeat).total_seconds() if last_heartbeat else None
        }
    
    def get_all_statuses(self) -> Dict[str, dict]:
        """Get heartbeat status for all tracked peers"""
        debug("HeartbeatSystem", "Getting all peer statuses")
        
        statuses = {}
        for peer_id in self.last_heartbeat.keys():
            statuses[peer_id] = self.get_peer_status(peer_id)
        
        return statuses
    
    def is_peer_alive(self, peer_id: str) -> bool:
        """
        Check if peer is alive
        
        Args:
            peer_id: Peer ID
            
        Returns:
            True if peer is alive
        """
        status = self.get_peer_status(peer_id)
        return status['is_alive']
    
    def add_peer(self, peer_id: str):
        """
        Add peer to heartbeat tracking
        
        Args:
            peer_id: Peer ID
        """
        debug("HeartbeatSystem", f"Adding peer to tracking: {peer_id[:8]}...")
        
        self.last_heartbeat[peer_id] = datetime.now()
        self.missed_heartbeats[peer_id] = 0
        
        info("HeartbeatSystem", f"Peer added to tracking: {peer_id[:8]}...")
    
    def remove_peer(self, peer_id: str):
        """
        Remove peer from heartbeat tracking
        
        Args:
            peer_id: Peer ID
        """
        debug("HeartbeatSystem", f"Removing peer from tracking: {peer_id[:8]}...")
        
        if peer_id in self.last_heartbeat:
            del self.last_heartbeat[peer_id]
        
        if peer_id in self.missed_heartbeats:
            del self.missed_heartbeats[peer_id]
        
        info("HeartbeatSystem", f"Peer removed from tracking: {peer_id[:8]}...")

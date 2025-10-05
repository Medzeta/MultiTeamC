"""
Presence System
Tracking av online/offline status för team members
"""

import threading
import time
from typing import Dict, Optional, Callable, Set, List
from datetime import datetime, timedelta
from core.debug_logger import debug, info, warning, error


class PresenceSystem:
    """System för presence tracking"""
    
    def __init__(self, p2p_system):
        """
        Initialize presence system
        
        Args:
            p2p_system: P2PSystem instance
        """
        debug("PresenceSystem", "Initializing presence system")
        
        self.p2p_system = p2p_system
        self.running = False
        self.broadcast_thread = None
        self.cleanup_thread = None
        
        # Settings
        self.broadcast_interval = 30  # Broadcast presence every 30 seconds
        self.offline_threshold = 90  # Consider offline after 90 seconds
        
        # Tracking
        self.online_users: Dict[str, datetime] = {}  # user_id -> last_seen
        self.user_info: Dict[str, Dict] = {}  # user_id -> {username, status, etc}
        
        # Callbacks
        self.on_user_online: Optional[Callable] = None
        self.on_user_offline: Optional[Callable] = None
        self.on_status_changed: Optional[Callable] = None
        
        info("PresenceSystem", "Presence system initialized")
    
    def start(self):
        """Start presence system"""
        info("PresenceSystem", "Starting presence system")
        
        if self.running:
            warning("PresenceSystem", "Presence system already running")
            return
        
        self.running = True
        
        # Start broadcast thread
        self.broadcast_thread = threading.Thread(target=self._broadcast_loop, daemon=True)
        self.broadcast_thread.start()
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        
        info("PresenceSystem", "Presence system started")
    
    def stop(self):
        """Stop presence system"""
        info("PresenceSystem", "Stopping presence system")
        
        self.running = False
        
        if self.broadcast_thread:
            self.broadcast_thread.join(timeout=5)
        
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
        
        info("PresenceSystem", "Presence system stopped")
    
    def _broadcast_loop(self):
        """Broadcast presence to all peers"""
        debug("PresenceSystem", "Starting broadcast loop")
        
        while self.running:
            try:
                self._broadcast_presence()
                time.sleep(self.broadcast_interval)
                
            except Exception as e:
                error("PresenceSystem", f"Error in broadcast loop: {e}")
                time.sleep(self.broadcast_interval)
    
    def _cleanup_loop(self):
        """Cleanup offline users"""
        debug("PresenceSystem", "Starting cleanup loop")
        
        while self.running:
            try:
                self._cleanup_offline_users()
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                error("PresenceSystem", f"Error in cleanup loop: {e}")
                time.sleep(10)
    
    def _broadcast_presence(self):
        """Broadcast presence to all connected peers"""
        debug("PresenceSystem", "Broadcasting presence")
        
        message = {
            'type': 'presence',
            'status': 'online',
            'timestamp': datetime.now().isoformat()
        }
        
        peers = self.p2p_system.get_connected_peers()
        
        for peer in peers:
            try:
                self.p2p_system.send_message(peer['id'], message)
                debug("PresenceSystem", f"Sent presence to peer {peer['id'][:8]}...")
            except Exception as e:
                error("PresenceSystem", f"Error sending presence to peer: {e}")
        
        info("PresenceSystem", f"Presence broadcasted to {len(peers)} peers")
    
    def _cleanup_offline_users(self):
        """Remove users that have been offline too long"""
        now = datetime.now()
        threshold = timedelta(seconds=self.offline_threshold)
        
        for user_id, last_seen in list(self.online_users.items()):
            if now - last_seen > threshold:
                debug("PresenceSystem", f"User {user_id[:8]}... went offline")
                
                # Remove from online users
                del self.online_users[user_id]
                
                # Callback
                if self.on_user_offline:
                    user_info = self.user_info.get(user_id, {})
                    self.on_user_offline(user_id, user_info)
                
                info("PresenceSystem", f"User {user_id[:8]}... marked as offline")
    
    def update_presence(self, user_id: str, username: str, status: str = 'online'):
        """
        Update user presence
        
        Args:
            user_id: User ID
            username: Username
            status: Status (online, away, busy, offline)
        """
        debug("PresenceSystem", f"Updating presence: {username} ({user_id[:8]}...) - {status}")
        
        was_online = user_id in self.online_users
        
        # Update last seen
        self.online_users[user_id] = datetime.now()
        
        # Update user info
        self.user_info[user_id] = {
            'username': username,
            'status': status,
            'last_seen': datetime.now().isoformat()
        }
        
        # Callback if user just came online
        if not was_online and status == 'online':
            if self.on_user_online:
                self.on_user_online(user_id, self.user_info[user_id])
            info("PresenceSystem", f"User {username} came online")
        
        # Callback for status change
        if self.on_status_changed:
            self.on_status_changed(user_id, status)
    
    def is_online(self, user_id: str) -> bool:
        """
        Check if user is online
        
        Args:
            user_id: User ID
            
        Returns:
            True if user is online
        """
        if user_id not in self.online_users:
            return False
        
        last_seen = self.online_users[user_id]
        threshold = timedelta(seconds=self.offline_threshold)
        
        return datetime.now() - last_seen < threshold
    
    def get_online_users(self) -> List[Dict]:
        """Get list of online users"""
        online = []
        
        for user_id in list(self.online_users.keys()):
            if self.is_online(user_id):
                user_data = self.user_info.get(user_id, {})
                user_data['user_id'] = user_id
                online.append(user_data)
        
        debug("PresenceSystem", f"Found {len(online)} online users")
        return online
    
    def get_user_status(self, user_id: str) -> str:
        """
        Get user status
        
        Args:
            user_id: User ID
            
        Returns:
            Status string (online, offline, away, busy)
        """
        if not self.is_online(user_id):
            return 'offline'
        
        user_info = self.user_info.get(user_id, {})
        return user_info.get('status', 'online')
    
    def get_last_seen(self, user_id: str) -> Optional[str]:
        """
        Get last seen timestamp for user
        
        Args:
            user_id: User ID
            
        Returns:
            ISO format timestamp or None
        """
        if user_id not in self.online_users:
            return None
        
        return self.online_users[user_id].isoformat()

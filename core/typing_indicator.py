"""
Typing Indicator System
Visar när användare skriver i team chat
"""

import threading
import time
from typing import Dict, Optional, Callable
from datetime import datetime, timedelta
from core.debug_logger import debug, info, warning, error


class TypingIndicator:
    """System för typing indicators"""
    
    def __init__(self, p2p_system):
        """
        Initialize typing indicator system
        
        Args:
            p2p_system: P2PSystem instance
        """
        debug("TypingIndicator", "Initializing typing indicator system")
        
        self.p2p_system = p2p_system
        self.running = False
        self.cleanup_thread = None
        
        # Settings
        self.typing_timeout = 3  # Seconds before "typing" disappears
        self.send_interval = 2  # Send typing indicator every 2 seconds while typing
        
        # Tracking
        self.typing_users: Dict[str, Dict[str, datetime]] = {}  # team_id -> {user_id: last_typing_time}
        self.last_sent: Dict[str, datetime] = {}  # team_id -> last time we sent typing indicator
        
        # Callbacks
        self.on_typing_started: Optional[Callable] = None
        self.on_typing_stopped: Optional[Callable] = None
        
        info("TypingIndicator", "Typing indicator system initialized")
    
    def start(self):
        """Start typing indicator system"""
        info("TypingIndicator", "Starting typing indicator system")
        
        if self.running:
            warning("TypingIndicator", "Typing indicator system already running")
            return
        
        self.running = True
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        
        info("TypingIndicator", "Typing indicator system started")
    
    def stop(self):
        """Stop typing indicator system"""
        info("TypingIndicator", "Stopping typing indicator system")
        
        self.running = False
        
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
        
        info("TypingIndicator", "Typing indicator system stopped")
    
    def _cleanup_loop(self):
        """Cleanup loop to remove old typing indicators"""
        debug("TypingIndicator", "Starting cleanup loop")
        
        while self.running:
            try:
                self._cleanup_old_indicators()
                time.sleep(1)  # Check every second
                
            except Exception as e:
                error("TypingIndicator", f"Error in cleanup loop: {e}")
                time.sleep(1)
    
    def _cleanup_old_indicators(self):
        """Remove typing indicators that have timed out"""
        now = datetime.now()
        timeout = timedelta(seconds=self.typing_timeout)
        
        for team_id, users in list(self.typing_users.items()):
            for user_id, last_time in list(users.items()):
                if now - last_time > timeout:
                    debug("TypingIndicator", f"Removing timed out typing indicator: {user_id[:8]}... in team {team_id[:8]}...")
                    
                    del self.typing_users[team_id][user_id]
                    
                    # Callback
                    if self.on_typing_stopped:
                        self.on_typing_stopped(team_id, user_id)
                    
                    # Remove team if no users typing
                    if not self.typing_users[team_id]:
                        del self.typing_users[team_id]
    
    def send_typing(self, team_id: str, user_id: str, username: str):
        """
        Send typing indicator to team
        
        Args:
            team_id: Team ID
            user_id: User ID
            username: Username
        """
        now = datetime.now()
        
        # Check if we should send (throttle to avoid spam)
        if team_id in self.last_sent:
            time_since_last = (now - self.last_sent[team_id]).total_seconds()
            if time_since_last < self.send_interval:
                debug("TypingIndicator", f"Throttling typing indicator for team {team_id[:8]}...")
                return
        
        debug("TypingIndicator", f"Sending typing indicator: {username} in team {team_id[:8]}...")
        
        # Send to all team members via P2P
        message = {
            'type': 'typing_indicator',
            'team_id': team_id,
            'user_id': user_id,
            'username': username,
            'timestamp': now.isoformat()
        }
        
        # Broadcast to all peers
        peers = self.p2p_system.get_connected_peers()
        for peer in peers:
            try:
                self.p2p_system.send_message(peer['id'], message)
                debug("TypingIndicator", f"Sent typing indicator to peer {peer['id'][:8]}...")
            except Exception as e:
                error("TypingIndicator", f"Error sending typing indicator to peer: {e}")
        
        # Update last sent time
        self.last_sent[team_id] = now
        
        info("TypingIndicator", f"Typing indicator sent: {username} in team {team_id[:8]}...")
    
    def receive_typing(self, team_id: str, user_id: str, username: str):
        """
        Receive typing indicator from another user
        
        Args:
            team_id: Team ID
            user_id: User ID
            username: Username
        """
        debug("TypingIndicator", f"Received typing indicator: {username} ({user_id[:8]}...) in team {team_id[:8]}...")
        
        # Initialize team if not exists
        if team_id not in self.typing_users:
            self.typing_users[team_id] = {}
        
        # Check if this is a new typing user
        is_new = user_id not in self.typing_users[team_id]
        
        # Update typing time
        self.typing_users[team_id][user_id] = datetime.now()
        
        # Callback if new
        if is_new and self.on_typing_started:
            self.on_typing_started(team_id, user_id, username)
            info("TypingIndicator", f"User started typing: {username} in team {team_id[:8]}...")
    
    def stop_typing(self, team_id: str, user_id: str):
        """
        Stop typing indicator for user
        
        Args:
            team_id: Team ID
            user_id: User ID
        """
        debug("TypingIndicator", f"Stopping typing indicator: {user_id[:8]}... in team {team_id[:8]}...")
        
        if team_id in self.typing_users and user_id in self.typing_users[team_id]:
            del self.typing_users[team_id][user_id]
            
            # Callback
            if self.on_typing_stopped:
                self.on_typing_stopped(team_id, user_id)
            
            # Remove team if no users typing
            if not self.typing_users[team_id]:
                del self.typing_users[team_id]
            
            info("TypingIndicator", f"User stopped typing: {user_id[:8]}... in team {team_id[:8]}...")
    
    def get_typing_users(self, team_id: str) -> list:
        """
        Get list of users currently typing in team
        
        Args:
            team_id: Team ID
            
        Returns:
            List of user IDs currently typing
        """
        if team_id not in self.typing_users:
            return []
        
        return list(self.typing_users[team_id].keys())
    
    def is_typing(self, team_id: str, user_id: str) -> bool:
        """
        Check if user is typing in team
        
        Args:
            team_id: Team ID
            user_id: User ID
            
        Returns:
            True if user is typing
        """
        if team_id not in self.typing_users:
            return False
        
        return user_id in self.typing_users[team_id]
    
    def get_typing_status(self, team_id: str) -> dict:
        """
        Get typing status for team
        
        Args:
            team_id: Team ID
            
        Returns:
            Dict with typing users and their info
        """
        if team_id not in self.typing_users:
            return {'count': 0, 'users': []}
        
        users = []
        for user_id, last_time in self.typing_users[team_id].items():
            users.append({
                'user_id': user_id,
                'last_typing': last_time.isoformat(),
                'seconds_ago': (datetime.now() - last_time).total_seconds()
            })
        
        return {
            'count': len(users),
            'users': users
        }

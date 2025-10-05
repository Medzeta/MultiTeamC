"""
Session Manager
Hantering av session timeout och inaktivitet
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Callable
from core.debug_logger import debug, info, warning, error
from core.remember_me import RememberMe


class SessionManager:
    """System för session timeout management"""
    
    def __init__(self, timeout_minutes: int = 30):
        """
        Initialize session manager
        
        Args:
            timeout_minutes: Minutes of inactivity before timeout (default: 30)
        """
        debug("SessionManager", "Initializing session manager")
        
        self.timeout_minutes = timeout_minutes
        self.timeout_seconds = timeout_minutes * 60
        
        self.last_activity = datetime.now()
        self.is_active = False
        self.monitor_thread = None
        
        self.remember_me = RememberMe()
        
        # Callbacks
        self.on_timeout: Optional[Callable] = None
        self.on_warning: Optional[Callable] = None  # Called 5 min before timeout
        
        info("SessionManager", f"Session manager initialized (timeout: {timeout_minutes} min)")
    
    def start(self):
        """Start session monitoring"""
        info("SessionManager", "Starting session monitoring")
        
        if self.is_active:
            warning("SessionManager", "Session monitoring already active")
            return
        
        self.is_active = True
        self.last_activity = datetime.now()
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        info("SessionManager", "Session monitoring started")
    
    def stop(self):
        """Stop session monitoring"""
        info("SessionManager", "Stopping session monitoring")
        
        self.is_active = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        
        info("SessionManager", "Session monitoring stopped")
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
        debug("SessionManager", f"Activity updated: {self.last_activity.strftime('%H:%M:%S')}")
    
    def get_time_until_timeout(self) -> int:
        """
        Get seconds until timeout
        
        Returns:
            Seconds until timeout
        """
        elapsed = (datetime.now() - self.last_activity).total_seconds()
        remaining = self.timeout_seconds - elapsed
        return max(0, int(remaining))
    
    def get_inactive_time(self) -> int:
        """
        Get seconds of inactivity
        
        Returns:
            Seconds since last activity
        """
        elapsed = (datetime.now() - self.last_activity).total_seconds()
        return int(elapsed)
    
    def is_timeout_imminent(self) -> bool:
        """
        Check if timeout is imminent (within 5 minutes)
        
        Returns:
            True if timeout is within 5 minutes
        """
        remaining = self.get_time_until_timeout()
        return remaining <= 300  # 5 minutes
    
    def extend_session(self):
        """Extend session by resetting activity"""
        info("SessionManager", "Session extended by user")
        self.update_activity()
    
    def _monitor_loop(self):
        """Monitor session activity"""
        debug("SessionManager", "Session monitor loop started")
        
        warning_sent = False
        
        while self.is_active:
            try:
                # Check inactivity
                inactive_seconds = self.get_inactive_time()
                remaining_seconds = self.get_time_until_timeout()
                
                # Debug log every minute
                if inactive_seconds % 60 == 0 and inactive_seconds > 0:
                    debug("SessionManager", 
                          f"Inactive: {inactive_seconds//60} min, "
                          f"Remaining: {remaining_seconds//60} min")
                
                # Warning at 5 minutes before timeout
                if remaining_seconds <= 300 and remaining_seconds > 0 and not warning_sent:
                    warning("SessionManager", "Session timeout warning (5 min remaining)")
                    warning_sent = True
                    
                    if self.on_warning:
                        self.on_warning(remaining_seconds)
                
                # Timeout reached
                if remaining_seconds <= 0:
                    error("SessionManager", "Session timeout reached")
                    self.is_active = False
                    
                    # Clear remember me session if exists
                    self.remember_me.clear_session()
                    
                    if self.on_timeout:
                        self.on_timeout()
                    
                    break
                
                # Reset warning flag if activity resumed
                if remaining_seconds > 300:
                    warning_sent = False
                
                # Sleep for 1 second
                time.sleep(1)
                
            except Exception as e:
                error("SessionManager", f"Error in monitor loop: {e}")
                time.sleep(5)
        
        debug("SessionManager", "Session monitor loop ended")
    
    def get_status(self) -> dict:
        """
        Get session status
        
        Returns:
            Dict with session info
        """
        return {
            'is_active': self.is_active,
            'last_activity': self.last_activity.isoformat(),
            'inactive_seconds': self.get_inactive_time(),
            'remaining_seconds': self.get_time_until_timeout(),
            'timeout_minutes': self.timeout_minutes,
            'is_imminent': self.is_timeout_imminent()
        }
    
    def format_time_remaining(self) -> str:
        """
        Format remaining time as human-readable string
        
        Returns:
            Formatted time string
        """
        seconds = self.get_time_until_timeout()
        
        if seconds <= 0:
            return "Expired"
        
        minutes = seconds // 60
        secs = seconds % 60
        
        if minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"


class ActivityTracker:
    """Helper class to track user activity"""
    
    def __init__(self, session_manager: SessionManager):
        """
        Initialize activity tracker
        
        Args:
            session_manager: SessionManager instance
        """
        debug("ActivityTracker", "Initializing activity tracker")
        
        self.session_manager = session_manager
        self.tracking_enabled = True
        
        info("ActivityTracker", "Activity tracker initialized")
    
    def track_mouse_activity(self, event):
        """Track mouse activity"""
        if self.tracking_enabled:
            self.session_manager.update_activity()
    
    def track_keyboard_activity(self, event):
        """Track keyboard activity"""
        if self.tracking_enabled:
            self.session_manager.update_activity()
    
    def track_click_activity(self, event):
        """Track click activity"""
        if self.tracking_enabled:
            self.session_manager.update_activity()
    
    def enable_tracking(self):
        """Enable activity tracking"""
        debug("ActivityTracker", "Activity tracking enabled")
        self.tracking_enabled = True
    
    def disable_tracking(self):
        """Disable activity tracking"""
        debug("ActivityTracker", "Activity tracking disabled")
        self.tracking_enabled = False
    
    def bind_to_widget(self, widget):
        """
        Bind activity tracking to widget
        
        Args:
            widget: Tkinter widget to bind to
        """
        debug("ActivityTracker", f"Binding activity tracking to widget: {widget}")
        
        # Mouse events
        widget.bind('<Motion>', self.track_mouse_activity, add='+')
        widget.bind('<Button-1>', self.track_click_activity, add='+')
        widget.bind('<Button-2>', self.track_click_activity, add='+')
        widget.bind('<Button-3>', self.track_click_activity, add='+')
        
        # Keyboard events
        widget.bind('<Key>', self.track_keyboard_activity, add='+')
        
        info("ActivityTracker", "Activity tracking bound to widget")
    
    def bind_to_window(self, window):
        """
        Bind activity tracking to entire window
        
        Args:
            window: Tkinter window to bind to
        """
        debug("ActivityTracker", "Binding activity tracking to window")
        
        self.bind_to_widget(window)
        
        # Also bind to all children recursively
        for child in window.winfo_children():
            try:
                self.bind_to_widget(child)
            except Exception as e:
                debug("ActivityTracker", f"Could not bind to child widget: {e}")
        
        info("ActivityTracker", "Activity tracking bound to window and children")

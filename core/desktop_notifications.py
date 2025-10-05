"""
Desktop Notifications System
Windows Toast notifications för viktiga händelser
"""

import platform
from typing import Optional
from core.debug_logger import debug, info, warning, error, exception

# Try to import Windows toast notifications
try:
    from win10toast import ToastNotifier
    TOAST_AVAILABLE = True
except ImportError:
    TOAST_AVAILABLE = False
    warning("DesktopNotifications", "win10toast not available - install with: pip install win10toast")


class DesktopNotifications:
    """System för Windows desktop notifications"""
    
    def __init__(self):
        """Initialize desktop notifications"""
        debug("DesktopNotifications", "Initializing desktop notifications")
        
        self.enabled = True
        self.toaster = None
        
        # Check if we're on Windows
        if platform.system() != "Windows":
            warning("DesktopNotifications", "Desktop notifications only supported on Windows")
            self.enabled = False
        elif not TOAST_AVAILABLE:
            warning("DesktopNotifications", "win10toast not installed")
            self.enabled = False
        else:
            try:
                self.toaster = ToastNotifier()
                info("DesktopNotifications", "Desktop notifications initialized")
            except Exception as e:
                exception("DesktopNotifications", f"Failed to initialize toaster: {e}")
                self.enabled = False
    
    def show_notification(
        self,
        title: str,
        message: str,
        duration: int = 5,
        icon_path: Optional[str] = None,
        threaded: bool = True
    ) -> bool:
        """
        Show desktop notification
        
        Args:
            title: Notification title
            message: Notification message
            duration: Duration in seconds (default: 5)
            icon_path: Path to icon file (optional)
            threaded: Run in separate thread (default: True)
            
        Returns:
            True if notification shown successfully
        """
        if not self.enabled or not self.toaster:
            debug("DesktopNotifications", "Notifications disabled or not available")
            return False
        
        debug("DesktopNotifications", f"Showing notification: {title}")
        
        try:
            self.toaster.show_toast(
                title=title,
                msg=message,
                duration=duration,
                icon_path=icon_path,
                threaded=threaded
            )
            info("DesktopNotifications", f"Notification shown: {title}")
            return True
            
        except Exception as e:
            exception("DesktopNotifications", f"Error showing notification: {e}")
            return False
    
    def show_message(self, sender: str, message: str) -> bool:
        """
        Show new message notification
        
        Args:
            sender: Message sender name
            message: Message preview
            
        Returns:
            True if successful
        """
        return self.show_notification(
            title=f"New message from {sender}",
            message=message[:100] + "..." if len(message) > 100 else message,
            duration=5
        )
    
    def show_file_received(self, sender: str, filename: str) -> bool:
        """
        Show file received notification
        
        Args:
            sender: File sender name
            filename: File name
            
        Returns:
            True if successful
        """
        return self.show_notification(
            title=f"File received from {sender}",
            message=f"📁 {filename}",
            duration=5
        )
    
    def show_team_invite(self, team_name: str, inviter: str) -> bool:
        """
        Show team invitation notification
        
        Args:
            team_name: Team name
            inviter: Inviter name
            
        Returns:
            True if successful
        """
        return self.show_notification(
            title="Team Invitation",
            message=f"{inviter} invited you to join {team_name}",
            duration=7
        )
    
    def show_peer_online(self, peer_name: str) -> bool:
        """
        Show peer online notification
        
        Args:
            peer_name: Peer name
            
        Returns:
            True if successful
        """
        return self.show_notification(
            title="Peer Online",
            message=f"🟢 {peer_name} is now online",
            duration=3
        )
    
    def show_system_message(self, title: str, message: str) -> bool:
        """
        Show system message notification
        
        Args:
            title: Notification title
            message: System message
            
        Returns:
            True if successful
        """
        return self.show_notification(
            title=f"MultiTeam - {title}",
            message=message,
            duration=5
        )
    
    def enable(self):
        """Enable desktop notifications"""
        debug("DesktopNotifications", "Enabling desktop notifications")
        self.enabled = True
    
    def disable(self):
        """Disable desktop notifications"""
        debug("DesktopNotifications", "Disabling desktop notifications")
        self.enabled = False
    
    def is_available(self) -> bool:
        """
        Check if desktop notifications are available
        
        Returns:
            True if available
        """
        return self.enabled and self.toaster is not None

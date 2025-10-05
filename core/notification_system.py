"""
Notification System
Toast notifications för events i appen
"""

import customtkinter as ctk
from typing import Literal, Optional, Callable
from datetime import datetime
import threading
from core.debug_logger import debug, info, warning, error


class ToastNotification(ctk.CTkFrame):
    """Toast notification widget"""
    
    def __init__(
        self,
        parent,
        message: str,
        notification_type: Literal["info", "success", "warning", "error"] = "info",
        duration: int = 3000,
        on_click: Optional[Callable] = None,
        **kwargs
    ):
        """
        Initialize toast notification
        
        Args:
            parent: Parent widget
            message: Notification message
            notification_type: Type of notification (info, success, warning, error)
            duration: Duration in milliseconds (0 = permanent)
            on_click: Optional callback when clicked
        """
        debug("ToastNotification", f"Creating notification: {notification_type} - {message}")
        
        super().__init__(
            parent,
            fg_color=self._get_color(notification_type),
            corner_radius=8,
            **kwargs
        )
        
        self.message = message
        self.notification_type = notification_type
        self.duration = duration
        self.on_click_callback = on_click
        self._fade_timer = None
        
        self._create_ui()
        
        # Auto-hide after duration
        if duration > 0:
            self.after(duration, self._start_fade_out)
        
        info("ToastNotification", f"Notification created: {message}")
    
    def _get_color(self, notification_type: str) -> tuple:
        """Get color based on notification type"""
        colors = {
            "info": ("#2b5797", "#1e3a5f"),
            "success": ("#107c10", "#0d5e0d"),
            "warning": ("#f7630c", "#d15a0a"),
            "error": ("#c42b1c", "#a52318")
        }
        return colors.get(notification_type, colors["info"])
    
    def _get_icon(self, notification_type: str) -> str:
        """Get icon based on notification type"""
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        return icons.get(notification_type, icons["info"])
    
    def _create_ui(self):
        """Create notification UI"""
        debug("ToastNotification", "Creating notification UI")
        
        # Make clickable
        self.bind("<Button-1>", self._on_click)
        
        # Content container
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=10)
        content.bind("<Button-1>", self._on_click)
        
        # Icon
        icon_label = ctk.CTkLabel(
            content,
            text=self._get_icon(self.notification_type),
            font=("Segoe UI", 16),
            text_color=("#ffffff", "#ffffff")
        )
        icon_label.pack(side="left", padx=(0, 10))
        icon_label.bind("<Button-1>", self._on_click)
        
        # Message
        message_label = ctk.CTkLabel(
            content,
            text=self.message,
            font=("Segoe UI", 11),
            text_color=("#ffffff", "#ffffff"),
            wraplength=300,
            justify="left"
        )
        message_label.pack(side="left", fill="x", expand=True)
        message_label.bind("<Button-1>", self._on_click)
        
        # Close button
        close_btn = ctk.CTkLabel(
            content,
            text="✕",
            font=("Segoe UI", 14, "bold"),
            text_color=("#ffffff", "#ffffff"),
            cursor="hand2"
        )
        close_btn.pack(side="right", padx=(10, 0))
        close_btn.bind("<Button-1>", lambda e: self._close())
        
        debug("ToastNotification", "Notification UI created")
    
    def _on_click(self, event=None):
        """Handle notification click"""
        debug("ToastNotification", "Notification clicked")
        
        if self.on_click_callback:
            self.on_click_callback()
        
        self._close()
    
    def _start_fade_out(self):
        """Start fade out animation"""
        debug("ToastNotification", "Starting fade out")
        self._close()
    
    def _close(self):
        """Close notification"""
        debug("ToastNotification", "Closing notification")
        
        if self._fade_timer:
            self.after_cancel(self._fade_timer)
        
        self.destroy()
        info("ToastNotification", "Notification closed")


class NotificationSystem:
    """Centralized notification system"""
    
    def __init__(self, root_window):
        """
        Initialize notification system
        
        Args:
            root_window: Root window to attach notifications to
        """
        debug("NotificationSystem", "Initializing notification system")
        
        self.root_window = root_window
        self.notifications = []
        self.max_notifications = 5
        self.notification_spacing = 10
        
        # Create notification container
        self.container = ctk.CTkFrame(
            root_window,
            fg_color="transparent"
        )
        self.container.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)
        
        info("NotificationSystem", "Notification system initialized")
    
    def show(
        self,
        message: str,
        notification_type: Literal["info", "success", "warning", "error"] = "info",
        duration: int = 3000,
        on_click: Optional[Callable] = None
    ):
        """
        Show a notification
        
        Args:
            message: Notification message
            notification_type: Type of notification
            duration: Duration in milliseconds (0 = permanent)
            on_click: Optional callback when clicked
        """
        info("NotificationSystem", f"Showing notification: {notification_type} - {message}")
        
        # Remove oldest if at max
        if len(self.notifications) >= self.max_notifications:
            oldest = self.notifications.pop(0)
            oldest.destroy()
            debug("NotificationSystem", "Removed oldest notification")
        
        # Create notification
        notification = ToastNotification(
            self.container,
            message=message,
            notification_type=notification_type,
            duration=duration,
            on_click=on_click
        )
        
        # Add to list
        self.notifications.append(notification)
        
        # Position notification
        self._reposition_notifications()
        
        # Remove from list when destroyed
        def on_destroy():
            if notification in self.notifications:
                self.notifications.remove(notification)
                self._reposition_notifications()
        
        notification.bind("<Destroy>", lambda e: on_destroy())
        
        debug("NotificationSystem", f"Notification shown, total: {len(self.notifications)}")
    
    def _reposition_notifications(self):
        """Reposition all notifications"""
        debug("NotificationSystem", f"Repositioning {len(self.notifications)} notifications")
        
        y_offset = 0
        for notification in reversed(self.notifications):
            notification.pack(side="bottom", anchor="e", pady=(0, self.notification_spacing))
            y_offset += notification.winfo_reqheight() + self.notification_spacing
    
    def show_info(self, message: str, duration: int = 3000, on_click: Optional[Callable] = None):
        """Show info notification"""
        self.show(message, "info", duration, on_click)
    
    def show_success(self, message: str, duration: int = 3000, on_click: Optional[Callable] = None):
        """Show success notification"""
        self.show(message, "success", duration, on_click)
    
    def show_warning(self, message: str, duration: int = 3000, on_click: Optional[Callable] = None):
        """Show warning notification"""
        self.show(message, "warning", duration, on_click)
    
    def show_error(self, message: str, duration: int = 5000, on_click: Optional[Callable] = None):
        """Show error notification"""
        self.show(message, "error", duration, on_click)
    
    def clear_all(self):
        """Clear all notifications"""
        info("NotificationSystem", "Clearing all notifications")
        
        for notification in self.notifications[:]:
            notification.destroy()
        
        self.notifications.clear()
        debug("NotificationSystem", "All notifications cleared")

"""
Timeout Warning Dialog
Varnar användaren när session håller på att timeout:a
"""

import customtkinter as ctk
from typing import Callable
from core.debug_logger import debug, info
from core.ui_components import CustomButton, CustomLabel, CustomFrame


class TimeoutWarningDialog(ctk.CTkToplevel):
    """Dialog som varnar för session timeout"""
    
    def __init__(
        self,
        parent,
        remaining_seconds: int,
        on_extend: Callable = None,
        on_logout: Callable = None
    ):
        """
        Initialize timeout warning dialog
        
        Args:
            parent: Parent window
            remaining_seconds: Seconds until timeout
            on_extend: Callback for extend session
            on_logout: Callback for logout
        """
        debug("TimeoutWarningDialog", "Initializing timeout warning dialog")
        
        super().__init__(parent)
        
        self.on_extend = on_extend
        self.on_logout = on_logout
        self.remaining_seconds = remaining_seconds
        
        # Window settings
        self.title("Session Timeout Warning")
        self.geometry("500x300")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 500) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 300) // 2
        self.geometry(f"+{x}+{y}")
        
        self._create_ui()
        
        # Start countdown
        self._update_countdown()
        
        info("TimeoutWarningDialog", "Timeout warning dialog initialized")
    
    def _create_ui(self):
        """Create dialog UI"""
        debug("TimeoutWarningDialog", "Creating dialog UI")
        
        # Main container
        container = CustomFrame(self, transparent=False)
        container.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Warning icon and title
        header_frame = CustomFrame(container, transparent=True)
        header_frame.pack(fill="x", pady=(0, 20))
        
        CustomLabel(
            header_frame,
            text="⚠️",
            size=48
        ).pack()
        
        CustomLabel(
            header_frame,
            text="Session Timeout Warning",
            size=18,
            bold=True
        ).pack(pady=(10, 0))
        
        # Message
        CustomLabel(
            container,
            text="Your session is about to expire due to inactivity.",
            size=12,
            color=("#666666", "#999999")
        ).pack(pady=(0, 10))
        
        # Countdown
        self.countdown_label = CustomLabel(
            container,
            text=self._format_time(self.remaining_seconds),
            size=32,
            bold=True,
            color=("#ff6b6b", "#ff6b6b")
        )
        self.countdown_label.pack(pady=(10, 20))
        
        CustomLabel(
            container,
            text="Time remaining until automatic logout",
            size=10,
            color=("#888888", "#888888")
        ).pack(pady=(0, 20))
        
        # Buttons
        button_frame = CustomFrame(container, transparent=True)
        button_frame.pack(fill="x", pady=(10, 0))
        
        CustomButton(
            button_frame,
            text="Stay Logged In",
            command=self._handle_extend,
            style="success",
            width=200,
            height=45
        ).pack(side="left", padx=(0, 10))
        
        CustomButton(
            button_frame,
            text="Logout Now",
            command=self._handle_logout,
            style="secondary",
            width=200,
            height=45
        ).pack(side="left")
        
        debug("TimeoutWarningDialog", "Dialog UI created")
    
    def _format_time(self, seconds: int) -> str:
        """Format seconds as MM:SS"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
    
    def _update_countdown(self):
        """Update countdown timer"""
        if self.remaining_seconds > 0:
            self.countdown_label.configure(text=self._format_time(self.remaining_seconds))
            self.remaining_seconds -= 1
            self.after(1000, self._update_countdown)
        else:
            # Time's up - auto logout
            debug("TimeoutWarningDialog", "Countdown reached zero - auto logout")
            self._handle_logout()
    
    def _handle_extend(self):
        """Handle extend session"""
        info("TimeoutWarningDialog", "User chose to extend session")
        
        if self.on_extend:
            self.on_extend()
        
        self.destroy()
    
    def _handle_logout(self):
        """Handle logout"""
        info("TimeoutWarningDialog", "User chose to logout (or auto logout)")
        
        if self.on_logout:
            self.on_logout()
        
        self.destroy()

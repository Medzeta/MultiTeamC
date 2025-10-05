"""
Password Reset Module
UI för lösenordsåterställning
"""

import customtkinter as ctk
from typing import Callable, Optional
from core.debug_logger import debug, info, warning, error
from core.ui_components import (
    CustomButton, CustomLabel, CustomFrame, CustomEntry, MessageBox
)
from core.password_reset import PasswordReset


class PasswordResetModule(ctk.CTkFrame):
    """Password reset module"""
    
    def __init__(
        self,
        master,
        on_back: Callable = None,
        on_success: Callable = None,
        **kwargs
    ):
        """
        Initialize password reset module
        
        Args:
            master: Parent widget
            on_back: Callback for back button
            on_success: Callback for successful reset
        """
        debug("PasswordResetModule", "Initializing password reset module")
        
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.on_back = on_back
        self.on_success = on_success
        self.password_reset = PasswordReset()
        
        self.current_step = 1  # 1: Request, 2: Verify Token, 3: New Password
        self.user_info = None
        
        self._create_ui()
        
        info("PasswordResetModule", "Password reset module initialized")
    
    def _create_ui(self):
        """Create password reset UI"""
        debug("PasswordResetModule", "Creating password reset UI")
        
        # Center container
        center_container = CustomFrame(self, transparent=True)
        center_container.pack(expand=True, fill="both")
        
        # Card frame (centrerad ruta)
        card_frame = CustomFrame(center_container, transparent=False)
        card_frame.place(relx=0.5, rely=0.5, anchor="center")
        card_frame.configure(
            width=500,
            height=600,
            border_width=1,
            border_color=("#3a3a3a", "#3a3a3a"),
            corner_radius=10
        )
        
        # Inner content
        inner_content = CustomFrame(card_frame, transparent=True)
        inner_content.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Title
        CustomLabel(
            inner_content,
            text="🔐 Password Reset",
            size=24,
            bold=True
        ).pack(pady=(0, 10))
        
        # Subtitle
        self.subtitle_label = CustomLabel(
            inner_content,
            text="Enter your email to receive a reset token",
            size=11,
            color=("#888888", "#888888")
        )
        self.subtitle_label.pack(pady=(0, 30))
        
        # Content frame (will be replaced based on step)
        self.content_frame = CustomFrame(inner_content, transparent=True)
        self.content_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Back button
        CustomButton(
            inner_content,
            text="← Back to Login",
            command=self._on_back,
            style="secondary",
            width=200,
            height=40
        ).pack()
        
        # Show initial step
        self._show_step_1()
    
    def _show_step_1(self):
        """Show step 1: Request reset token"""
        debug("PasswordResetModule", "Showing step 1: Request token")
        
        self.current_step = 1
        self.subtitle_label.configure(text="Enter your email to receive a reset token")
        
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        content = CustomFrame(self.content_frame, transparent=True)
        content.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Email input
        CustomLabel(
            content,
            text="Email Address:",
            size=12
        ).pack(anchor="w", pady=(0, 5))
        
        self.email_entry = CustomEntry(
            content,
            placeholder="your.email@example.com"
        )
        self.email_entry.pack(fill="x", pady=(0, 20))
        self.email_entry.focus()
        self.email_entry.bind("<Return>", lambda e: self._request_reset())
        
        # Request button
        CustomButton(
            content,
            text="Send Reset Token",
            command=self._request_reset,
            style="primary",
            width=200,
            height=40
        ).pack()
        
        debug("PasswordResetModule", "Step 1 UI created")
    
    def _show_step_2(self):
        """Show step 2: Verify token"""
        debug("PasswordResetModule", "Showing step 2: Verify token")
        
        self.current_step = 2
        self.subtitle_label.configure(text="Check your email and enter the reset token")
        
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        content = CustomFrame(self.content_frame, transparent=True)
        content.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Info message
        info_frame = CustomFrame(content, transparent=False)
        info_frame.pack(fill="x", pady=(0, 20))
        
        CustomLabel(
            info_frame,
            text="📧 Email Sent!",
            size=14,
            bold=True,
            color=("#4da6ff", "#4da6ff")
        ).pack(pady=(15, 5))
        
        CustomLabel(
            info_frame,
            text="We've sent a reset token to your email.\nPlease check your inbox and enter the token below.",
            size=11,
            color=("#888888", "#888888")
        ).pack(pady=(0, 15))
        
        # Token input
        CustomLabel(
            content,
            text="Reset Token:",
            size=12
        ).pack(anchor="w", pady=(0, 5))
        
        self.token_entry = CustomEntry(
            content,
            placeholder="Enter token from email"
        )
        self.token_entry.pack(fill="x", pady=(0, 20))
        self.token_entry.focus()
        self.token_entry.bind("<Return>", lambda e: self._verify_token())
        
        # Verify button
        CustomButton(
            content,
            text="Verify Token",
            command=self._verify_token,
            style="primary",
            width=200,
            height=40
        ).pack()
        
        debug("PasswordResetModule", "Step 2 UI created")
    
    def _show_step_3(self):
        """Show step 3: Set new password"""
        debug("PasswordResetModule", "Showing step 3: New password")
        
        self.current_step = 3
        self.subtitle_label.configure(text="Create your new password")
        
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        content = CustomFrame(self.content_frame, transparent=True)
        content.pack(fill="both", expand=True, padx=40, pady=40)
        
        # New password
        CustomLabel(
            content,
            text="New Password:",
            size=12
        ).pack(anchor="w", pady=(0, 5))
        
        self.password_entry = CustomEntry(
            content,
            placeholder="Enter new password",
            show="•"
        )
        self.password_entry.pack(fill="x", pady=(0, 15))
        self.password_entry.focus()
        
        # Confirm password
        CustomLabel(
            content,
            text="Confirm Password:",
            size=12
        ).pack(anchor="w", pady=(0, 5))
        
        self.confirm_entry = CustomEntry(
            content,
            placeholder="Confirm new password",
            show="•"
        )
        self.confirm_entry.pack(fill="x", pady=(0, 20))
        self.confirm_entry.bind("<Return>", lambda e: self._reset_password())
        
        # Reset button
        CustomButton(
            content,
            text="Reset Password",
            command=self._reset_password,
            style="success",
            width=200,
            height=40
        ).pack()
        
        debug("PasswordResetModule", "Step 3 UI created")
    
    def _request_reset(self):
        """Request password reset"""
        email = self.email_entry.get().strip()
        
        if not email:
            MessageBox.show_error(self, "Error", "Please enter your email address")
            return
        
        debug("PasswordResetModule", f"Requesting reset for: {email}")
        
        # Generate token
        token = self.password_reset.generate_reset_token(email)
        
        if token:
            info("PasswordResetModule", "Reset token generated and sent")
            MessageBox.show_success(
                self,
                "Success",
                "Reset token sent!\n\nCheck your email for the reset token."
            )
            self._show_step_2()
        else:
            error("PasswordResetModule", "Failed to generate reset token")
            MessageBox.show_error(
                self,
                "Error",
                "Email not found or error occurred.\n\nPlease check your email and try again."
            )
    
    def _verify_token(self):
        """Verify reset token"""
        token = self.token_entry.get().strip()
        
        if not token:
            MessageBox.show_error(self, "Error", "Please enter the reset token")
            return
        
        debug("PasswordResetModule", f"Verifying token: {token[:8]}...")
        
        # Verify token
        user_info = self.password_reset.verify_token(token)
        
        if user_info:
            self.user_info = user_info
            info("PasswordResetModule", "Token verified successfully")
            self._show_step_3()
        else:
            error("PasswordResetModule", "Invalid or expired token")
            MessageBox.show_error(
                self,
                "Error",
                "Invalid or expired token!\n\nPlease check the token and try again,\nor request a new one."
            )
    
    def _reset_password(self):
        """Reset password"""
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        if not password or not confirm:
            MessageBox.show_error(self, "Error", "Please fill in all fields")
            return
        
        if password != confirm:
            MessageBox.show_error(self, "Error", "Passwords do not match!")
            return
        
        if len(password) < 6:
            MessageBox.show_error(self, "Error", "Password must be at least 6 characters")
            return
        
        debug("PasswordResetModule", "Resetting password")
        
        # Reset password
        success = self.password_reset.reset_password(
            self.user_info['token'],
            password
        )
        
        if success:
            info("PasswordResetModule", "Password reset successful")
            MessageBox.show_success(
                self,
                "Success",
                "Password Reset Successful!\n\nYou can now login with your new password."
            )
            
            # Call success callback
            if self.on_success:
                self.on_success()
            else:
                self._on_back()
        else:
            error("PasswordResetModule", "Failed to reset password")
            MessageBox.show_error(
                self,
                "Error",
                "Failed to reset password!\n\nPlease try again."
            )
    
    def _on_back(self):
        """Handle back button"""
        debug("PasswordResetModule", "Back button clicked")
        
        if self.on_back:
            self.on_back()

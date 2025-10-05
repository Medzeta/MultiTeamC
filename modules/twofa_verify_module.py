"""
2FA Verification Module
Används vid login för att verifiera 2FA-kod
"""

import customtkinter as ctk
from typing import Callable
from core.debug_logger import debug, info, warning
from core.ui_components import (
    CustomButton, CustomEntry, CustomLabel,
    CustomFrame, MessageBox
)
from core.twofa_system import TwoFASystem


class TwoFAVerifyModule(ctk.CTkFrame):
    """2FA verification module för login"""
    
    def __init__(
        self,
        master,
        user_id: int,
        user_email: str,
        secret: str,
        on_success: Callable,
        on_cancel: Callable,
        **kwargs
    ):
        """Initialize 2FA verify module"""
        debug("TwoFAVerifyModule", f"Initializing 2FA verify for user: {user_email}")
        
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.user_id = user_id
        self.user_email = user_email
        self.secret = secret
        self.on_success = on_success
        self.on_cancel = on_cancel
        self.twofa = TwoFASystem()
        
        self.attempts = 0
        self.max_attempts = 3
        
        self._create_ui()
        
        info("TwoFAVerifyModule", "2FA verify module initialized")
    
    def _create_ui(self):
        """Create 2FA verification UI"""
        debug("TwoFAVerifyModule", "Creating 2FA verification UI")
        
        # Center container
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        container = CustomFrame(self, transparent=False)
        container.grid(row=0, column=0, sticky="")
        container.configure(width=450, height=500)
        
        # Title
        title_frame = CustomFrame(container, transparent=True)
        title_frame.pack(pady=(40, 30))
        
        icon_label = CustomLabel(title_frame, text="🔐", size=64)
        icon_label.pack()
        
        title_label = CustomLabel(
            title_frame,
            text="Two-Factor Authentication",
            size=24,
            bold=True
        )
        title_label.pack(pady=(15, 5))
        
        subtitle_label = CustomLabel(
            title_frame,
            text=f"Enter code for {self.user_email}",
            size=12,
            color=("#999999", "#999999")
        )
        subtitle_label.pack()
        
        # Instructions
        instruction_frame = CustomFrame(container, transparent=True)
        instruction_frame.pack(pady=20, padx=40)
        
        CustomLabel(
            instruction_frame,
            text="Open your authenticator app and enter the 6-digit code:",
            size=11,
            color=("#cccccc", "#cccccc")
        ).pack()
        
        # Code entry
        self.code_entry = CustomEntry(
            container,
            placeholder="000000",
            width=250,
            height=60
        )
        self.code_entry.configure(font=("Courier New", 24, "bold"), justify="center")
        self.code_entry.pack(pady=20)
        self.code_entry.bind("<Return>", lambda e: self._verify_code())
        self.code_entry.focus()
        
        # Attempts remaining
        self.attempts_label = CustomLabel(
            container,
            text=f"Attempts remaining: {self.max_attempts - self.attempts}",
            size=10,
            color=("#666666", "#666666")
        )
        self.attempts_label.pack(pady=(0, 20))
        
        # Verify button
        self.verify_btn = CustomButton(
            container,
            text="Verify Code",
            command=self._verify_code,
            width=250,
            height=45,
            style="primary"
        )
        self.verify_btn.pack(pady=10)
        
        # Divider
        divider_frame = CustomFrame(container, transparent=True)
        divider_frame.pack(fill="x", pady=20, padx=40)
        
        divider_left = ctk.CTkFrame(divider_frame, height=1, fg_color=("#3a3a3a", "#2a2a2a"))
        divider_left.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        divider_label = CustomLabel(divider_frame, text="OR", size=10, color=("#666666", "#666666"))
        divider_label.pack(side="left")
        
        divider_right = ctk.CTkFrame(divider_frame, height=1, fg_color=("#3a3a3a", "#2a2a2a"))
        divider_right.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # Backup code button
        backup_btn = CustomButton(
            container,
            text="Use Backup Code",
            command=self._use_backup_code,
            width=250,
            height=40,
            style="transparent"
        )
        backup_btn.pack(pady=5)
        
        # Cancel button
        cancel_btn = CustomButton(
            container,
            text="← Cancel",
            command=self._handle_cancel,
            width=250,
            height=40,
            style="transparent"
        )
        cancel_btn.pack(pady=(10, 20))
        
        debug("TwoFAVerifyModule", "2FA verification UI created")
    
    def _verify_code(self):
        """Verify 2FA code"""
        debug("TwoFAVerifyModule", "Verifying 2FA code")
        
        code = self.code_entry.get_value().strip()
        
        if not code:
            warning("TwoFAVerifyModule", "Code is empty")
            MessageBox.show_error(
                self.master,
                "Verification Error",
                "Please enter the 6-digit code."
            )
            return
        
        if len(code) != 6 or not code.isdigit():
            warning("TwoFAVerifyModule", "Invalid code format")
            MessageBox.show_error(
                self.master,
                "Verification Error",
                "Please enter a valid 6-digit code."
            )
            return
        
        # Verify token
        if self.twofa.verify_token(self.secret, code):
            info("TwoFAVerifyModule", "2FA code verified successfully")
            MessageBox.show_success(
                self.master,
                "Verified!",
                "Two-factor authentication successful."
            )
            self.after(100, self.on_success)
        else:
            self.attempts += 1
            warning("TwoFAVerifyModule", f"2FA verification failed (attempt {self.attempts}/{self.max_attempts})")
            
            if self.attempts >= self.max_attempts:
                error("TwoFAVerifyModule", "Max attempts reached")
                MessageBox.show_error(
                    self.master,
                    "Too Many Attempts",
                    "Maximum verification attempts reached.\n\nPlease try again later or use a backup code."
                )
                self.verify_btn.configure(state="disabled")
                self.code_entry.configure(state="disabled")
            else:
                self.attempts_label.configure(text=f"Attempts remaining: {self.max_attempts - self.attempts}")
                MessageBox.show_error(
                    self.master,
                    "Verification Failed",
                    f"Invalid code. Please try again.\n\n{self.max_attempts - self.attempts} attempt(s) remaining."
                )
                self.code_entry.delete(0, "end")
                self.code_entry.focus()
    
    def _use_backup_code(self):
        """Show backup code entry dialog"""
        debug("TwoFAVerifyModule", "Backup code option selected")
        
        from core.custom_window import CustomDialog
        
        dialog = CustomDialog(self.master, title="Use Backup Code", width=400, height=250)
        
        content = CustomFrame(dialog.content_frame, transparent=True)
        content.pack(expand=True, fill="both", padx=20, pady=20)
        
        CustomLabel(
            content,
            text="Enter Backup Code",
            size=16,
            bold=True
        ).pack(pady=(10, 5))
        
        CustomLabel(
            content,
            text="Enter one of your 8-character backup codes:",
            size=11,
            color=("#999999", "#999999")
        ).pack(pady=(0, 15))
        
        backup_entry = CustomEntry(
            content,
            placeholder="XXXXXXXX",
            width=250,
            height=45
        )
        backup_entry.configure(font=("Courier New", 14, "bold"), justify="center")
        backup_entry.pack(pady=10)
        backup_entry.focus()
        
        def verify_backup():
            code = backup_entry.get_value().strip().upper()
            
            if not code:
                MessageBox.show_error(dialog, "Error", "Please enter a backup code.")
                return
            
            if len(code) != 8:
                MessageBox.show_error(dialog, "Error", "Backup codes are 8 characters long.")
                return
            
            debug("TwoFAVerifyModule", "Verifying backup code")
            if self.twofa.verify_backup_code(self.user_id, code):
                info("TwoFAVerifyModule", "Backup code verified successfully")
                dialog._close_dialog()
                MessageBox.show_success(
                    self.master,
                    "Verified!",
                    "Backup code accepted.\n\nNote: This code has been used and cannot be used again."
                )
                self.after(100, self.on_success)
            else:
                warning("TwoFAVerifyModule", "Invalid backup code")
                MessageBox.show_error(
                    dialog,
                    "Verification Failed",
                    "Invalid backup code. Please check and try again."
                )
        
        btn_frame = CustomFrame(content, transparent=True)
        btn_frame.pack(pady=(15, 0))
        
        CustomButton(
            btn_frame,
            text="Verify",
            command=verify_backup,
            width=120,
            height=35,
            style="success"
        ).pack(side="left", padx=5)
        
        CustomButton(
            btn_frame,
            text="Cancel",
            command=dialog._close_dialog,
            width=120,
            height=35,
            style="secondary"
        ).pack(side="left", padx=5)
        
        backup_entry.bind("<Return>", lambda e: verify_backup())
    
    def _handle_cancel(self):
        """Handle cancel button"""
        debug("TwoFAVerifyModule", "Cancel button clicked")
        self.on_cancel()


if __name__ == "__main__":
    # Test 2FA verify module
    info("TEST", "Testing TwoFAVerifyModule...")
    
    from core.custom_window import CustomWindow
    import pyotp
    
    # Generate test secret
    secret = pyotp.random_base32()
    print(f"Test secret: {secret}")
    print(f"Current token: {pyotp.TOTP(secret).now()}")
    
    def on_success():
        print("2FA verification successful")
    
    def on_cancel():
        print("2FA verification cancelled")
    
    app = CustomWindow(title="2FA Verify Test", width=500, height=550)
    
    verify_module = TwoFAVerifyModule(
        app.content_frame,
        user_id=1,
        user_email="test@example.com",
        secret=secret,
        on_success=on_success,
        on_cancel=on_cancel
    )
    verify_module.pack(fill="both", expand=True)
    
    info("TEST", "Starting mainloop...")
    app.mainloop()

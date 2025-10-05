"""
2FA Setup Module
Användare kan aktivera/inaktivera 2FA och scanna QR-kod
"""

import customtkinter as ctk
from typing import Callable, Optional
from PIL import Image, ImageTk
from io import BytesIO
from core.debug_logger import debug, info, warning, error
from core.ui_components import (
    CustomButton, CustomEntry, CustomLabel,
    CustomFrame, MessageBox
)
from core.twofa_system import TwoFASystem


class TwoFASetupModule(ctk.CTkFrame):
    """2FA setup module"""
    
    def __init__(
        self,
        master,
        user_id: int,
        user_email: str,
        on_complete: Callable,
        on_cancel: Callable,
        **kwargs
    ):
        """Initialize 2FA setup module"""
        debug("TwoFASetupModule", f"Initializing 2FA setup for user: {user_email}")
        
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.user_id = user_id
        self.user_email = user_email
        self.on_complete = on_complete
        self.on_cancel = on_cancel
        self.twofa = TwoFASystem()
        
        # Check current 2FA status
        self.is_enabled, self.current_secret = self.twofa.get_user_2fa_status(user_id)
        
        # Generate new secret and backup codes
        self.secret = self.twofa.generate_secret()
        self.backup_codes = self.twofa.generate_backup_codes()
        
        self._create_ui()
        
        info("TwoFASetupModule", "2FA setup module initialized")
    
    def _create_ui(self):
        """Create 2FA setup UI - Professional full-window layout"""
        debug("TwoFASetupModule", "Creating 2FA setup UI")
        
        # Use full window
        scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_fg_color=("#2b2b2b", "#2b2b2b"),
            scrollbar_button_color=("#3b3b3b", "#3b3b3b"),
            scrollbar_button_hover_color=("#4b4b4b", "#4b4b4b")
        )
        scroll_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Title
        CustomLabel(scroll_frame, text="🔐 Two-Factor Authentication", size=18, bold=True).pack(pady=(0, 20))
        
        # Step 1: Download App
        step1 = self._create_step(scroll_frame, "1", "Download Authenticator App", 
                                   "Install Google Authenticator, Microsoft Authenticator, or Authy on your phone.")
        
        # Step 2: Scan QR Code
        step2 = self._create_step(scroll_frame, "2", "Scan QR Code", 
                                   "Open your authenticator app and scan this QR code:")
        
        # QR Code
        qr_image = self.twofa.generate_qr_code(self.user_email, self.secret)
        if qr_image:
            qr_photo = ImageTk.PhotoImage(qr_image)
            qr_label = ctk.CTkLabel(step2, image=qr_photo, text="")
            qr_label.image = qr_photo
            qr_label.pack(pady=10)
        
        # Step 3: Enter Code
        step3 = self._create_step(scroll_frame, "3", "Enter Verification Code", 
                                   "Enter the 6-digit code from your authenticator app:")
        
        self.code_entry = CustomEntry(step3, placeholder="000000", width=200, height=50)
        self.code_entry.configure(font=("Courier New", 18, "bold"), justify="center")
        self.code_entry.pack(pady=10)
        self.code_entry.bind("<Return>", lambda e: self._verify_and_enable())
        self.after(300, lambda: self.code_entry.focus_force())
        
        # Backup Codes
        backup_frame = CustomFrame(scroll_frame, transparent=False)
        backup_frame.pack(fill="x", pady=15)
        
        CustomLabel(backup_frame, text="💾 Backup Codes", size=14, bold=True).pack(pady=(15, 5))
        CustomLabel(backup_frame, text="Save these codes. Each can be used once if you lose your authenticator.", 
                   size=10, color=("#999999", "#999999")).pack(pady=(0, 10))
        
        # Two columns
        codes_container = CustomFrame(backup_frame, transparent=True)
        codes_container.pack(pady=(0, 15))
        
        mid = len(self.backup_codes) // 2
        left_codes = ctk.CTkTextbox(codes_container, width=350, height=120, font=("Courier New", 11))
        left_codes.pack(side="left", padx=(0, 10))
        left_codes.insert("1.0", "\n".join([f"  {i+1}. {code}" for i, code in enumerate(self.backup_codes[:mid])]))
        left_codes.configure(state="disabled")
        
        right_codes = ctk.CTkTextbox(codes_container, width=350, height=120, font=("Courier New", 11))
        right_codes.pack(side="left")
        right_codes.insert("1.0", "\n".join([f"  {i+mid+1}. {code}" for i, code in enumerate(self.backup_codes[mid:])]))
        right_codes.configure(state="disabled")
        
        # Buttons
        button_frame = CustomFrame(scroll_frame, transparent=True)
        button_frame.pack(pady=15)
        
        CustomButton(button_frame, text="✓ Verify & Enable 2FA", command=self._verify_and_enable, 
                    width=250, height=45, style="success").pack(side="left", padx=10)
        CustomButton(button_frame, text="Cancel", command=self._handle_cancel, 
                    width=150, height=45, style="secondary").pack(side="left", padx=10)
        
        debug("TwoFASetupModule", "2FA setup UI created successfully")
    
    def _create_step(self, parent, number: str, title: str, description: str) -> ctk.CTkFrame:
        """Create a step section"""
        step_frame = CustomFrame(parent, transparent=False)
        step_frame.pack(fill="x", pady=10, padx=20)
        
        # Header
        header_frame = CustomFrame(step_frame, transparent=True)
        header_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        # Step number circle
        number_label = ctk.CTkLabel(
            header_frame,
            text=number,
            font=("Segoe UI", 16, "bold"),
            width=35,
            height=35,
            fg_color=("#1f6aa5", "#144870"),
            corner_radius=17
        )
        number_label.pack(side="left", padx=(0, 15))
        
        # Title
        title_label = CustomLabel(
            header_frame,
            text=title,
            size=14,
            bold=True
        )
        title_label.pack(side="left", anchor="w")
        
        # Description
        desc_label = CustomLabel(
            step_frame,
            text=description,
            size=11,
            color=("#cccccc", "#cccccc")
        )
        desc_label.pack(anchor="w", padx=(75, 20), pady=(0, 15))
        
        return step_frame
    
    def _verify_and_enable(self):
        """Verify code and enable 2FA"""
        debug("TwoFASetupModule", "Verify and enable 2FA")
        
        code = self.code_entry.get_value().strip()
        
        if not code:
            warning("TwoFASetupModule", "Code is empty")
            MessageBox.show_error(
                self.master,
                "Verification Error",
                "Please enter the 6-digit code from your authenticator app."
            )
            return
        
        if len(code) != 6 or not code.isdigit():
            warning("TwoFASetupModule", "Invalid code format")
            MessageBox.show_error(
                self.master,
                "Verification Error",
                "Please enter a valid 6-digit code."
            )
            return
        
        # Verify token
        debug("TwoFASetupModule", "Verifying TOTP token")
        if self.twofa.verify_token(self.secret, code):
            info("TwoFASetupModule", "Token verified successfully")
            
            # Enable 2FA for user
            if self.twofa.enable_2fa_for_user(self.user_id, self.secret, self.backup_codes):
                info("TwoFASetupModule", f"2FA enabled for user: {self.user_email}")
                
                MessageBox.show_success(
                    self.master,
                    "2FA Enabled!",
                    "Two-Factor Authentication has been enabled successfully.\n\nMake sure to save your backup codes!"
                )
                
                # Complete setup
                self.after(100, self.on_complete)
            else:
                error("TwoFASetupModule", "Failed to enable 2FA")
                MessageBox.show_error(
                    self.master,
                    "Setup Error",
                    "Failed to enable 2FA. Please try again."
                )
        else:
            warning("TwoFASetupModule", "Token verification failed")
            MessageBox.show_error(
                self.master,
                "Verification Failed",
                "Invalid code. Please check your authenticator app and try again."
            )
    
    def _handle_cancel(self):
        """Handle cancel button"""
        debug("TwoFASetupModule", "Cancel button clicked")
        self.on_cancel()


if __name__ == "__main__":
    # Test 2FA setup module
    info("TEST", "Testing TwoFASetupModule...")
    
    from core.custom_window import CustomWindow
    
    def on_complete():
        print("2FA setup completed")
    
    def on_cancel():
        print("2FA setup cancelled")
    
    app = CustomWindow(title="2FA Setup Test", width=650, height=750)
    
    setup_module = TwoFASetupModule(
        app.content_frame,
        user_id=1,
        user_email="test@example.com",
        on_complete=on_complete,
        on_cancel=on_cancel
    )
    setup_module.pack(fill="both", expand=True)
    
    info("TEST", "Starting mainloop...")
    app.mainloop()

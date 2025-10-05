"""
Forgot Password Module för Multi Team -C
Komplett lösenordsåterställning med email-baserat token system
Följer global UI design och full debug logging
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QFrame, 
                            QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from core.pyqt_theme import Theme
from core.debug_logger import debug, info, error, warning
from core.auth_system import AuthSystem
from core.email_service import EmailService
from core.database_manager import db
import secrets
import string
import sqlite3
from datetime import datetime, timedelta


class ForgotPasswordModule(QWidget):
    """
    Forgot Password Module med global UI design
    Implementerar säker lösenordsåterställning via email
    """
    
    # Signals
    back_to_login = pyqtSignal()
    password_reset_success = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.auth_system = AuthSystem()
        self.email_service = EmailService()
        self.reset_token = None
        self.reset_email = None
        self.token_expiry = None
        
        debug("ForgotPasswordModule", "="*60)
        debug("ForgotPasswordModule", "INITIALIZING FORGOT PASSWORD MODULE")
        debug("ForgotPasswordModule", "="*60)
        
        self._create_ui()
        
        info("ForgotPasswordModule", "Forgot password module initialized successfully")
    
    def _create_ui(self):
        """Skapa forgot password UI - FAST LAYOUT UTAN SCROLL"""
        debug("ForgotPasswordModule", "Creating forgot password UI WITHOUT SCROLL")
        
        # Main layout - FAST LAYOUT UTAN SCROLL
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        debug("ForgotPasswordModule", "Main layout: margins=0, spacing=0, centered")
        
        # Forgot password card - Fast storlek enligt GLOBAL_DESIGN.md
        debug("ForgotPasswordModule", "Creating forgot password card with FIXED SIZE...")
        self._create_forgot_password_card(main_layout)
        debug("ForgotPasswordModule", "Forgot password card added to main layout - NO SCROLL")
        
        debug("ForgotPasswordModule", "Forgot password UI created successfully")
    
    def _create_forgot_password_card(self, layout):
        """Skapa forgot password card med global design"""
        debug("ForgotPasswordModule", "Creating forgot password card")
        
        # Card frame (samma storlek som login card enligt global design)
        self.card_frame = QFrame()
        # Use global card size
        self.card_frame.setFixedSize(Theme.CARD_WIDTH, Theme.CARD_HEIGHT)
        self.card_frame.setStyleSheet(Theme.create_login_card_style())
        debug("ForgotPasswordModule", f"Card size set to: {Theme.CARD_WIDTH}x{Theme.CARD_HEIGHT}px (global)")
        
        # Card layout (mycket tightare spacing)
        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(3)
        
        # Komplett header-sekvens med korrekt spacing (samma som login)
        title_label, subtitle_label, section_label = Theme.setup_complete_header_sequence(card_layout, "Reset Password")
        
        # Email input (med instruktioner precis ovanför)
        self._create_email_input(card_layout)
        
        # Reset code input (dold initialt)
        self._create_reset_code_input(card_layout)
        
        # New password inputs (dolda initialt)
        self._create_new_password_inputs(card_layout)
        
        # Action buttons
        self._create_action_buttons(card_layout)
        
        # Back to login
        self._create_back_button(card_layout)
        
        layout.addWidget(self.card_frame, alignment=Qt.AlignmentFlag.AlignCenter)
        debug("ForgotPasswordModule", "Forgot password card created successfully")
    
    def _create_email_input(self, layout):
        """Skapa email input med label till vänster"""
        debug("ForgotPasswordModule", "Creating email input with label")
        
        # Instruktioner ovanför
        self.instructions_label = QLabel("Enter your email address and we'll send you a reset code.")
        self.instructions_label.setFont(Theme.get_font(size=11))
        self.instructions_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY};")
        self.instructions_label.setWordWrap(True)
        layout.addWidget(self.instructions_label)
        
        # Email row med label till vänster
        email_row = QHBoxLayout()
        email_row.setSpacing(Theme.SPACING_MD)
        email_row.setContentsMargins(0, 0, 0, 0)
        
        email_label = QLabel("Email:")
        email_label.setFixedWidth(120)
        Theme.setup_secondary_text(email_label, size=14)
        email_row.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email address")
        Theme.setup_text_field(self.email_input)
        self.email_input.returnPressed.connect(self._handle_send_reset_code)
        email_row.addWidget(self.email_input)
        
        layout.addLayout(email_row)
        
        debug("ForgotPasswordModule", "Email input created with label")
    
    def _create_reset_code_input(self, layout):
        """Skapa reset code input (dold initialt)"""
        debug("ForgotPasswordModule", "Creating reset code input")
        
        # Code container
        self.code_container = QWidget()
        code_layout = QVBoxLayout(self.code_container)
        code_layout.setContentsMargins(0, 0, 0, 0)
        code_layout.setSpacing(2)
        
        # Code label
        code_label = QLabel("Reset Code")
        code_label.setFont(Theme.get_font(size=11, bold=True))
        code_label.setStyleSheet(f"color: {Theme.TEXT}; margin-bottom: 2px;")
        code_layout.addWidget(code_label)
        
        # Code input
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Enter the 6-digit code from email")
        self.code_input.setMaxLength(6)
        Theme.setup_text_field(self.code_input)
        self.code_input.returnPressed.connect(self._handle_verify_code)
        code_layout.addWidget(self.code_input)
        
        # Dölj initialt
        self.code_container.hide()
        layout.addWidget(self.code_container)
        
        debug("ForgotPasswordModule", "Reset code input created (hidden)")
    
    def _create_new_password_inputs(self, layout):
        """Skapa nya lösenord inputs (dolda initialt)"""
        debug("ForgotPasswordModule", "Creating new password inputs")
        
        # Password container
        self.password_container = QWidget()
        password_layout = QVBoxLayout(self.password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(5)
        
        # New password
        new_password_label = QLabel("New Password")
        new_password_label.setFont(Theme.get_font(size=11, bold=True))
        new_password_label.setStyleSheet(f"color: {Theme.TEXT}; margin-bottom: 2px;")
        password_layout.addWidget(new_password_label)
        
        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("Enter new password")
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        Theme.setup_text_field(self.new_password_input)
        password_layout.addWidget(self.new_password_input)
        
        # Confirm password
        confirm_password_label = QLabel("Confirm Password")
        confirm_password_label.setFont(Theme.get_font(size=11, bold=True))
        confirm_password_label.setStyleSheet(f"color: {Theme.TEXT}; margin-bottom: 2px;")
        password_layout.addWidget(confirm_password_label)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm new password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        Theme.setup_text_field(self.confirm_password_input)
        self.confirm_password_input.returnPressed.connect(self._handle_reset_password)
        password_layout.addWidget(self.confirm_password_input)
        
        # Dölj initialt
        self.password_container.hide()
        layout.addWidget(self.password_container)
        
        debug("ForgotPasswordModule", "New password inputs created (hidden)")
    
    def _create_action_buttons(self, layout):
        """Skapa action buttons aligned with text fields"""
        debug("ForgotPasswordModule", "Creating action buttons")
        
        # Add spacing before buttons (global design)
        layout.addSpacing(Theme.SPACING_XL)  # 15px spacing
        
        # Button row aligned with text fields
        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.setSpacing(Theme.SPACING_MD)
        
        # Add spacing to align with text fields (120px label + 8px spacing)
        button_row.addSpacing(128)
        
        # Primary action button
        self.action_btn = QPushButton("Send Reset Code")
        Theme.setup_login_button(self.action_btn, width=150)
        self.action_btn.clicked.connect(self._handle_primary_action)
        button_row.addWidget(self.action_btn)
        
        # Secondary action button (dold initialt)
        self.secondary_btn = QPushButton("Resend Code")
        Theme.setup_login_button(self.secondary_btn, width=120)
        self.secondary_btn.clicked.connect(self._handle_resend_code)
        self.secondary_btn.hide()
        button_row.addWidget(self.secondary_btn)
        
        # Back button
        back_btn = QPushButton("← Back to Login")
        Theme.setup_login_button(back_btn, width=130)
        back_btn.clicked.connect(lambda: self.back_to_login.emit())
        button_row.addWidget(back_btn)
        
        button_row.addStretch()
        
        layout.addLayout(button_row)
        debug("ForgotPasswordModule", "Action buttons created aligned with text fields")
    
    def _create_back_button(self, layout):
        """Back button nu integrerad i action buttons"""
        pass
    
    def _handle_primary_action(self):
        """Hantera primär action baserat på nuvarande steg"""
        debug("ForgotPasswordModule", "Primary action triggered")
        
        if self.action_btn.text() == "Send Reset Code":
            self._handle_send_reset_code()
        elif self.action_btn.text() == "Verify Code":
            self._handle_verify_code()
        elif self.action_btn.text() == "Reset Password":
            self._handle_reset_password()
    
    def _handle_send_reset_code(self):
        """Skicka reset code via email"""
        email = self.email_input.text().strip()
        
        debug("ForgotPasswordModule", f"Attempting to send reset code to: {email}")
        
        if not email:
            self._show_error("Please enter your email address.")
            return
        
        if not self._validate_email(email):
            self._show_error("Please enter a valid email address.")
            return
        
        # Kontrollera om email finns i databasen
        if not self._email_exists(email):
            # Av säkerhetsskäl, visa samma meddelande även om email inte finns
            debug("ForgotPasswordModule", f"Email {email} not found in database, but showing success message for security")
        
        # Generera reset token
        self.reset_token = self._generate_reset_token()
        self.reset_email = email
        self.token_expiry = datetime.now() + timedelta(minutes=15)  # 15 minuters giltighet
        
        debug("ForgotPasswordModule", f"Generated reset token: {self.reset_token}")
        debug("ForgotPasswordModule", f"Token expires at: {self.token_expiry}")
        
        # Spara token i databas
        self._save_reset_token(email, self.reset_token, self.token_expiry)
        
        # Skicka email
        if self._send_reset_email(email, self.reset_token):
            self._show_success("Reset code sent! Check your email.")
            self._switch_to_code_verification()
        else:
            self._show_error("Failed to send reset code. Please try again.")
    
    def _handle_verify_code(self):
        """Verifiera reset code"""
        code = self.code_input.text().strip()
        
        debug("ForgotPasswordModule", f"Verifying reset code: {code}")
        
        if not code:
            self._show_error("Please enter the reset code.")
            return
        
        if len(code) != 6:
            self._show_error("Reset code must be 6 digits.")
            return
        
        # Verifiera token
        debug("ForgotPasswordModule", f"Attempting to verify token for email: {self.reset_email}")
        if self._verify_reset_token(self.reset_email, code):
            debug("ForgotPasswordModule", "Reset code verified successfully")
            self._show_success("Code verified! Enter your new password.")
            debug("ForgotPasswordModule", "About to switch to password reset")
            self._switch_to_password_reset()
            debug("ForgotPasswordModule", "Switched to password reset completed")
        else:
            debug("ForgotPasswordModule", "Reset code verification failed")
            self._show_error("Invalid or expired reset code.")
    
    def _handle_reset_password(self):
        """Återställ lösenord"""
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        debug("ForgotPasswordModule", "Attempting to reset password")
        
        if not new_password:
            self._show_error("Please enter a new password.")
            return
        
        if new_password != confirm_password:
            self._show_error("Passwords do not match.")
            return
        
        if len(new_password) < 6:
            self._show_error("Password must be at least 6 characters.")
            return
        
        # Uppdatera lösenord i databas
        if self._update_password(self.reset_email, new_password):
            # Ta bort använt token
            self._delete_reset_token(self.reset_email)
            
            debug("ForgotPasswordModule", f"Password reset successful for {self.reset_email}")
            self._show_success("Password reset successful! You can now login.")
            
            # Vänta 2 sekunder och gå tillbaka till login
            QTimer.singleShot(2000, lambda: self.back_to_login.emit())
        else:
            self._show_error("Failed to reset password. Please try again.")
    
    def _handle_resend_code(self):
        """Skicka om reset code"""
        debug("ForgotPasswordModule", "Resending reset code")
        self._handle_send_reset_code()
    
    def _switch_to_code_verification(self):
        """Växla till code verification steg"""
        debug("ForgotPasswordModule", "Switching to code verification step")
        
        # Uppdatera instruktioner
        self.instructions_label.setText("Enter the 6-digit code sent to your email.")
        
        # Visa code input
        self.code_container.show()
        
        # Uppdatera button
        self.action_btn.setText("Verify Code")
        
        # Visa resend button
        self.secondary_btn.show()
        
        # Fokusera på code input
        self.code_input.setFocus()
        
        debug("ForgotPasswordModule", "Switched to code verification step")
    
    def _switch_to_password_reset(self):
        """Växla till password reset steg"""
        debug("ForgotPasswordModule", "Switching to password reset step")
        
        # Uppdatera instruktioner
        self.instructions_label.setText("Enter your new password below.")
        
        # Dölj code input
        self.code_container.hide()
        
        # Visa password inputs
        self.password_container.show()
        
        # Uppdatera button
        self.action_btn.setText("Reset Password")
        
        # Dölj resend button
        self.secondary_btn.hide()
        
        # Fokusera på new password input
        self.new_password_input.setFocus()
        
        debug("ForgotPasswordModule", "Switched to password reset step")
    
    def _generate_reset_token(self):
        """Generera säker 6-siffrig reset token"""
        token = ''.join(secrets.choice(string.digits) for _ in range(6))
        debug("ForgotPasswordModule", f"Generated secure reset token: {token}")
        return token
    
    def _validate_email(self, email):
        """Validera email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = re.match(pattern, email) is not None
        debug("ForgotPasswordModule", f"Email validation for {email}: {is_valid}")
        return is_valid
    
    def _email_exists(self, email):
        """Kontrollera om email finns i databasen"""
        try:
            # Använd DatabaseManager för att kontrollera email
            user = db.get_user_by_email(email)
            exists = user is not None
            debug("ForgotPasswordModule", f"Email {email} exists in database: {exists}")
            return exists
            
        except Exception as e:
            error("ForgotPasswordModule", f"Error checking email existence: {e}")
            return False
    
    def _save_reset_token(self, email, token, expiry):
        """Spara reset token i databas"""
        try:
            return db.save_reset_token(email, token, expiry)
        except Exception as e:
            error("ForgotPasswordModule", f"Error saving reset token: {e}")
            return False
    
    def _verify_reset_token(self, email, token):
        """Verifiera reset token"""
        try:
            return db.verify_reset_token(email, token)
        except Exception as e:
            error("ForgotPasswordModule", f"Error verifying reset token: {e}")
            return False
    
    def _update_password(self, email, new_password):
        """Uppdatera lösenord i databas"""
        try:
            # Använd DatabaseManager för att uppdatera lösenord
            success = db.update_user_password(email, new_password)
            
            if success:
                debug("ForgotPasswordModule", f"Password updated for {email}")
            else:
                error("ForgotPasswordModule", f"Failed to update password for {email}")
            
            return success
            
        except Exception as e:
            error("ForgotPasswordModule", f"Error updating password: {e}")
            return False
    
    def _delete_reset_token(self, email):
        """Ta bort använd reset token"""
        try:
            db.delete_reset_token(email)
            debug("ForgotPasswordModule", f"Reset token deleted for {email}")
        except Exception as e:
            error("ForgotPasswordModule", f"Error deleting reset token: {e}")
    
    def _send_reset_email(self, email, token):
        """Skicka reset email"""
        try:
            subject = "Multi Team -C - Password Reset Code"
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .logo {{ font-size: 24px; font-weight: bold; color: #1f6aa5; }}
                    .code {{ font-size: 32px; font-weight: bold; color: #1f6aa5; text-align: center; 
                             background: #f0f8ff; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                    .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; 
                              text-align: center; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">Multi Team -C</div>
                        <p>Password Reset Request</p>
                    </div>
                    
                    <p>Hello,</p>
                    
                    <p>You requested a password reset for your Multi Team -C account. Use the code below to reset your password:</p>
                    
                    <div class="code">{token}</div>
                    
                    <p><strong>Important:</strong></p>
                    <ul>
                        <li>This code expires in 15 minutes</li>
                        <li>Do not share this code with anyone</li>
                        <li>If you didn't request this reset, please ignore this email</li>
                    </ul>
                    
                    <p>Best regards,<br>Multi Team -C Team</p>
                    
                    <div class="footer">
                        <p>This is an automated message. Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            success = self.email_service.send_email(email, subject, "Password reset code", html_body)
            
            if success:
                info("ForgotPasswordModule", f"Reset email sent successfully to {email}")
            else:
                error("ForgotPasswordModule", f"Failed to send reset email to {email}")
            
            return success
            
        except Exception as e:
            error("ForgotPasswordModule", f"Error sending reset email: {e}")
            return False
    
    def _show_success(self, message):
        """Visa success meddelande"""
        debug("ForgotPasswordModule", f"Success: {message}")
        from core.custom_dialog import show_info
        show_info(self, "Success", message)
    
    def _show_error(self, message):
        """Visa error meddelande"""
        debug("ForgotPasswordModule", f"Error: {message}")
        from core.custom_dialog import show_error
        show_error(self, "Error", message)
    
    def reset_form(self):
        """Återställ formuläret till initial state"""
        debug("ForgotPasswordModule", "Resetting form to initial state")
        
        # Rensa inputs
        self.email_input.clear()
        self.code_input.clear()
        self.new_password_input.clear()
        self.confirm_password_input.clear()
        
        # Återställ UI
        self.instructions_label.setText("Enter your email address and we'll send you a reset code.")
        self.code_container.hide()
        self.password_container.hide()
        self.action_btn.setText("Send Reset Code")
        self.secondary_btn.hide()
        
        # Fokusera på email
        self.email_input.setFocus()
        
        # Rensa token data
        self.reset_token = None
        self.reset_email = None
        self.token_expiry = None
        
        debug("ForgotPasswordModule", "Form reset completed")

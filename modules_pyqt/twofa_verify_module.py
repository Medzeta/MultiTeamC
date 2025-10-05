"""
2FA Verify Module med Global UI Design
Implementerar verifiering av 2FA kod vid inloggning
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QFrame, 
                            QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from core.pyqt_theme import Theme
from core.debug_logger import debug, info, error, warning
from core.twofa_system import TwoFASystem
from core.custom_dialog import show_error
import time


class TwoFAVerifyModule(QWidget):
    """
    2FA Verify Module med global UI design
    Implementerar verifiering av 2FA kod vid inloggning
    """
    
    # Signals
    verification_success = pyqtSignal(dict)  # Skicka user_data vid success
    back_to_login = pyqtSignal()
    
    def __init__(self, user_data):
        super().__init__()
        
        debug("TwoFAVerifyModule", "Initializing 2FA verify module")
        
        self.user_data = user_data
        self.twofa_system = TwoFASystem()
        self.attempt_count = 0
        self.max_attempts = 5
        self.lockout_time = 300  # 5 minuter
        self.last_attempt_time = 0
        
        self._create_ui()
        
        info("TwoFAVerifyModule", f"2FA verify module initialized for user: {user_data['email']}")
    
    def _create_ui(self):
        """Skapa UI - FAST LAYOUT UTAN SCROLL"""
        debug("TwoFAVerifyModule", "Creating 2FA verify UI WITHOUT SCROLL")
        
        # Main layout - FAST LAYOUT UTAN SCROLL
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        debug("TwoFAVerifyModule", "Main layout: margins=0, spacing=0, centered")
        
        # 2FA verify card - Fast storlek enligt GLOBAL_DESIGN.md
        debug("TwoFAVerifyModule", "Creating 2FA verify card with FIXED SIZE...")
        self._create_2fa_verify_card(main_layout)
        debug("TwoFAVerifyModule", "2FA verify card added to main layout - NO SCROLL")
        
        debug("TwoFAVerifyModule", "2FA verify UI created successfully")
    
    def _create_2fa_verify_card(self, layout):
        """Skapa 2FA verify card med global design"""
        debug("TwoFAVerifyModule", "Creating 2FA verify card")
        
        # Card frame (samma storlek som login card)
        self.card_frame = QFrame()
        # Use global card size
        self.card_frame.setFixedSize(Theme.CARD_WIDTH, Theme.CARD_HEIGHT)
        self.card_frame.setStyleSheet(Theme.create_login_card_style())
        debug("TwoFAVerifyModule", f"Card size set to: {Theme.CARD_WIDTH}x{Theme.CARD_HEIGHT}px (global)")
        
        # Card layout
        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(8)
        
        # App logga inuti kortet
        title_label = QLabel("Multi Team -C")
        subtitle_label = QLabel("P2P Team Collaboration Platform")
        Theme.setup_app_title(title_label, subtitle_label)
        card_layout.addWidget(title_label)
        card_layout.addWidget(subtitle_label)
        
        # Section header
        Theme.add_section_header(card_layout, "Two-Factor Authentication")
        
        # Användar info
        self._create_user_info(card_layout)
        
        # 2FA input sektion
        self._create_2fa_input_section(card_layout)
        
        # Backup code sektion
        self._create_backup_code_section(card_layout)
        
        # Action buttons
        self._create_action_buttons(card_layout)
        
        layout.addWidget(self.card_frame, alignment=Qt.AlignmentFlag.AlignCenter)
        debug("TwoFAVerifyModule", "2FA verify card created successfully")
    
    def _create_user_info(self, layout):
        """Skapa användar info"""
        debug("TwoFAVerifyModule", "Creating user info")
        
        user_info = QLabel(f"Signed in as: {self.user_data['email']}")
        Theme.setup_secondary_text(user_info, size=11, margin_bottom=5)
        user_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(user_info)
        
        debug("TwoFAVerifyModule", "User info created")
    
    def _create_2fa_input_section(self, layout):
        """Skapa 2FA input sektion"""
        debug("TwoFAVerifyModule", "Creating 2FA input section")
        
        # Container för 2FA input
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(2)
        
        # Instruktioner
        instructions = QLabel("Enter the 6-digit code from your authenticator app:")
        Theme.setup_secondary_text(instructions, size=11)
        input_layout.addWidget(instructions)
        
        # 2FA input
        self.twofa_input = QLineEdit()
        self.twofa_input.setPlaceholderText("000000")
        self.twofa_input.setMaxLength(6)
        Theme.setup_text_field(self.twofa_input)
        self.twofa_input.returnPressed.connect(self._verify_2fa)
        self.twofa_input.textChanged.connect(self._on_input_changed)
        input_layout.addWidget(self.twofa_input)
        
        # Auto-focus på input med timer för att säkerställa att det fungerar
        self.twofa_input.setFocus()
        
        # Sätt focus igen efter UI är laddat
        QTimer.singleShot(100, lambda: self.twofa_input.setFocus())
        
        layout.addWidget(input_container)
        debug("TwoFAVerifyModule", "2FA input section created")
    
    def _create_backup_code_section(self, layout):
        """Skapa backup code sektion"""
        debug("TwoFAVerifyModule", "Creating backup code section")
        
        # Backup code container (dold initialt)
        self.backup_container = QWidget()
        backup_layout = QVBoxLayout(self.backup_container)
        backup_layout.setContentsMargins(0, 0, 0, 0)
        backup_layout.setSpacing(2)
        
        # Backup code instruktioner
        backup_instructions = QLabel("Or enter a backup code:")
        Theme.setup_secondary_text(backup_instructions, size=11)
        backup_layout.addWidget(backup_instructions)
        
        # Backup code input
        self.backup_input = QLineEdit()
        self.backup_input.setPlaceholderText("XXXXXXXX")
        self.backup_input.setMaxLength(8)
        Theme.setup_text_field(self.backup_input)
        self.backup_input.returnPressed.connect(self._verify_backup_code)
        backup_layout.addWidget(self.backup_input)
        
        # Dölj initialt
        self.backup_container.hide()
        layout.addWidget(self.backup_container)
        
        debug("TwoFAVerifyModule", "Backup code section created")
    
    def _create_action_buttons(self, layout):
        """Skapa action buttons"""
        debug("TwoFAVerifyModule", "Creating action buttons")
        
        # Button container
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(8)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Verify button
        self.verify_btn = QPushButton("Verify")
        Theme.setup_login_button(self.verify_btn, width=100)
        self.verify_btn.clicked.connect(self._verify_2fa)
        self.verify_btn.setEnabled(False)  # Disabled tills kod är inmatad
        button_layout.addWidget(self.verify_btn)
        
        # Use backup code button
        self.backup_btn = QPushButton("Use Backup Code")
        Theme.setup_login_button(self.backup_btn, width=140)
        self.backup_btn.clicked.connect(self._toggle_backup_mode)
        button_layout.addWidget(self.backup_btn)
        
        # Back button
        back_btn = QPushButton("← Back to Login")
        Theme.setup_login_button(back_btn, width=130)
        back_btn.clicked.connect(lambda: self.back_to_login.emit())
        button_layout.addWidget(back_btn)
        
        layout.addWidget(button_container)
        debug("TwoFAVerifyModule", "Action buttons created")
    
    def _on_input_changed(self, text):
        """Hantera input ändringar"""
        # Aktivera verify button endast om 6 siffror är inmatade
        self.verify_btn.setEnabled(len(text) == 6 and text.isdigit())
    
    def _toggle_backup_mode(self):
        """Växla backup code mode"""
        debug("TwoFAVerifyModule", "Toggling backup code mode")
        
        if self.backup_container.isVisible():
            # Dölj backup mode
            self.backup_container.hide()
            self.backup_btn.setText("Use Backup Code")
            self.twofa_input.setFocus()
        else:
            # Visa backup mode
            self.backup_container.show()
            self.backup_btn.setText("Use Authenticator")
            self.backup_input.setFocus()
        
        debug("TwoFAVerifyModule", f"Backup mode toggled: {self.backup_container.isVisible()}")
    
    def _verify_2fa(self):
        """Verifiera 2FA kod"""
        debug("TwoFAVerifyModule", "Verifying 2FA code")
        
        # Kontrollera rate limiting
        if not self._check_rate_limit():
            return
        
        token = self.twofa_input.text().strip()
        
        if not token:
            show_error(self, "Error", "Please enter the 6-digit code from your authenticator app.")
            return
        
        if len(token) != 6 or not token.isdigit():
            show_error(self, "Error", "Please enter a valid 6-digit code.")
            return
        
        # Hämta användarens 2FA secret
        enabled, secret, backup_codes = self.twofa_system.get_user_2fa_status(self.user_data["id"])
        
        if not enabled or not secret:
            error("TwoFAVerifyModule", f"2FA not properly configured for user: {self.user_data['email']}")
            show_error(self, "Error", "2FA is not properly configured for your account.")
            return
        
        # Verifiera token
        if self.twofa_system.verify_token(secret, token):
            info("TwoFAVerifyModule", f"2FA verification successful for user: {self.user_data['email']}")
            self._handle_verification_success()
        else:
            self.attempt_count += 1
            self.last_attempt_time = time.time()
            
            warning("TwoFAVerifyModule", f"Invalid 2FA token for user: {self.user_data['email']} (attempt {self.attempt_count})")
            
            remaining_attempts = self.max_attempts - self.attempt_count
            if remaining_attempts > 0:
                show_error(self, "Error", f"Invalid code. {remaining_attempts} attempts remaining.")
            else:
                show_error(self, "Error", f"Too many failed attempts. Please wait {self.lockout_time // 60} minutes before trying again.")
                self._disable_inputs()
    
    def _verify_backup_code(self):
        """Verifiera backup kod"""
        debug("TwoFAVerifyModule", "Verifying backup code")
        
        # Kontrollera rate limiting
        if not self._check_rate_limit():
            return
        
        code = self.backup_input.text().strip().upper()
        
        if not code:
            show_error(self, "Error", "Please enter a backup code.")
            return
        
        if len(code) != 8:
            show_error(self, "Error", "Backup codes are 8 characters long.")
            return
        
        # Verifiera backup kod
        if self.twofa_system.verify_backup_code(self.user_data["id"], code):
            info("TwoFAVerifyModule", f"Backup code verification successful for user: {self.user_data['email']}")
            self._handle_verification_success()
        else:
            self.attempt_count += 1
            self.last_attempt_time = time.time()
            
            warning("TwoFAVerifyModule", f"Invalid backup code for user: {self.user_data['email']} (attempt {self.attempt_count})")
            
            remaining_attempts = self.max_attempts - self.attempt_count
            if remaining_attempts > 0:
                show_error(self, "Error", f"Invalid backup code. {remaining_attempts} attempts remaining.")
            else:
                show_error(self, "Error", f"Too many failed attempts. Please wait {self.lockout_time // 60} minutes before trying again.")
                self._disable_inputs()
    
    def _check_rate_limit(self):
        """Kontrollera rate limiting"""
        current_time = time.time()
        
        # Kontrollera om användaren är låst
        if self.attempt_count >= self.max_attempts:
            time_since_last_attempt = current_time - self.last_attempt_time
            if time_since_last_attempt < self.lockout_time:
                remaining_time = self.lockout_time - time_since_last_attempt
                minutes = int(remaining_time // 60)
                seconds = int(remaining_time % 60)
                show_error(self, "Rate Limited", f"Too many failed attempts. Please wait {minutes}m {seconds}s before trying again.")
                return False
            else:
                # Reset attempts efter lockout period
                self.attempt_count = 0
                self._enable_inputs()
        
        return True
    
    def _disable_inputs(self):
        """Inaktivera inputs efter för många försök"""
        debug("TwoFAVerifyModule", "Disabling inputs due to too many attempts")
        
        self.twofa_input.setEnabled(False)
        self.backup_input.setEnabled(False)
        self.verify_btn.setEnabled(False)
        self.backup_btn.setEnabled(False)
    
    def _enable_inputs(self):
        """Aktivera inputs efter lockout period"""
        debug("TwoFAVerifyModule", "Re-enabling inputs after lockout period")
        
        self.twofa_input.setEnabled(True)
        self.backup_input.setEnabled(True)
        self.backup_btn.setEnabled(True)
        # verify_btn aktiveras via _on_input_changed
    
    def _handle_verification_success(self):
        """Hantera framgångsrik verifiering"""
        debug("TwoFAVerifyModule", "Handling verification success")
        
        # Rensa inputs
        self.twofa_input.clear()
        self.backup_input.clear()
        
        # Skicka success signal med user data
        self.verification_success.emit(self.user_data)
        
        info("TwoFAVerifyModule", f"2FA verification completed successfully for user: {self.user_data['email']}")
    
    def reset_form(self):
        """Återställ formuläret"""
        debug("TwoFAVerifyModule", "Resetting form")
        
        self.twofa_input.clear()
        self.backup_input.clear()
        self.attempt_count = 0
        self.last_attempt_time = 0
        
        # Dölj backup mode
        if self.backup_container.isVisible():
            self._toggle_backup_mode()
        
        # Aktivera inputs
        self._enable_inputs()
        
        # Focus på 2FA input
        self.twofa_input.setFocus()
        
        debug("TwoFAVerifyModule", "Form reset completed")

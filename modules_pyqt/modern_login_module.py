"""
Modern PyQt6 Login Module
Helt ny login-modul enligt uppdaterad GLOBAL_DESIGN.md
Rektangulär design med rundade hörn, subtila färgövergångar och moderna hover-effekter
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QCheckBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from core.pyqt_theme import Theme
from core.debug_logger import debug, info, error
from core.auth_system import AuthSystem
from core.remember_me import RememberMe


class ModernLoginModule(QWidget):
    """
    Modern login module med helt nytt designsystem
    Följer uppdaterad GLOBAL_DESIGN.md med:
    - Rektangulär login-ruta (420x580px)
    - Rundade hörn (12px)
    - Subtila färgövergångar
    - Kompakt textfält design
    - Moderna hover-effekter
    """
    
    # Signals
    login_success = pyqtSignal(dict)  # Emits user data
    register_clicked = pyqtSignal()
    forgot_password_clicked = pyqtSignal()
    license_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.auth_system = AuthSystem()
        self.remember_me = RememberMe()
        
        debug("ModernLoginModule", "Initializing MODERN login module")
        
        self._create_ui()
        
        info("ModernLoginModule", "Modern login module initialized")
    
    def _create_ui(self):
        """Skapa modern login UI enligt uppdaterad design - UTAN SCROLL"""
        debug("ModernLoginModule", "="*60)
        debug("ModernLoginModule", "Creating MODERN login UI WITHOUT SCROLL")
        debug("ModernLoginModule", "="*60)
        
        # Main layout - FAST LAYOUT UTAN SCROLL
        debug("ModernLoginModule", "Setting up main layout - FIXED SIZE")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        debug("ModernLoginModule", "Main layout: margins=0, spacing=0, centered")
        
        # LOGIN CARD - Fast storlek enligt GLOBAL_DESIGN.md
        debug("ModernLoginModule", "Creating login card with FIXED SIZE...")
        self.login_card = self._create_login_card()
        main_layout.addWidget(self.login_card, alignment=Qt.AlignmentFlag.AlignCenter)
        debug("ModernLoginModule", "Login card added to main layout - NO SCROLL")
        
        # Koppla Enter-tangenter
        debug("ModernLoginModule", "Connecting Enter key handlers")
        self.email_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(self._handle_login)
        debug("ModernLoginModule", "Enter keys connected: Email->Password, Password->Login")
        
        # Sätt fokus på email-fält med timer för att säkerställa att det fungerar
        self.email_input.setFocus()
        debug("ModernLoginModule", "Focus set to email input field")
        
        # Sätt focus igen efter UI är laddat
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, lambda: self.email_input.setFocus())
        debug("ModernLoginModule", "Timer set for delayed focus on email input")
        
        debug("ModernLoginModule", "="*60)
        debug("ModernLoginModule", "Modern login UI created successfully")
        debug("ModernLoginModule", "="*60)
    
    def _create_login_card(self):
        """
        Skapa login card enligt uppdaterad GLOBAL_DESIGN.md
        420x580px med rundade hörn och gradient bakgrund
        """
        debug("ModernLoginModule", "")
        debug("ModernLoginModule", "[LOGIN CARD] Starting card creation")
        debug("ModernLoginModule", "[LOGIN CARD] Using GLOBAL_DESIGN.md standards")
        
        # Card frame med exakt storlek enligt GLOBAL_DESIGN.md
        debug("ModernLoginModule", "[LOGIN CARD] Creating card frame")
        card = QFrame()
        # Använd globala card-inställningar men gör kortet bredare och högre
        # Use global card size
        card.setFixedSize(Theme.CARD_WIDTH, Theme.CARD_HEIGHT)
        card.setStyleSheet(Theme.create_login_card_style())
        debug("ModernLoginModule", f"[LOGIN CARD] Card size: {Theme.CARD_WIDTH}x{Theme.CARD_HEIGHT}px (global)")
        
        # Card layout med globala kompakta inställningar
        debug("ModernLoginModule", "[LOGIN CARD] Setting up card layout")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(Theme.SPACING_LG)
        card_layout.setContentsMargins(20, 20, 20, 20)
        debug("ModernLoginModule", f"[LOGIN CARD] Layout spacing: {Theme.SPACING_LG}px")
        debug("ModernLoginModule", f"[LOGIN CARD] Layout padding: 20px")
        
        # APP TITLE & SUBTITLE
        debug("ModernLoginModule", "[LOGIN CARD] Creating title and subtitle")
        title_label = QLabel("Multi Team -C")
        subtitle_label = QLabel("P2P Team Collaboration Platform")
        Theme.setup_app_title(title_label, subtitle_label)
        
        card_layout.addWidget(title_label)
        card_layout.addSpacing(-45)  # Tight spacing mellan titel och undertitel
        card_layout.addWidget(subtitle_label)
        card_layout.addSpacing(25)  # Spacing efter subtitle
        
        # GLOBAL SECTION HEADER - Använd nya globala funktionen
        debug("ModernLoginModule", "[LOGIN CARD] Adding Sign In header with global function")
        Theme.add_section_header(card_layout, "Sign In")
        debug("ModernLoginModule", "[LOGIN CARD] Global section header added with automatic spacing")
        
        # EMAIL INPUT - Använd global styling
        debug("ModernLoginModule", "[LOGIN CARD] Creating email input")
        email_row = QHBoxLayout()
        
        email_label = QLabel("Email:")
        email_label.setFont(Theme.get_font(size=12))
        email_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; min-width: 80px;")
        email_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        email_row.addWidget(email_label)
        
        email_row.addSpacing(Theme.SPACING_LG)
        
        self.email_input = QLineEdit()
        Theme.setup_text_field(self.email_input, placeholder="Enter your email", height=26)
        email_row.addWidget(self.email_input)
        debug("ModernLoginModule", "[LOGIN CARD] Email input configured with Theme.setup_text_field()")
        
        card_layout.addLayout(email_row)
        
        # Använd global kompakt spacing
        card_layout.addSpacing(Theme.SPACING_XS)
        
        # PASSWORD INPUT - Använd global styling
        debug("ModernLoginModule", "[LOGIN CARD] Creating password input")
        password_row = QHBoxLayout()
        
        password_label = QLabel("Password:")
        password_label.setFont(Theme.get_font(size=12))
        password_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; min-width: 80px;")
        password_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        password_row.addWidget(password_label)
        
        password_row.addSpacing(Theme.SPACING_LG)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        Theme.setup_text_field(self.password_input, placeholder="Enter your password", height=26)
        password_row.addWidget(self.password_input)
        debug("ModernLoginModule", "[LOGIN CARD] Password input configured with Theme.setup_text_field()")
        
        card_layout.addLayout(password_row)
        
        # Minskat spacing för att flytta checkbox uppåt totalt 13px
        card_layout.addSpacing(-5)  # Från 8px till -5px = -13px uppåt
        
        # REMEMBER ME CHECKBOX - Ny design som passar appens färger (justerad till höger)
        debug("ModernLoginModule", "[LOGIN CARD] Creating remember me checkbox")
        remember_row = QHBoxLayout()
        remember_row.addSpacing(100)  # Moved 2px right for better alignment
        
        self.remember_checkbox = QCheckBox()
        Theme.setup_checkbox(self.remember_checkbox, "Remember me")
        self.remember_checkbox.setFont(Theme.get_font(size=14))
        remember_row.addWidget(self.remember_checkbox)
        remember_row.addStretch()
        debug("ModernLoginModule", "[LOGIN CARD] Checkbox configured with Theme.setup_checkbox()")
        
        card_layout.addLayout(remember_row)
        
        # Minimal spacing före Sign in
        card_layout.addSpacing(Theme.SPACING_XS)
        
        # DIVIDER - SIGN IN - DIVIDER (Sign in börjar exakt vid 98px som Remember me)
        signin_row = QHBoxLayout()
        signin_row.setSpacing(0)  # Ingen automatisk spacing
        
        # Empty space on left (no separator)
        signin_row.addSpacing(98)  # 88px + 10px spacing
        
        # Sign in button
        debug("ModernLoginModule", "[LOGIN CARD] Creating Sign in button")
        self.login_btn = QPushButton("Sign in")
        Theme.setup_login_button(self.login_btn)
        self.login_btn.clicked.connect(self._handle_login)
        signin_row.addWidget(self.login_btn)
        debug("ModernLoginModule", "[LOGIN CARD] Sign in button configured with Theme.setup_login_button()")
        
        # Spacing efter Sign in
        signin_row.addSpacing(Theme.SPACING_LG)
        
        # Höger divider (går hela vägen ut till höger kant)
        right_divider = QLabel("─" * 50)
        right_divider.setStyleSheet(f"color: {Theme.BORDER}; font-size: 12px;")
        signin_row.addWidget(right_divider, 1)  # Stretch factor 1 för att fylla ut
        
        card_layout.addLayout(signin_row)
        
        # Negativ spacing för att dra upp knapparna
        card_layout.addSpacing(-5)  # Negativ spacing drar upp knapparna
        
        # CREATE ACCOUNT, FORGOT PASSWORD & LICENSE ACTIVATION ROW - Centrerad
        other_btn_row = QHBoxLayout()
        other_btn_row.addStretch()  # Vänster stretch för centrering
        
        # Create new account button
        debug("ModernLoginModule", "[LOGIN CARD] Creating secondary buttons")
        self.register_btn = QPushButton("Create new account")
        Theme.setup_login_button(self.register_btn, width=140)
        self.register_btn.clicked.connect(lambda: self.register_clicked.emit())
        other_btn_row.addWidget(self.register_btn)
        debug("ModernLoginModule", "[LOGIN CARD] Create account button: 140px width")
        
        # Spacing mellan knapparna
        other_btn_row.addSpacing(Theme.SPACING_MD)
        
        # Forgot password button
        self.forgot_btn = QPushButton("Forgot password?")
        Theme.setup_login_button(self.forgot_btn, width=130)
        self.forgot_btn.clicked.connect(lambda: self.forgot_password_clicked.emit())
        other_btn_row.addWidget(self.forgot_btn)
        debug("ModernLoginModule", "[LOGIN CARD] Forgot password button: 130px width")
        
        # Spacing mellan knapparna
        other_btn_row.addSpacing(Theme.SPACING_MD)
        
        # License activation button (utan ikon)
        self.license_btn = QPushButton("License activation")
        Theme.setup_login_button(self.license_btn, width=130)
        self.license_btn.clicked.connect(lambda: self.license_clicked.emit())
        other_btn_row.addWidget(self.license_btn)
        debug("ModernLoginModule", "[LOGIN CARD] License activation button: 130px width")
        
        other_btn_row.addStretch()
        
        card_layout.addLayout(other_btn_row)
        
        debug("ModernLoginModule", "[LOGIN CARD] All buttons configured with Theme.setup_login_button()")
        debug("ModernLoginModule", "[LOGIN CARD] Card creation completed successfully")
        debug("ModernLoginModule", "")
        return card
    
    def _create_divider(self):
        """Skapa divider med 'OR' text"""
        divider_layout = QHBoxLayout()
        
        # Vänster linje
        left_line = QFrame()
        left_line.setFrameShape(QFrame.Shape.HLine)
        left_line.setStyleSheet(f"background-color: {Theme.BORDER}; max-height: 1px;")
        divider_layout.addWidget(left_line)
        
        # OR text
        or_label = QLabel("  OR  ")
        or_label.setProperty("caption", True)
        or_label.setFont(Theme.get_font(size=12))
        or_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY};")
        divider_layout.addWidget(or_label)
        
        # Höger linje
        right_line = QFrame()
        right_line.setFrameShape(QFrame.Shape.HLine)
        right_line.setStyleSheet(f"background-color: {Theme.BORDER}; max-height: 1px;")
        divider_layout.addWidget(right_line)
        
        return divider_layout
    
    def _handle_login(self):
        """Hantera inloggning"""
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        debug("ModernLoginModule", f"Login attempt: {email}")
        
        if not email or not password:
            self._show_error("Please enter both email and password")
            return
        
        # Kolla först om användaren finns men inte är verifierad
        user_data = self.auth_system.get_user_by_email(email)
        
        if user_data and not user_data.get("verified", False):
            debug("ModernLoginModule", f"User exists but not verified: {email}")
            self._handle_unverified_user(email)
            return
        
        # Autentisera
        user = self.auth_system.authenticate(email, password)
        
        if user:
            info("ModernLoginModule", f"Login successful: {email}")
            
            # Hantera remember me
            if self.remember_checkbox.isChecked():
                self.remember_me.save_credentials(email, password)
            
            # Emit success signal
            self.login_success.emit(user)
        else:
            error("ModernLoginModule", f"Login failed: {email}")
            self._show_error("Invalid email or password")
    
    def _handle_unverified_user(self, email):
        """Hantera overifierad användare"""
        debug("ModernLoginModule", f"Handling unverified user: {email}")
        
        from core.custom_dialog import show_question
        
        # Fråga om användaren vill verifiera nu
        result = show_question(
            self, 
            "Account Not Verified", 
            f"Your account ({email}) is not verified yet.\n\nWould you like to verify it now?\n\nCheck your email for the verification code."
        )
        
        if result:
            self._show_verification_dialog(email)
    
    def _show_verification_dialog(self, email):
        """Visa verifieringsdialog för befintlig användare"""
        debug("ModernLoginModule", f"Showing verification dialog for: {email}")
        
        try:
            from core.verification_dialog import show_verification_dialog
            from PyQt6.QtWidgets import QDialog
            
            result, entered_code = show_verification_dialog(self, email)
            
            if result == QDialog.DialogCode.Accepted and entered_code:
                debug("ModernLoginModule", f"User entered verification code: {entered_code}")
                
                # Verifiera koden via AuthSystem
                if self.auth_system.verify_email(email, entered_code):
                    info("ModernLoginModule", f"Email verified successfully: {email}")
                    from core.custom_dialog import show_info
                    show_info(self, "Success", "Your email has been verified!\n\nYou can now log in with your credentials.")
                else:
                    error("ModernLoginModule", f"Verification failed for: {email}")
                    self._show_error("Invalid verification code.\n\nPlease check your email and try again.")
            else:
                debug("ModernLoginModule", "User cancelled verification")
                
        except Exception as e:
            error("ModernLoginModule", f"Verification dialog error: {e}")
            self._show_error("Failed to show verification dialog.\n\nPlease try again.")
    
    def _show_error(self, message):
        """Visa felmeddelande med custom dialog"""
        from core.custom_dialog import show_error
        show_error(self, "Error", message)
    
    def set_email(self, email):
        """Sätt email i textfältet (för pre-fill efter registrering)"""
        if hasattr(self, 'email_input'):
            self.email_input.setText(email)


# Export
__all__ = ['ModernLoginModule']

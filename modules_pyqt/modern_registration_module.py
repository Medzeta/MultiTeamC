"""
Modern PyQt6 Registration Module
Registrering med email verifiering enligt GLOBAL_DESIGN.md
Namn, Företag, Email, Password
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from core.pyqt_theme import Theme
from core.debug_logger import debug, info, warning, error
from core.auth_system import AuthSystem
from core.email_service import EmailService
import re


class ModernRegistrationModule(QWidget):
    """
    Modern registration module enligt GLOBAL_DESIGN.md
    - Följer samma design som login-modulen
    - Email verifiering
    - Full debug logging
    """
    
    # Signals
    registration_complete = pyqtSignal(str)  # Emits email
    back_to_login = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.auth_system = AuthSystem()
        self.email_service = EmailService()
        
        self.verification_code = None
        self.user_email = None
        self.registration_data = {}
        
        debug("ModernRegistrationModule", "="*60)
        debug("ModernRegistrationModule", "Initializing MODERN registration module")
        debug("ModernRegistrationModule", "="*60)
        
        self._create_ui()
        
        info("ModernRegistrationModule", "Modern registration module initialized")
    
    def _create_ui(self):
        """Skapa modern registration UI - FAST LAYOUT UTAN SCROLL"""
        debug("ModernRegistrationModule", "Creating MODERN registration UI WITHOUT SCROLL")
        
        # Main layout - FAST LAYOUT UTAN SCROLL
        debug("ModernRegistrationModule", "Setting up main layout - FIXED SIZE")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        debug("ModernRegistrationModule", "Main layout: margins=0, spacing=0, centered")
        
        # REGISTRATION CARD - Fast storlek enligt GLOBAL_DESIGN.md
        debug("ModernRegistrationModule", "Creating registration card with FIXED SIZE...")
        self.registration_card = self._create_registration_card()
        main_layout.addWidget(self.registration_card, alignment=Qt.AlignmentFlag.AlignCenter)
        debug("ModernRegistrationModule", "Registration card added to main layout - NO SCROLL")
        
        debug("ModernRegistrationModule", "="*60)
        debug("ModernRegistrationModule", "Modern registration UI created successfully")
        debug("ModernRegistrationModule", "="*60)
    
    def _create_registration_card(self):
        """Skapa registration card enligt GLOBAL_DESIGN.md"""
        debug("ModernRegistrationModule", "")
        debug("ModernRegistrationModule", "[REG CARD] Starting card creation")
        debug("ModernRegistrationModule", "[REG CARD] Using GLOBAL_DESIGN.md standards")
        
        # Card frame
        debug("ModernRegistrationModule", "[REG CARD] Creating card frame")
        card = QFrame()
        # Use global card size
        card.setFixedSize(Theme.CARD_WIDTH, Theme.CARD_HEIGHT)
        card.setStyleSheet(Theme.create_login_card_style())
        debug("ModernRegistrationModule", f"[REG CARD] Card size: {Theme.CARD_WIDTH}x{Theme.CARD_HEIGHT}px (global)")
        
        # Card layout
        debug("ModernRegistrationModule", "[REG CARD] Setting up card layout")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(Theme.SPACING_LG)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        # KOMPLETT HEADER SEKVENS - Använd nya globala funktionen för 100% konsistens
        debug("ModernRegistrationModule", "[REG CARD] Creating complete header sequence")
        title_label, subtitle_label, section_label = Theme.setup_complete_header_sequence(
            card_layout, "Create Account"
        )
        debug("ModernRegistrationModule", "[REG CARD] Complete header sequence created with guaranteed consistency")
        card_layout.addSpacing(Theme.SECTION_TO_CONTENT)  # Global spacing från section header till innehåll
        
        # NAME INPUT
        debug("ModernRegistrationModule", "[REG CARD] Creating name input")
        name_row = QHBoxLayout()
        name_label = QLabel("Name:")
        name_label.setFont(Theme.get_font(size=12))
        name_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; min-width: 80px;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        name_row.addWidget(name_label)
        name_row.addSpacing(Theme.SPACING_LG)
        
        self.name_input = QLineEdit()
        Theme.setup_text_field(self.name_input, placeholder="Enter your full name", height=26)
        name_row.addWidget(self.name_input)
        card_layout.addLayout(name_row)
        card_layout.addSpacing(Theme.SPACING_XS)
        
        # COMPANY INPUT
        debug("ModernRegistrationModule", "[REG CARD] Creating company input")
        company_row = QHBoxLayout()
        company_label = QLabel("Company:")
        company_label.setFont(Theme.get_font(size=12))
        company_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; min-width: 80px;")
        company_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        company_row.addWidget(company_label)
        company_row.addSpacing(Theme.SPACING_LG)
        
        self.company_input = QLineEdit()
        Theme.setup_text_field(self.company_input, placeholder="Enter your company name", height=26)
        company_row.addWidget(self.company_input)
        card_layout.addLayout(company_row)
        card_layout.addSpacing(Theme.SPACING_XS)
        
        # EMAIL INPUT
        debug("ModernRegistrationModule", "[REG CARD] Creating email input")
        email_row = QHBoxLayout()
        email_label = QLabel("Email:")
        email_label.setFont(Theme.get_font(size=12))
        email_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; min-width: 80px;")
        email_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        email_row.addWidget(email_label)
        email_row.addSpacing(Theme.SPACING_LG)
        
        self.email_input = QLineEdit()
        Theme.setup_text_field(self.email_input, placeholder="Enter your email address", height=26)
        email_row.addWidget(self.email_input)
        card_layout.addLayout(email_row)
        card_layout.addSpacing(Theme.SPACING_XS)
        
        # PASSWORD INPUT
        debug("ModernRegistrationModule", "[REG CARD] Creating password input")
        password_row = QHBoxLayout()
        password_label = QLabel("Password:")
        password_label.setFont(Theme.get_font(size=12))
        password_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; min-width: 80px;")
        password_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        password_row.addWidget(password_label)
        password_row.addSpacing(Theme.SPACING_LG)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        Theme.setup_text_field(self.password_input, placeholder="Create a strong password", height=26)
        password_row.addWidget(self.password_input)
        card_layout.addLayout(password_row)
        card_layout.addSpacing(Theme.SPACING_XS)
        
        # CONFIRM PASSWORD INPUT
        debug("ModernRegistrationModule", "[REG CARD] Creating confirm password input")
        confirm_row = QHBoxLayout()
        confirm_label = QLabel("Confirm:")
        confirm_label.setFont(Theme.get_font(size=12))
        confirm_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; min-width: 80px;")
        confirm_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        confirm_row.addWidget(confirm_label)
        confirm_row.addSpacing(Theme.SPACING_LG)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        Theme.setup_text_field(self.confirm_password_input, placeholder="Re-enter your password", height=26)
        confirm_row.addWidget(self.confirm_password_input)
        card_layout.addLayout(confirm_row)
        card_layout.addSpacing(Theme.SPACING_XS)
        
        # BUTTONS ROW - Alla knappar på samma rad
        debug("ModernRegistrationModule", "[REG CARD] Creating buttons row")
        buttons_row = QHBoxLayout()
        buttons_row.addStretch()
        
        # Back to Login button
        self.back_btn = QPushButton("← Back to Login")
        Theme.setup_login_button(self.back_btn, width=130)
        self.back_btn.clicked.connect(lambda: self.back_to_login.emit())
        buttons_row.addWidget(self.back_btn)
        
        buttons_row.addSpacing(Theme.SPACING_MD)
        
        # Create Account button
        self.create_btn = QPushButton("Create Account")
        Theme.setup_login_button(self.create_btn, width=140)
        self.create_btn.clicked.connect(self._handle_register)
        buttons_row.addWidget(self.create_btn)
        
        buttons_row.addStretch()
        card_layout.addLayout(buttons_row)
        debug("ModernRegistrationModule", "[REG CARD] Buttons row created: Back (130px) + Create (140px)")
        
        # Connect Enter keys
        debug("ModernRegistrationModule", "[REG CARD] Connecting Enter key handlers")
        self.name_input.returnPressed.connect(self.company_input.setFocus)
        self.company_input.returnPressed.connect(self.email_input.setFocus)
        self.email_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(self.confirm_password_input.setFocus)
        self.confirm_password_input.returnPressed.connect(self._handle_register)
        
        # Set focus
        self.name_input.setFocus()
        
        debug("ModernRegistrationModule", "[REG CARD] All inputs configured with Theme.setup_text_field()")
        debug("ModernRegistrationModule", "[REG CARD] Card creation completed successfully")
        debug("ModernRegistrationModule", "")
        return card
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = re.match(pattern, email) is not None
        debug("ModernRegistrationModule", f"Email validation for {email}: {is_valid}")
        return is_valid
    
    def _handle_register(self):
        """Handle registration"""
        debug("ModernRegistrationModule", "="*60)
        debug("ModernRegistrationModule", "Create Account button clicked")
        
        # Get values
        name = self.name_input.text().strip()
        company = self.company_input.text().strip()
        email = self.email_input.text().strip().lower()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        debug("ModernRegistrationModule", f"Registration attempt - Name: {name}, Company: {company}, Email: {email}")
        
        # Validate fields
        if not name:
            warning("ModernRegistrationModule", "Registration failed: Name is empty")
            self._show_error("Please enter your full name.")
            self.name_input.setFocus()
            return
        
        if not company:
            warning("ModernRegistrationModule", "Registration failed: Company is empty")
            self._show_error("Please enter your company name.")
            self.company_input.setFocus()
            return
        
        if not email:
            warning("ModernRegistrationModule", "Registration failed: Email is empty")
            self._show_error("Please enter your email address.")
            self.email_input.setFocus()
            return
        
        if not self._validate_email(email):
            warning("ModernRegistrationModule", f"Registration failed: Invalid email format: {email}")
            self._show_error("Please enter a valid email address.")
            self.email_input.setFocus()
            return
        
        # Check SuperAdmin email
        if self.auth_system.is_superadmin(email):
            error("ModernRegistrationModule", "Cannot register with SuperAdmin email")
            self._show_error("This email is reserved for system administration.")
            return
        
        if not password:
            warning("ModernRegistrationModule", "Registration failed: Password is empty")
            self._show_error("Please enter a password.")
            self.password_input.setFocus()
            return
        
        if password != confirm_password:
            warning("ModernRegistrationModule", "Registration failed: Passwords don't match")
            self._show_error("Passwords do not match.")
            self.confirm_password_input.setFocus()
            return
        
        # Check if user exists
        existing_user = self.auth_system.get_user_by_email(email)
        if existing_user:
            warning("ModernRegistrationModule", f"Registration failed: User already exists: {email}")
            self._show_error("An account with this email already exists.\n\nPlease login or use a different email.")
            self.email_input.setFocus()
            return
        
        # Generate verification code
        debug("ModernRegistrationModule", "Generating verification code")
        self.verification_code = self.email_service.generate_verification_code()
        self.user_email = email
        
        # Send verification email
        info("ModernRegistrationModule", f"Sending verification email to: {email}")
        
        # Disable button during send
        self.create_btn.setEnabled(False)
        self.create_btn.setText("Sending email...")
        
        success = self.email_service.send_verification_email(email, name, self.verification_code)
        
        self.create_btn.setEnabled(True)
        self.create_btn.setText("Create Account")
        
        if not success:
            error("ModernRegistrationModule", "Failed to send verification email")
            self._show_error("Failed to send verification email.\n\nPlease check your internet connection and try again.")
            return
        
        # Register user (unverified)
        debug("ModernRegistrationModule", "Registering user in database")
        if self.auth_system.register_user(email, password, name, company, self.verification_code):
            info("ModernRegistrationModule", f"User registered successfully: {email}")
            
            # Store registration data for verification
            self.registration_data = {
                "name": name,
                "company": company,
                "email": email
            }
            
            # Show verification form
            self._create_verification_form()
        else:
            error("ModernRegistrationModule", "Failed to register user")
            self._show_error("Failed to create account.\n\nPlease try again later.")
        
        debug("ModernRegistrationModule", "="*60)
    
    def _create_verification_form(self):
        """Create email verification form"""
        debug("ModernRegistrationModule", "")
        debug("ModernRegistrationModule", "[VERIFY CARD] Creating verification form")
        
        # Clear and recreate card
        self.registration_card.deleteLater()
        
        # Create verification card
        card = QFrame()
        # Use global card size
        card.setFixedSize(Theme.CARD_WIDTH, Theme.CARD_HEIGHT)
        card.setStyleSheet(Theme.create_login_card_style())
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(Theme.SPACING_LG)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Multi Team -C")
        subtitle_label = QLabel("P2P Team Collaboration Platform")
        Theme.setup_app_title(title_label, subtitle_label)
        
        card_layout.addWidget(title_label)
        card_layout.addSpacing(-45)
        card_layout.addWidget(subtitle_label)
        card_layout.addSpacing(Theme.SPACING_XL + 10)
        
        # Email icon and header
        icon_label = QLabel("📧")
        icon_label.setFont(Theme.get_font(size=48))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(icon_label)
        
        verify_header = QLabel("Verify Your Email")
        verify_header.setFont(Theme.get_font(size=20, bold=True))
        verify_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        verify_header.setStyleSheet(f"color: {Theme.TEXT};")
        card_layout.addWidget(verify_header)
        
        email_info = QLabel(f"We sent a verification code to\n{self.user_email}")
        email_info.setFont(Theme.get_font(size=12))
        email_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        email_info.setStyleSheet(f"color: {Theme.TEXT_SECONDARY};")
        card_layout.addWidget(email_info)
        
        card_layout.addSpacing(Theme.SPACING_LG)
        
        # Code input
        code_label = QLabel("Enter 6-digit verification code:")
        code_label.setFont(Theme.get_font(size=12, bold=True))
        code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        code_label.setStyleSheet(f"color: {Theme.TEXT};")
        card_layout.addWidget(code_label)
        
        self.code_input = QLineEdit()
        self.code_input.setMaxLength(6)
        self.code_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        Theme.setup_text_field(self.code_input, placeholder="000000", height=40)
        self.code_input.setStyleSheet(self.code_input.styleSheet() + "font-size: 20px; font-weight: bold; letter-spacing: 5px;")
        card_layout.addWidget(self.code_input)
        
        card_layout.addSpacing(Theme.SPACING_LG)
        
        # Verify button
        verify_row = QHBoxLayout()
        verify_row.addStretch()
        
        self.verify_btn = QPushButton("Verify Email")
        Theme.setup_login_button(self.verify_btn, width=140)
        self.verify_btn.clicked.connect(self._handle_verify)
        verify_row.addWidget(self.verify_btn)
        
        verify_row.addStretch()
        card_layout.addLayout(verify_row)
        
        card_layout.addSpacing(Theme.SPACING_SM)
        
        # Resend and Back buttons
        button_row = QHBoxLayout()
        button_row.addStretch()
        
        self.resend_btn = QPushButton("Resend Code")
        Theme.setup_login_button(self.resend_btn, width=120)
        self.resend_btn.clicked.connect(self._handle_resend)
        button_row.addWidget(self.resend_btn)
        
        button_row.addSpacing(Theme.SPACING_MD)
        
        back_btn = QPushButton("← Back")
        Theme.setup_login_button(back_btn, width=80)
        back_btn.clicked.connect(self._create_ui)
        button_row.addWidget(back_btn)
        
        button_row.addStretch()
        card_layout.addLayout(button_row)
        
        # Connect Enter key
        self.code_input.returnPressed.connect(self._handle_verify)
        self.code_input.setFocus()
        
        # Replace card
        layout = self.registration_card.parent().layout()
        layout.replaceWidget(self.registration_card, card)
        self.registration_card = card
        
        debug("ModernRegistrationModule", "[VERIFY CARD] Verification form created")
        debug("ModernRegistrationModule", "")
    
    def _handle_verify(self):
        """Handle email verification"""
        debug("ModernRegistrationModule", "Verify button clicked")
        
        code = self.code_input.text().strip()
        
        debug("ModernRegistrationModule", f"Verification attempt - Code: {code}")
        
        if not code:
            warning("ModernRegistrationModule", "Verification failed: Code is empty")
            self._show_error("Please enter the verification code.")
            return
        
        if len(code) != 6 or not code.isdigit():
            warning("ModernRegistrationModule", "Verification failed: Invalid code format")
            self._show_error("Please enter a valid 6-digit code.")
            return
        
        # Verify code
        debug("ModernRegistrationModule", "Verifying code with auth system")
        if self.auth_system.verify_email(self.user_email, code):
            info("ModernRegistrationModule", f"Email verified successfully: {self.user_email}")
            
            # Send welcome email
            self.email_service.send_welcome_email(
                self.user_email,
                self.registration_data["name"]
            )
            
            # Show success and emit signal
            self._show_success(f"Your account has been created successfully.\n\nWelcome to MultiTeam, {self.registration_data['name']}!")
            self.registration_complete.emit(self.user_email)
        else:
            error("ModernRegistrationModule", "Email verification failed: Invalid code")
            self._show_error("Invalid verification code.\n\nPlease check the code and try again.")
    
    def _handle_resend(self):
        """Handle resend verification code"""
        debug("ModernRegistrationModule", "Resend code button clicked")
        
        # Generate new code
        self.verification_code = self.email_service.generate_verification_code()
        
        # Send email
        info("ModernRegistrationModule", f"Resending verification email to: {self.user_email}")
        success = self.email_service.send_verification_email(
            self.user_email,
            self.registration_data["name"],
            self.verification_code
        )
        
        if success:
            self._show_info("A new verification code has been sent to your email.")
        else:
            self._show_error("Failed to resend verification code.\n\nPlease try again.")
    
    def _show_error(self, message):
        """Visa felmeddelande med custom dialog"""
        from core.custom_dialog import show_error
        show_error(self, "Error", message)
    
    def _show_success(self, message):
        """Visa success-meddelande med custom dialog"""
        from core.custom_dialog import show_info
        show_info(self, "Success", message)
    
    def _show_info(self, message):
        """Visa info-meddelande med custom dialog"""
        from core.custom_dialog import show_info
        show_info(self, "Information", message)


# Export
__all__ = ['ModernRegistrationModule']

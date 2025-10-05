"""
Ny Modern PyQt6 Registration Module
EXAKT KOPIA av login-modulens struktur för 100% konsistent spacing
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from core.pyqt_theme import Theme
from core.debug_logger import debug, info, warning, error
from core.auth_system import AuthSystem
from core.email_service import EmailService
import re


class NewRegistrationModule(QWidget):
    """
    Ny registration module - EXAKT KOPIA av login-modulens struktur
    Garanterar 100% konsistent spacing och design
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
        
        debug("NewRegistrationModule", "="*60)
        debug("NewRegistrationModule", "Initializing NEW registration module")
        debug("NewRegistrationModule", "="*60)
        
        self._create_ui()
        
        info("NewRegistrationModule", "New registration module initialized")
    
    def _create_ui(self):
        """Skapa registration UI - FAST LAYOUT UTAN SCROLL"""
        debug("NewRegistrationModule", "="*60)
        debug("NewRegistrationModule", "Creating NEW registration UI WITHOUT SCROLL")
        debug("NewRegistrationModule", "="*60)
        
        # Main layout - FAST LAYOUT UTAN SCROLL
        debug("NewRegistrationModule", "Setting up main layout - FIXED SIZE")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        debug("NewRegistrationModule", "Main layout: margins=0, spacing=0, centered")
        
        # REGISTRATION CARD - Fast storlek enligt GLOBAL_DESIGN.md
        debug("NewRegistrationModule", "Creating registration card with FIXED SIZE...")
        self.registration_card = self._create_registration_card()
        main_layout.addWidget(self.registration_card, alignment=Qt.AlignmentFlag.AlignCenter)
        debug("NewRegistrationModule", "Registration card added to main layout - NO SCROLL")
        
        debug("NewRegistrationModule", "Connecting Enter key handlers")
        self.name_input.returnPressed.connect(self.company_input.setFocus)
        self.company_input.returnPressed.connect(self.email_input.setFocus)
        self.email_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(self.confirm_password_input.setFocus)
        self.confirm_password_input.returnPressed.connect(self._handle_registration)
        debug("NewRegistrationModule", "Enter keys connected - using _handle_registration method")
        
        # Sätt fokus på första fält
        self.name_input.setFocus()
        debug("NewRegistrationModule", "Focus set to name input field")
        
        debug("NewRegistrationModule", "="*60)
        debug("NewRegistrationModule", "NEW registration UI created successfully")
        debug("NewRegistrationModule", "="*60)
    
    def _create_registration_card(self):
        """
        Skapa registration card - EXAKT KOPIA av login card strukturen
        Bara med fler input-fält
        """
        debug("NewRegistrationModule", "")
        debug("NewRegistrationModule", "[REG CARD] Starting card creation")
        debug("NewRegistrationModule", "[REG CARD] Using EXACT login card structure")
        
        # Card frame - EXAKT som login
        debug("NewRegistrationModule", "[REG CARD] Creating card frame")
        card = QFrame()
        # Använd globala card-inställningar men gör kortet högre för fler fält
        # Use global card size
        card.setFixedSize(Theme.CARD_WIDTH, Theme.CARD_HEIGHT)
        card.setStyleSheet(Theme.create_login_card_style())
        debug("NewRegistrationModule", f"[REG CARD] Card size: {Theme.CARD_WIDTH}x{Theme.CARD_HEIGHT}px (global)")
        
        # Card layout - EXAKT som login
        debug("NewRegistrationModule", "[REG CARD] Setting up card layout")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(Theme.SPACING_LG)
        card_layout.setContentsMargins(20, 20, 20, 20)
        debug("NewRegistrationModule", f"[REG CARD] Layout spacing: {Theme.SPACING_LG}px")
        debug("NewRegistrationModule", f"[REG CARD] Layout padding: 20px")
        
        # APP TITLE & SUBTITLE - Utan section header
        debug("NewRegistrationModule", "[REG CARD] Creating title and subtitle only")
        title_label = QLabel("Multi Team -C")
        title_label.setFont(Theme.get_font(size=40, bold=True))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            color: {Theme.TEXT};
            font-size: 40px;
            font-weight: 900;
            margin: 0px;
            padding: 0px;
        """)
        card_layout.addWidget(title_label)
        
        # TIGHT SPACING MELLAN TITEL OCH UNDERTITEL
        card_layout.addSpacing(-45)  # Hårdkodat som login använder
        
        # APP SUBTITLE
        subtitle_label = QLabel("P2P Team Collaboration Platform")
        subtitle_font = Theme.get_font(size=17)
        subtitle_font.setItalic(True)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(f"""
            color: {Theme.BORDER};
            font-size: 17px;
            font-style: italic;
            font-weight: normal;
            margin: 0px;
            padding: 0px;
        """)
        subtitle_label.setWindowOpacity(0.7)
        card_layout.addWidget(subtitle_label)
        
        # Större spacing efter subtitle
        card_layout.addSpacing(25)  # Samma som login hade
        
        # GLOBAL SECTION HEADER - Använd nya globala funktionen
        debug("NewRegistrationModule", "[REG CARD] Adding Create Account header with global function")
        Theme.add_section_header(card_layout, "Create Account")
        debug("NewRegistrationModule", "[REG CARD] Global section header added with automatic spacing")
        
        # NAME INPUT - Samma struktur som login email input
        debug("NewRegistrationModule", "[REG CARD] Creating name input")
        name_row = QHBoxLayout()
        
        name_label = QLabel("Name:")
        Theme.setup_field_label(name_label, width=80)
        name_row.addWidget(name_label)
        
        name_row.addSpacing(Theme.SPACING_LG)
        
        self.name_input = QLineEdit()
        Theme.setup_text_field(self.name_input, placeholder="Enter your full name", height=26)
        name_row.addWidget(self.name_input)
        debug("NewRegistrationModule", "[REG CARD] Name input configured with Theme.setup_text_field()")
        
        card_layout.addLayout(name_row)
        
        # Använd global kompakt spacing - EXAKT som login
        card_layout.addSpacing(Theme.SPACING_XS)
        
        # COMPANY INPUT - Samma struktur
        debug("NewRegistrationModule", "[REG CARD] Creating company input")
        company_row = QHBoxLayout()
        
        company_label = QLabel("Company:")
        Theme.setup_field_label(company_label, width=80)
        company_row.addWidget(company_label)
        
        company_row.addSpacing(Theme.SPACING_LG)
        
        self.company_input = QLineEdit()
        Theme.setup_text_field(self.company_input, placeholder="Enter your company name", height=26)
        company_row.addWidget(self.company_input)
        debug("NewRegistrationModule", "[REG CARD] Company input configured with Theme.setup_text_field()")
        
        card_layout.addLayout(company_row)
        card_layout.addSpacing(Theme.SPACING_XS)
        
        # EMAIL INPUT - EXAKT som login
        debug("NewRegistrationModule", "[REG CARD] Creating email input")
        email_row = QHBoxLayout()
        
        email_label = QLabel("Email:")
        Theme.setup_field_label(email_label, width=80)
        email_row.addWidget(email_label)
        
        email_row.addSpacing(Theme.SPACING_LG)
        
        self.email_input = QLineEdit()
        Theme.setup_text_field(self.email_input, placeholder="Enter your email address", height=26)
        email_row.addWidget(self.email_input)
        debug("NewRegistrationModule", "[REG CARD] Email input configured with Theme.setup_text_field()")
        
        card_layout.addLayout(email_row)
        card_layout.addSpacing(Theme.SPACING_XS)
        
        # PASSWORD INPUT - EXAKT som login
        debug("NewRegistrationModule", "[REG CARD] Creating password input")
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
        debug("NewRegistrationModule", "[REG CARD] Password input configured with Theme.setup_text_field()")
        
        card_layout.addLayout(password_row)
        card_layout.addSpacing(Theme.SPACING_XS)
        
        # CONFIRM PASSWORD INPUT
        debug("NewRegistrationModule", "[REG CARD] Creating confirm password input")
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
        debug("NewRegistrationModule", "[REG CARD] Confirm password input configured with Theme.setup_text_field()")
        
        card_layout.addLayout(confirm_row)
        
        # Spacing före knappar (global design)
        card_layout.addSpacing(Theme.SPACING_XL)  # 15px
        
        # BUTTONS ROW - Aligned with text fields (global design)
        debug("NewRegistrationModule", "[REG CARD] Creating buttons row aligned with text fields")
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(Theme.SPACING_MD)
        buttons_row.setContentsMargins(0, 0, 0, 0)
        
        # Add spacing to align with text fields (80px label + 10px spacing + 8px adjustment)
        buttons_row.addSpacing(98)  # 80px label + Theme.SPACING_LG (10px) + 8px
        
        # Create Account button
        self.create_btn = QPushButton("Create Account")
        Theme.setup_login_button(self.create_btn, width=140)
        self.create_btn.clicked.connect(self._handle_registration)
        buttons_row.addWidget(self.create_btn)
        
        # Back to Login button (always to the right)
        self.back_btn = QPushButton("← Back to Login")
        Theme.setup_login_button(self.back_btn, width=130)
        self.back_btn.clicked.connect(lambda: self.back_to_login.emit())
        buttons_row.addWidget(self.back_btn)
        
        buttons_row.addStretch()
        card_layout.addLayout(buttons_row)
        debug("NewRegistrationModule", "[REG CARD] Buttons row created: Create (140px) + Back (130px)")
        debug("NewRegistrationModule", "[REG CARD] All inputs configured with Theme.setup_text_field()")
        debug("NewRegistrationModule", "[REG CARD] Card creation completed successfully")
        debug("NewRegistrationModule", "")
        return card
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = re.match(pattern, email) is not None
        debug("NewRegistrationModule", f"Email validation for {email}: {is_valid}")
        return is_valid
    
    def _handle_registration(self):
        """Hantera registrering"""
        debug("NewRegistrationModule", "="*60)
        debug("NewRegistrationModule", "STARTAR registreringsprocess")
        
        # Säkerhetskontroll - kolla att widgets fortfarande existerar
        try:
            if not self._widgets_exist():
                error("NewRegistrationModule", "Widgets har förstörts - avbryter registrering")
                return
        except RuntimeError as e:
            error("NewRegistrationModule", f"Widget runtime error: {e}")
            return
        
        # Validera inputs
        try:
            name = self.name_input.text().strip()
            company = self.company_input.text().strip()
            email = self.email_input.text().strip().lower()
            password = self.password_input.text()
            confirm_password = self.confirm_password_input.text()
        except RuntimeError as e:
            error("NewRegistrationModule", f"Failed to read input fields: {e}")
            return
        
        debug("NewRegistrationModule", f"Registration attempt - Name: {name}, Company: {company}, Email: {email}")
        
        # Validate fields
        if not name:
            warning("NewRegistrationModule", "Registration failed: Name is empty")
            self._show_error("Please enter your full name.")
            self.name_input.setFocus()
            return
        
        if not company:
            warning("NewRegistrationModule", "Registration failed: Company is empty")
            self._show_error("Please enter your company name.")
            self.company_input.setFocus()
            return
        
        if not email:
            warning("NewRegistrationModule", "Registration failed: Email is empty")
            self._show_error("Please enter your email address.")
            self.email_input.setFocus()
            return
        
        if not self._validate_email(email):
            warning("NewRegistrationModule", f"Registration failed: Invalid email format: {email}")
            self._show_error("Please enter a valid email address.")
            self.email_input.setFocus()
            return
        
        # Check SuperAdmin email
        if self.auth_system.is_superadmin(email):
            error("NewRegistrationModule", "Cannot register with SuperAdmin email")
            self._show_error("This email is reserved for system administration.")
            return
        
        if not password:
            warning("NewRegistrationModule", "Registration failed: Password is empty")
            self._show_error("Please enter a password.")
            self.password_input.setFocus()
            return
        
        if password != confirm_password:
            warning("NewRegistrationModule", "Registration failed: Passwords don't match")
            self._show_error("Passwords do not match.")
            self.confirm_password_input.setFocus()
            return
        
        # Check if user exists
        existing_user = self.auth_system.get_user_by_email(email)
        if existing_user:
            warning("NewRegistrationModule", f"Registration failed: User already exists: {email}")
            self._show_error("An account with this email already exists.\n\nPlease login or use a different email.")
            self.email_input.setFocus()
            return
        
        # Generate verification code
        debug("NewRegistrationModule", "Generating verification code")
        self.verification_code = self.email_service.generate_verification_code()
        self.user_email = email
        
        # Send verification email
        info("NewRegistrationModule", f"Sending verification email to: {email}")
        
        # Disable button during send (med widget-validering)
        try:
            if self._widgets_exist():
                self.create_btn.setEnabled(False)
                self.create_btn.setText("Sending email...")
        except RuntimeError:
            error("NewRegistrationModule", "Widget destroyed during email send setup")
            return
        
        success = self.email_service.send_verification_email(email, name, self.verification_code)
        
        # Re-enable button (med widget-validering)
        try:
            if self._widgets_exist():
                self.create_btn.setEnabled(True)
                self.create_btn.setText("Create Account")
        except RuntimeError:
            error("NewRegistrationModule", "Widget destroyed during email send cleanup")
            # Fortsätt ändå eftersom email kan ha skickats
        
        if not success:
            error("NewRegistrationModule", "Failed to send verification email")
            self._show_error("Failed to send verification email.\n\nPlease check your internet connection and try again.")
            return
        
        # Visa verifieringsdialog
        debug("NewRegistrationModule", "Showing verification dialog")
        from core.verification_dialog import show_verification_dialog
        from PyQt6.QtWidgets import QDialog
        
        try:
            result, entered_code = show_verification_dialog(self, email)
            
            if result == QDialog.DialogCode.Accepted:
                debug("NewRegistrationModule", f"User entered verification code: {entered_code}")
                
                # Kontrollera om koden stämmer
                if entered_code == self.verification_code:
                    debug("NewRegistrationModule", "Verification code correct - registering user")
                    
                    # Register user (verified)
                    if self.auth_system.register_user(email, password, name, company, self.verification_code):
                        info("NewRegistrationModule", f"User registered successfully: {email}")
                        
                        # Verifiera användaren i databasen
                        debug("NewRegistrationModule", "Verifying user in database")
                        if self.auth_system.verify_email(email, entered_code):
                            info("NewRegistrationModule", f"User verified successfully: {email}")
                        else:
                            warning("NewRegistrationModule", f"Failed to verify user in database: {email}")
                        
                        # Show success and emit signal
                        self._show_success(f"Account created successfully!\n\nWelcome to MultiTeam, {name}!")
                        self.registration_complete.emit(email)
                    else:
                        error("NewRegistrationModule", "Failed to register user")
                        self._show_error("Failed to create account.\n\nPlease try again later.")
                else:
                    error("NewRegistrationModule", f"Verification code mismatch: {entered_code} != {self.verification_code}")
                    self._show_error("Invalid verification code.\n\nPlease check your email and try again.")
            else:
                debug("NewRegistrationModule", "User cancelled verification")
                self._show_error("Registration cancelled.\n\nPlease try again when you're ready.")
        except Exception as e:
            error("NewRegistrationModule", f"Verification dialog error: {e}")
            self._show_error("Failed to show verification dialog.\n\nPlease try again.")
        
        debug("NewRegistrationModule", "="*60)
    
    def _show_error(self, message):
        """Visa felmeddelande med custom dialog"""
        try:
            from core.custom_dialog import show_error
            show_error(self, "Error", message)
        except RuntimeError as e:
            error("NewRegistrationModule", f"Failed to show error dialog: {e}")
    
    def _show_success(self, message):
        """Visa success-meddelande med custom dialog"""
        try:
            from core.custom_dialog import show_info
            show_info(self, "Success", message)
        except RuntimeError as e:
            error("NewRegistrationModule", f"Failed to show success dialog: {e}")
    
    def _widgets_exist(self):
        """Kontrollera att alla widgets fortfarande existerar"""
        try:
            widgets_to_check = [
                self.name_input,
                self.company_input, 
                self.email_input,
                self.password_input,
                self.confirm_password_input,
                self.create_btn
            ]
            
            for widget in widgets_to_check:
                if widget is None:
                    return False
                # Testa att komma åt widget-egenskaper
                _ = widget.isVisible()
                
            return True
        except (RuntimeError, AttributeError):
            return False


# Export
__all__ = ['NewRegistrationModule']

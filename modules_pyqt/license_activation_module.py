"""
License Activation Module - PyQt6 Version
UI for trial activation and license application with global design
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTextEdit, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from core.pyqt_theme import Theme
from core.debug_logger import debug, info, warning, error
from core.license_activation import LicenseActivation
from core.custom_dialog import show_info, show_error, show_question


class LicenseActivationModule(QWidget):
    """License activation and application UI with global design"""
    
    activation_success = pyqtSignal()
    back_to_login = pyqtSignal()
    application_clicked = pyqtSignal(str)  # Signal with machine_uid
    
    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        
        debug("LicenseActivationModule", "Initializing license activation module")
        
        self.activation_system = LicenseActivation()
        self.machine_uid = self.activation_system.get_machine_uid()
        self.current_user = current_user  # Store current user info
        
        # Extract user_id if user is logged in
        self.user_id = None
        if self.current_user:
            self.user_id = self.current_user.get('id')
            debug("LicenseActivationModule", f"User logged in: {self.current_user.get('email')} (ID: {self.user_id})")
        else:
            debug("LicenseActivationModule", "No user logged in - using anonymous mode")
        
        self._create_ui()
        self._check_and_update_trial_status()
        
        info("LicenseActivationModule", "License activation module initialized")
    
    def _create_ui(self):
        """Create UI with global design"""
        debug("LicenseActivationModule", "Creating license activation UI")
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create license activation card
        self._create_license_card(layout)
        
        debug("LicenseActivationModule", "License activation UI created successfully")
    
    def _create_license_card(self, layout):
        """Create license activation card with EXACT global design from login"""
        debug("LicenseActivationModule", "Creating license activation card with global design")
        
        # Card frame - Use global card size
        self.card_frame = QFrame()
        self.card_frame.setFixedSize(Theme.CARD_WIDTH, Theme.CARD_HEIGHT)
        self.card_frame.setStyleSheet(Theme.create_login_card_style())
        debug("LicenseActivationModule", f"Card size set to: {Theme.CARD_WIDTH}x{Theme.CARD_HEIGHT}px (global)")
        
        # Card layout - EXACT same settings as login
        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setContentsMargins(20, 20, 20, 20)  # Same as login
        card_layout.setSpacing(Theme.SPACING_LG)  # 10px - same as login
        
        # App logga inuti kortet
        title_label = QLabel("Multi Team -C")
        subtitle_label = QLabel("P2P Team Collaboration Platform")
        Theme.setup_app_title(title_label, subtitle_label)
        
        card_layout.addWidget(title_label)
        card_layout.addSpacing(-20)  # Mindre negativ spacing för att undvika överlappning
        card_layout.addWidget(subtitle_label)
        card_layout.addSpacing(25)  # Spacing efter subtitle
        
        # Section header
        Theme.add_section_header(card_layout, "License Activation")
        
        # Machine UID display
        uid_row = QHBoxLayout()
        uid_row.setSpacing(Theme.SPACING_MD)
        uid_row.setContentsMargins(0, 0, 0, 0)
        uid_label = QLabel("Machine UID:")
        uid_label.setFixedWidth(120)
        Theme.setup_secondary_text(uid_label, size=14)
        uid_row.addWidget(uid_label)
        
        self.uid_display = QLineEdit()
        self.uid_display.setText(self.machine_uid)
        self.uid_display.setReadOnly(True)
        Theme.setup_text_field(self.uid_display)
        uid_row.addWidget(self.uid_display)
        card_layout.addLayout(uid_row)
        
        # Spacing mellan textfält
        card_layout.addSpacing(Theme.SPACING_XS)  # 3px mellan fält
        
        # License key input
        key_row = QHBoxLayout()
        key_row.setSpacing(Theme.SPACING_MD)
        key_row.setContentsMargins(0, 0, 0, 0)
        key_label = QLabel("License Key:")
        key_label.setFixedWidth(120)
        Theme.setup_secondary_text(key_label, size=14)
        key_row.addWidget(key_label)
        
        self.license_key_input = QLineEdit()
        self.license_key_input.setPlaceholderText("Enter your license key")
        Theme.setup_text_field(self.license_key_input)
        key_row.addWidget(self.license_key_input)
        card_layout.addLayout(key_row)
        
        # Add spacing before activate button (3 enterslag = ~45px)
        card_layout.addSpacing(45)  # 3 enterslag
        
        # Activate button - aligned with text fields
        activate_row = QHBoxLayout()
        activate_row.setSpacing(Theme.SPACING_MD)
        activate_row.setContentsMargins(0, 0, 0, 0)
        
        # Add spacing to align with text fields (120px label + 8px spacing)
        activate_row.addSpacing(128)
        
        activate_btn = QPushButton("Activate License")
        Theme.setup_login_button(activate_btn, width=160)
        activate_btn.clicked.connect(self._activate_license)
        activate_row.addWidget(activate_btn)
        
        activate_row.addStretch()
        card_layout.addLayout(activate_row)
        
        # Stretch to push everything up
        card_layout.addStretch()
        
        card_layout.addSpacing(15)
        
        # Bottom buttons row - Trial, Apply, Back (centered with spacing)
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(Theme.SPACING_MD)
        bottom_row.setContentsMargins(0, 0, 0, 0)
        
        # Center buttons with stretch on both sides
        bottom_row.addStretch()
        
        # Start 30-Day Trial button (using new tall button function)
        self.trial_btn = QPushButton("Start 30-Day Trial")
        Theme.setup_tall_button(self.trial_btn, width=150)  # Custom width for text, double height (50px)
        self.trial_btn.clicked.connect(self._start_trial)
        bottom_row.addWidget(self.trial_btn)
        
        # Apply for License button (normal size)
        apply_btn = QPushButton("Apply for License")
        Theme.setup_login_button(apply_btn, width=140)  # Back to normal login button
        apply_btn.clicked.connect(self._apply_for_license)
        bottom_row.addWidget(apply_btn)
        
        # Back to Login button (normal size)
        back_btn = QPushButton("← Back to Login")
        Theme.setup_login_button(back_btn, width=130)  # Back to normal login button
        back_btn.clicked.connect(lambda: self.back_to_login.emit())
        bottom_row.addWidget(back_btn)
        
        bottom_row.addStretch()
        card_layout.addLayout(bottom_row)
        
        layout.addWidget(self.card_frame)
        debug("LicenseActivationModule", "License activation card created")
    
    def _check_and_update_trial_status(self):
        """Check trial status and update UI accordingly"""
        debug("LicenseActivationModule", "Checking trial status")
        
        trial_status = self.activation_system.check_trial_status(self.machine_uid)
        
        if trial_status["has_trial"]:
            if trial_status["status"] == "active":
                # Trial is active - update button text and disable it
                days_left = trial_status["days_left"]
                self.trial_btn.setText(f"Trial Active\n({days_left} days left)")  # Two lines
                self.trial_btn.setEnabled(False)
                info("LicenseActivationModule", f"Trial is active with {days_left} days remaining")
            elif trial_status["status"] == "expired":
                # Trial has expired - update button text and disable it
                self.trial_btn.setText("Trial\nExpired")  # Two lines
                self.trial_btn.setEnabled(False)
                info("LicenseActivationModule", "Trial has expired")
        else:
            # No trial activated yet - keep button as is
            info("LicenseActivationModule", "No trial activated yet")
        
        debug("LicenseActivationModule", f"Trial status check complete: {trial_status['message']}")
    
    def _activate_license(self):
        """Activate license with provided key"""
        debug("LicenseActivationModule", "Activating license")
        
        license_key = self.license_key_input.text().strip()
        
        if not license_key:
            show_error(self, "Error", "Please enter a license key")
            return
        
        # Validate and activate license
        success, message = self.activation_system.activate_license(
            license_key, 
            self.machine_uid
        )
        
        if success:
            info("LicenseActivationModule", f"License activated successfully: {license_key}")
            show_info(self, "Success", 
                     f"License activated successfully!\n\n{message}")
            self.activation_success.emit()
        else:
            error("LicenseActivationModule", f"License activation failed: {message}")
            show_error(self, "Activation Failed", message)
    
    def _start_trial(self):
        """Start trial period with user association"""
        debug("LicenseActivationModule", "Starting trial")
        
        # Show different message based on login status
        if self.current_user:
            trial_message = (f"Start a 30-day trial period for {self.current_user.get('email')}?\n\n"
                           "This trial will be associated with your account.\n"
                           "You can only use the trial once per machine.")
        else:
            trial_message = ("Start a 30-day trial period?\n\n"
                           "You can only use the trial once per machine.")
        
        # Confirm trial start
        if show_question(self, "Start Trial", trial_message):
            
            # Pass user_id to associate trial with logged-in user
            success, message = self.activation_system.activate_trial(self.machine_uid, self.user_id)
            
            if success:
                if self.current_user:
                    info("LicenseActivationModule", f"Trial activated for user: {self.current_user.get('email')}")
                else:
                    info("LicenseActivationModule", "Trial activated successfully (anonymous)")
                
                # Update UI to reflect new trial status
                self._check_and_update_trial_status()
                
                success_message = f"30-day trial activated!\n\n{message}"
                if self.current_user:
                    success_message += f"\n\nAssociated with: {self.current_user.get('email')}"
                
                show_info(self, "Trial Started", success_message)
                self.activation_success.emit()
            else:
                error("LicenseActivationModule", f"Trial activation failed: {message}")
                show_error(self, "Trial Failed", message)
    
    def _apply_for_license(self):
        """Navigate to license application"""
        debug("LicenseActivationModule", "Navigating to license application")
        self.application_clicked.emit(self.machine_uid)

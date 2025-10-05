"""
License Application Module - PyQt6 Version
Module for applying for a license with global design
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTextEdit, QFrame, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal
from core.pyqt_theme import Theme
from core.debug_logger import debug, info, error
from core.license_activation import LicenseActivation
from core.custom_dialog import show_info, show_error


class LicenseApplicationModule(QWidget):
    """License application module with global design"""
    
    application_submitted = pyqtSignal()
    back_to_license = pyqtSignal()
    
    def __init__(self, parent=None, machine_uid=None, current_user=None):
        super().__init__(parent)
        
        debug("LicenseApplicationModule", "Initializing license application dialog")
        
        self.machine_uid = machine_uid
        self.activation_system = LicenseActivation()
        self.current_user = current_user  # Store current user info
        
        # Extract user_id if user is logged in
        self.user_id = None
        if self.current_user:
            self.user_id = self.current_user.get('id')
            debug("LicenseApplicationModule", f"User logged in: {self.current_user.get('email')} (ID: {self.user_id})")
        else:
            debug("LicenseApplicationModule", "No user logged in - using anonymous mode")
        
        self._create_ui()
        self._pre_fill_user_data()  # Pre-fill form with user data if logged in
        
        info("LicenseApplicationModule", "License application module initialized")
    
    def _create_ui(self):
        """Create UI with global design"""
        debug("LicenseApplicationModule", "Creating license application UI")
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Card frame - Use global card size
        card_frame = QFrame()
        card_frame.setFixedSize(Theme.CARD_WIDTH, Theme.CARD_HEIGHT)
        card_frame.setStyleSheet(Theme.create_login_card_style())
        
        # Card layout
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(Theme.CARD_PADDING, Theme.CARD_PADDING, Theme.CARD_PADDING, Theme.CARD_PADDING)
        card_layout.setSpacing(Theme.CARD_SPACING)
        
        # App logga
        title_label = QLabel("Multi Team -C")
        subtitle_label = QLabel("P2P Team Collaboration Platform")
        Theme.setup_app_title(title_label, subtitle_label)
        card_layout.addWidget(title_label)
        card_layout.addWidget(subtitle_label)
        
        # Section header
        Theme.add_section_header(card_layout, "Apply for License")
        
        # Name field
        name_row = QHBoxLayout()
        name_row.setSpacing(Theme.SPACING_MD)
        name_row.setContentsMargins(0, 0, 0, 0)
        name_label = QLabel("Full Name:")
        name_label.setFixedWidth(120)
        Theme.setup_secondary_text(name_label, size=14)
        name_row.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your full name")
        Theme.setup_text_field(self.name_input)
        name_row.addWidget(self.name_input)
        card_layout.addLayout(name_row)
        
        # Email field
        email_row = QHBoxLayout()
        email_row.setSpacing(Theme.SPACING_MD)
        email_row.setContentsMargins(0, 0, 0, 0)
        email_label = QLabel("Email:")
        email_label.setFixedWidth(120)
        Theme.setup_secondary_text(email_label, size=14)
        email_row.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("your.email@company.com")
        Theme.setup_text_field(self.email_input)
        email_row.addWidget(self.email_input)
        card_layout.addLayout(email_row)
        
        # Company field
        company_row = QHBoxLayout()
        company_row.setSpacing(Theme.SPACING_MD)
        company_row.setContentsMargins(0, 0, 0, 0)
        company_label = QLabel("Company:")
        company_label.setFixedWidth(120)
        Theme.setup_secondary_text(company_label, size=14)
        company_row.addWidget(company_label)
        
        self.company_input = QLineEdit()
        self.company_input.setPlaceholderText("Your company name")
        Theme.setup_text_field(self.company_input)
        company_row.addWidget(self.company_input)
        card_layout.addLayout(company_row)
        
        # License type
        type_row = QHBoxLayout()
        type_row.setSpacing(Theme.SPACING_MD)
        type_row.setContentsMargins(0, 0, 0, 0)
        type_label = QLabel("License Type:")
        type_label.setFixedWidth(120)
        Theme.setup_secondary_text(type_label, size=14)
        type_row.addWidget(type_label)
        
        self.license_type_combo = QComboBox()
        self.license_type_combo.addItems([
            "Trial (1 user)",
            "Duo (2 users)",
            "Small Team (5 users)",
            "Team (10 users)",
            "Business (20 users)",
            "Corporate (50 users)",
            "Enterprise (100 users)"
        ])
        Theme.setup_text_field(self.license_type_combo)
        
        # Göm scrollbar helt - aggressiv approach
        self.license_type_combo.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.license_type_combo.view().setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Extra styling direkt på view
        self.license_type_combo.view().setStyleSheet("""
            QListView {
                background-color: #606060;
                border: none;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
                outline: none;
            }
            QListView::item {
                background-color: #606060;
                color: #ffffff;
                padding: 4px 8px;
                min-height: 30px;
            }
            QListView::item:hover {
                background-color: #6a6a6a;
            }
            QListView::item:selected {
                background-color: #707070;
            }
            QScrollBar:vertical {
                width: 0px;
            }
            QScrollBar:horizontal {
                height: 0px;
            }
        """)
        
        type_row.addWidget(self.license_type_combo)
        card_layout.addLayout(type_row)
        
        # Purpose/Notes
        purpose_row = QHBoxLayout()
        purpose_row.setSpacing(Theme.SPACING_MD)
        purpose_row.setContentsMargins(0, 0, 0, 0)
        purpose_row.setAlignment(Qt.AlignmentFlag.AlignTop)
        purpose_label = QLabel("Purpose:")
        purpose_label.setFixedWidth(120)
        Theme.setup_secondary_text(purpose_label, size=14)
        purpose_row.addWidget(purpose_label)
        
        self.purpose_input = QTextEdit()
        self.purpose_input.setPlaceholderText("Describe your use case (optional)")
        self.purpose_input.setMaximumHeight(100)
        Theme.setup_text_field(self.purpose_input)
        purpose_row.addWidget(self.purpose_input)
        card_layout.addLayout(purpose_row)
        
        # Machine UID (read-only)
        uid_row = QHBoxLayout()
        uid_row.setSpacing(Theme.SPACING_MD)
        uid_row.setContentsMargins(0, 0, 0, 0)
        uid_label = QLabel("Machine UID:")
        uid_label.setFixedWidth(120)
        Theme.setup_secondary_text(uid_label, size=14)
        uid_row.addWidget(uid_label)
        
        self.uid_display = QLineEdit()
        self.uid_display.setText(self.machine_uid or "N/A")
        self.uid_display.setReadOnly(True)
        Theme.setup_text_field(self.uid_display)
        uid_row.addWidget(self.uid_display)
        card_layout.addLayout(uid_row)
        
        # Stretch
        card_layout.addStretch()
        
        # Buttons - aligned with text fields (120px label + 8px spacing)
        button_row = QHBoxLayout()
        button_row.setSpacing(Theme.SPACING_MD)
        button_row.setContentsMargins(0, 0, 0, 0)
        
        # Add spacing to align with text fields (120px label width + 8px spacing)
        button_row.addSpacing(128)
        
        submit_btn = QPushButton("Submit Application")
        Theme.setup_login_button(submit_btn, width=180)
        submit_btn.clicked.connect(self._submit_application)
        button_row.addWidget(submit_btn)
        
        back_btn = QPushButton("← Back")
        Theme.setup_login_button(back_btn, width=100)
        back_btn.clicked.connect(lambda: self.back_to_license.emit())
        button_row.addWidget(back_btn)
        
        button_row.addStretch()
        
        card_layout.addLayout(button_row)
        
        layout.addWidget(card_frame)
        
        debug("LicenseApplicationModule", "License application UI created successfully")
    
    def _pre_fill_user_data(self):
        """Pre-fill form with logged-in user's data"""
        if not self.current_user:
            debug("LicenseApplicationModule", "No user logged in - skipping pre-fill")
            return
        
        debug("LicenseApplicationModule", f"Pre-filling form for user: {self.current_user.get('email')}")
        
        # Pre-fill name and email from user account
        if self.current_user.get('name'):
            self.name_input.setText(self.current_user.get('name'))
            debug("LicenseApplicationModule", f"Pre-filled name: {self.current_user.get('name')}")
        
        if self.current_user.get('email'):
            self.email_input.setText(self.current_user.get('email'))
            debug("LicenseApplicationModule", f"Pre-filled email: {self.current_user.get('email')}")
        
        if self.current_user.get('company'):
            self.company_input.setText(self.current_user.get('company'))
            debug("LicenseApplicationModule", f"Pre-filled company: {self.current_user.get('company')}")
        
        info("LicenseApplicationModule", "Form pre-filled with user data")
    
    def _submit_application(self):
        """Submit license application"""
        debug("LicenseApplicationModule", "Submitting license application")
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        company = self.company_input.text().strip()
        license_type = self.license_type_combo.currentText()
        purpose = self.purpose_input.toPlainText().strip()
        
        if not name:
            show_error(self, "Error", "Please enter your full name")
            return
        
        if not email or '@' not in email:
            show_error(self, "Error", "Please enter a valid email address")
            return
        
        if not company:
            show_error(self, "Error", "Please enter your company name")
            return
        
        # Submit application with user association
        success, message = self.activation_system.submit_license_application(
            name=name,
            email=email,
            company=company,
            requested_tier=license_type,
            machine_uid=self.machine_uid,
            user_id=self.user_id  # Associate with logged-in user
        )
        
        if success:
            info("LicenseApplicationModule", f"License application submitted: {email}")
            show_info(self, "Application Submitted", 
                     "Your license application has been submitted!\n\n"
                     "You will receive a response via email within 24 hours.")
            self.application_submitted.emit()
        else:
            error("LicenseApplicationModule", f"License application failed: {message}")
            show_error(self, "Submission Failed", message)

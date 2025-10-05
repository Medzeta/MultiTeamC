"""
2FA Setup Module med Global UI Design
Implementerar Google Authenticator setup med QR kod
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QFrame, 
                            QSpacerItem, QSizePolicy, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap
from core.pyqt_theme import Theme
from core.debug_logger import debug, info, error, warning
from core.twofa_system import TwoFASystem
from core.custom_dialog import show_info, show_error
import io


class TwoFASetupModule(QWidget):
    """
    2FA Setup Module med global UI design
    Implementerar Google Authenticator setup med QR kod
    """
    
    # Signals
    setup_completed = pyqtSignal()
    back_to_settings = pyqtSignal()
    
    def __init__(self, user_data):
        super().__init__()
        
        debug("TwoFASetupModule", "Initializing 2FA setup module")
        
        self.user_data = user_data
        self.twofa_system = TwoFASystem()
        self.secret = None
        self.backup_codes = []
        
        self._create_ui()
        self._generate_2fa_data()
        
        info("TwoFASetupModule", "2FA setup module initialized successfully")
    
    def _create_ui(self):
        """Skapa UI - FAST LAYOUT UTAN SCROLL"""
        debug("TwoFASetupModule", "Creating 2FA setup UI WITHOUT SCROLL")
        
        # Main layout - FAST LAYOUT UTAN SCROLL
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        debug("TwoFASetupModule", "Main layout: margins=0, spacing=0, centered")
        
        # 2FA setup card - Fast storlek enligt GLOBAL_DESIGN.md
        debug("TwoFASetupModule", "Creating 2FA setup card with FIXED SIZE...")
        self._create_2fa_setup_card(main_layout)
        debug("TwoFASetupModule", "2FA setup card added to main layout - NO SCROLL")
        
        debug("TwoFASetupModule", "2FA setup UI created successfully")
    
    def _create_2fa_setup_card(self, layout):
        """Skapa 2FA setup card med global design"""
        debug("TwoFASetupModule", "Creating 2FA setup card")
        
        # Card frame - Use global card size
        self.card_frame = QFrame()
        self.card_frame.setFixedSize(Theme.CARD_WIDTH, Theme.CARD_HEIGHT)
        self.card_frame.setStyleSheet(Theme.create_login_card_style())
        debug("TwoFASetupModule", f"Card size set to: {Theme.CARD_WIDTH}x{Theme.CARD_HEIGHT}px (global)")
        
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
        Theme.add_section_header(card_layout, "Setup Two-Factor Authentication")
        
        # Instruktioner
        self._create_instructions(card_layout)
        
        # QR kod sektion
        self._create_qr_section(card_layout)
        
        # Verifiering sektion
        self._create_verification_section(card_layout)
        
        # Backup codes sektion
        self._create_backup_codes_section(card_layout)
        
        # Action buttons
        self._create_action_buttons(card_layout)
        
        layout.addWidget(self.card_frame, alignment=Qt.AlignmentFlag.AlignCenter)
        debug("TwoFASetupModule", "2FA setup card created successfully")
    
    def _create_instructions(self, layout):
        """Skapa instruktioner"""
        debug("TwoFASetupModule", "Creating instructions")
        
        instructions = QLabel(
            "1. Install Google Authenticator or similar app on your phone\n"
            "2. Scan the QR code below with your authenticator app\n"
            "3. Enter the 6-digit code from your app to verify setup"
        )
        Theme.setup_secondary_text(instructions, size=11, margin_bottom=5)
        layout.addWidget(instructions)
        
        debug("TwoFASetupModule", "Instructions created")
    
    def _create_qr_section(self, layout):
        """Skapa QR kod sektion"""
        debug("TwoFASetupModule", "Creating QR code section")
        
        # QR kod label
        self.qr_label = QLabel("QR Code will appear here...")
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setStyleSheet(f"""
            QLabel {{
                background-color: {Theme.SURFACE};
                border: 2px solid {Theme.BORDER};
                border-radius: 8px;
                padding: 10px;
                min-height: 200px;
                max-height: 200px;
                color: {Theme.TEXT_SECONDARY};
            }}
        """)
        layout.addWidget(self.qr_label)
        
        # Manual entry info
        manual_label = QLabel("Can't scan? Enter this code manually:")
        Theme.setup_secondary_text(manual_label, size=10)
        layout.addWidget(manual_label)
        
        # Secret kod för manual entry
        self.secret_label = QLabel("Secret will appear here...")
        self.secret_label.setFont(Theme.get_font(size=10))
        self.secret_label.setStyleSheet(f"""
            QLabel {{
                background-color: {Theme.SURFACE};
                border: 1px solid {Theme.BORDER};
                border-radius: 4px;
                padding: 10px;
                color: {Theme.TEXT};
                min-height: 40px;
                font-family: monospace;
                font-size: 10px;
            }}
        """)
        self.secret_label.setWordWrap(True)
        layout.addWidget(self.secret_label)
        
        debug("TwoFASetupModule", "QR code section created")
    
    def _create_verification_section(self, layout):
        """Skapa verifiering sektion"""
        debug("TwoFASetupModule", "Creating verification section")
        
        # Container för verifiering
        verify_container = QWidget()
        verify_layout = QVBoxLayout(verify_container)
        verify_layout.setContentsMargins(0, 0, 0, 0)
        verify_layout.setSpacing(2)
        
        # Instruktioner för verifiering
        verify_instructions = QLabel("Enter the 6-digit code from your authenticator app:")
        Theme.setup_secondary_text(verify_instructions, size=11)
        verify_layout.addWidget(verify_instructions)
        
        # Verifiering input
        self.verify_input = QLineEdit()
        self.verify_input.setPlaceholderText("000000")
        self.verify_input.setMaxLength(6)
        Theme.setup_text_field(self.verify_input)
        self.verify_input.returnPressed.connect(self._verify_setup)
        verify_layout.addWidget(self.verify_input)
        
        # Auto-focus på verify input med timer
        self.verify_input.setFocus()
        QTimer.singleShot(100, lambda: self.verify_input.setFocus())
        
        layout.addWidget(verify_container)
        debug("TwoFASetupModule", "Verification section created")
    
    def _create_backup_codes_section(self, layout):
        """Skapa backup codes sektion"""
        debug("TwoFASetupModule", "Creating backup codes section")
        
        # Backup codes container (dold initialt)
        self.backup_container = QWidget()
        backup_layout = QVBoxLayout(self.backup_container)
        backup_layout.setContentsMargins(0, 0, 0, 0)
        backup_layout.setSpacing(5)
        
        # Backup codes header
        backup_header = QLabel("Backup Codes")
        backup_header.setFont(Theme.get_font(size=12, bold=True))
        backup_header.setStyleSheet(f"color: {Theme.TEXT}; margin-bottom: 5px;")
        backup_layout.addWidget(backup_header)
        
        # Backup codes info
        backup_info = QLabel("Save these backup codes in a safe place.\nYou can use them to access your account if you lose your authenticator device.\nEach code can only be used once.")
        backup_info.setWordWrap(True)
        Theme.setup_secondary_text(backup_info, size=10, margin_bottom=5)
        backup_layout.addWidget(backup_info)
        
        # Backup codes display (kopierbar)
        self.backup_codes_display = QTextEdit()
        self.backup_codes_display.setReadOnly(False)  # Tillåt kopiering
        self.backup_codes_display.setMaximumHeight(120)
        self.backup_codes_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Theme.SURFACE};
                border: 1px solid {Theme.BORDER};
                border-radius: 4px;
                padding: 8px;
                color: {Theme.TEXT};
                font-family: monospace;
                font-size: 11px;
            }}
        """)
        backup_layout.addWidget(self.backup_codes_display)
        
        # Dölj initialt
        self.backup_container.hide()
        layout.addWidget(self.backup_container)
        
        debug("TwoFASetupModule", "Backup codes section created")
    
    def _create_action_buttons(self, layout):
        """Skapa action buttons"""
        debug("TwoFASetupModule", "Creating action buttons")
        
        # Button container
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(8)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Verify button
        self.verify_btn = QPushButton("Verify & Enable 2FA")
        Theme.setup_login_button(self.verify_btn, width=160)
        self.verify_btn.clicked.connect(self._verify_setup)
        button_layout.addWidget(self.verify_btn)
        
        # Complete button (dold initialt)
        self.complete_btn = QPushButton("Complete Setup")
        Theme.setup_login_button(self.complete_btn, width=130)
        self.complete_btn.clicked.connect(self._complete_setup)
        self.complete_btn.hide()
        button_layout.addWidget(self.complete_btn)
        
        # Back button
        back_btn = QPushButton("← Back")
        Theme.setup_login_button(back_btn, width=80)
        back_btn.clicked.connect(lambda: self.back_to_settings.emit())
        button_layout.addWidget(back_btn)
        
        layout.addWidget(button_container)
        debug("TwoFASetupModule", "Action buttons created")
    
    def _generate_2fa_data(self):
        """Generera 2FA data (secret och backup codes)"""
        debug("TwoFASetupModule", "Generating 2FA data")
        
        try:
            # Generera secret
            self.secret = self.twofa_system.generate_secret()
            debug("TwoFASetupModule", f"Generated secret: {self.secret[:8]}...")
            
            # Generera backup codes
            self.backup_codes = self.twofa_system.generate_backup_codes(10)
            debug("TwoFASetupModule", f"Generated {len(self.backup_codes)} backup codes")
            
            # Uppdatera UI
            self._update_qr_code()
            self._update_secret_display()
            
            info("TwoFASetupModule", "2FA data generated successfully")
            
        except Exception as e:
            error("TwoFASetupModule", f"Error generating 2FA data: {e}")
            show_error(self, "Error", "Failed to generate 2FA data. Please try again.")
    
    def _update_qr_code(self):
        """Uppdatera QR kod display"""
        debug("TwoFASetupModule", "Updating QR code display")
        
        try:
            if not self.secret:
                return
            
            # Generera QR kod
            qr_img = self.twofa_system.generate_qr_code(self.secret, self.user_data["email"])
            
            # Spara PIL Image för email-funktionen
            self.qr_code_image = qr_img
            debug("TwoFASetupModule", "QR code PIL Image saved for email")
            
            # Konvertera till QPixmap
            buffer = io.BytesIO()
            qr_img.save(buffer, format='PNG')
            buffer.seek(0)
            
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            
            # Skala QR kod till mindre storlek så den passar bättre
            scaled_pixmap = pixmap.scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            
            # Visa QR kod
            self.qr_label.setPixmap(scaled_pixmap)
            self.qr_label.setText("")  # Ta bort placeholder text
            
            debug("TwoFASetupModule", "QR code updated successfully")
            
        except Exception as e:
            error("TwoFASetupModule", f"Error updating QR code: {e}")
            self.qr_label.setText("Error generating QR code")
    
    def _update_secret_display(self):
        """Uppdatera secret display för manual entry"""
        debug("TwoFASetupModule", "Updating secret display")
        
        if self.secret:
            # Formatera secret med mellanslag för läsbarhet
            formatted_secret = ' '.join([self.secret[i:i+4] for i in range(0, len(self.secret), 4)])
            self.secret_label.setText(formatted_secret)
            debug("TwoFASetupModule", "Secret display updated")
    
    def _verify_setup(self):
        """Verifiera 2FA setup"""
        debug("TwoFASetupModule", "Verifying 2FA setup")
        
        token = self.verify_input.text().strip()
        
        if not token:
            show_error(self, "Error", "Please enter the 6-digit code from your authenticator app.")
            return
        
        if len(token) != 6 or not token.isdigit():
            show_error(self, "Error", "Please enter a valid 6-digit code.")
            return
        
        # Verifiera token
        if self.twofa_system.verify_token(self.secret, token):
            debug("TwoFASetupModule", "2FA token verified successfully")
            
            # Aktivera 2FA för användaren
            if self.twofa_system.enable_2fa_for_user(self.user_data["id"], self.secret, self.backup_codes):
                info("TwoFASetupModule", f"2FA enabled for user: {self.user_data['email']}")
                
                # Visa backup codes
                self._show_backup_codes()
                
                # Uppdatera UI
                self.verify_btn.hide()
                self.complete_btn.show()
                self.verify_input.setEnabled(False)
                
                show_info(self, "Success", "Two-Factor Authentication has been enabled successfully!")
            else:
                error("TwoFASetupModule", "Failed to enable 2FA in database")
                show_error(self, "Error", "Failed to enable 2FA. Please try again.")
        else:
            warning("TwoFASetupModule", "Invalid 2FA token provided")
            show_error(self, "Error", "Invalid code. Please check your authenticator app and try again.")
    
    def _show_backup_codes(self):
        """Visa backup codes och dölj QR-kod"""
        debug("TwoFASetupModule", "Showing backup codes and hiding QR code")
        
        # Dölj QR-kod och manual entry sektion
        self.qr_label.hide()
        self.secret_label.hide()
        
        # Formatera backup codes i tre kolumner (endast 9 koder)
        codes_to_show = self.backup_codes[:9]  # Visa endast första 9 koderna
        
        # Skapa tre kolumner med 3 koder vardera
        col1 = [f"{i+1}. {codes_to_show[i]}" for i in range(0, 3)]
        col2 = [f"{i+1}. {codes_to_show[i]}" for i in range(3, 6)]
        col3 = [f"{i+1}. {codes_to_show[i]}" for i in range(6, 9)]
        
        # Formatera i tre kolumner
        codes_text = ""
        for i in range(3):
            line = f"{col1[i]:<20} {col2[i]:<20} {col3[i]:<20}"
            codes_text += line + "\n"
        
        self.backup_codes_display.setText(codes_text.strip())
        
        # Anpassa storleken på backup codes display till innehållet
        self.backup_codes_display.setMaximumHeight(100)  # Mindre ram som omsluter koden
        self.backup_codes_display.setMinimumHeight(100)
        
        # Ta bort automatisk textmarkering
        self.backup_codes_display.clearFocus()
        
        # Visa backup codes container
        self.backup_container.show()
        
        debug("TwoFASetupModule", "Backup codes displayed, QR code hidden")
    
    def _complete_setup(self):
        """Slutför 2FA setup och skicka email automatiskt"""
        debug("TwoFASetupModule", "Completing 2FA setup")
        
        # Skicka email automatiskt
        debug("TwoFASetupModule", "Sending backup codes email automatically")
        try:
            from core.email_service import EmailService
            
            # Generera 30 backup codes för email
            extra_codes = self.twofa_system.generate_backup_codes(count=30)
            debug("TwoFASetupModule", f"Generated 30 backup codes for email")
            
            # Skapa email service
            email_service = EmailService()
            
            # Skicka email
            if email_service.send_backup_codes_email(
                self.user_data['email'],
                self.user_data.get('name', 'User'),
                extra_codes,
                self.secret,
                self.qr_code_image
            ):
                # Spara i databas
                try:
                    from core.database_manager import db
                    import io
                    
                    img_buffer = io.BytesIO()
                    self.qr_code_image.save(img_buffer, format='PNG')
                    qr_bytes = img_buffer.getvalue()
                    
                    db.save_2fa_email_data(self.user_data['id'], qr_bytes, extra_codes)
                    debug("TwoFASetupModule", "Email data saved to database")
                except Exception as e:
                    warning("TwoFASetupModule", f"Failed to save email data: {e}")
                
                info("TwoFASetupModule", f"Backup codes email sent to: {self.user_data['email']}")
            else:
                warning("TwoFASetupModule", "Failed to send backup codes email")
                
        except Exception as e:
            error("TwoFASetupModule", f"Error sending email: {e}")
        
        show_info(self, "Setup Complete", 
                 "Two-Factor Authentication setup is complete!\n\n"
                 "Backup codes have been sent to your email.")
        
        self.setup_completed.emit()
        info("TwoFASetupModule", "2FA setup completed successfully")

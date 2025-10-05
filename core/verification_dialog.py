"""
Email Verification Dialog för Multi Team -C
Visar en dialog där användaren kan mata in sin verifieringskod
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QPainterPath, QRegion
from core.pyqt_theme import Theme
from core.debug_logger import debug


class VerificationDialog(QDialog):
    """
    Email Verification Dialog med samma design som huvudfönster
    Användaren matar in sin 6-siffriga verifieringskod
    """
    
    verification_complete = pyqtSignal(str)  # Emit när verifiering är klar
    
    def __init__(self, parent=None, email=""):
        super().__init__(parent)
        
        self.email = email
        self.verification_code = ""
        
        debug("VerificationDialog", f"Skapar verification dialog för: {email}")
        
        self._setup_dialog()
        self._create_ui()
        
    def _setup_dialog(self):
        """Konfigurera dialog-fönster"""
        debug("VerificationDialog", "Konfigurerar verification dialog")
        
        # Ta bort OS-chrome och gör fönstret frameless
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Sätt storlek
        self.setFixedSize(450, 300)
        
        # Centrera på huvudfönster
        if self.parent():
            # Hitta huvudfönstret (CustomWindow)
            main_window = self.parent()
            while main_window.parent() is not None:
                main_window = main_window.parent()
            
            # Centrera på huvudfönstret
            parent_rect = main_window.geometry()
            x = parent_rect.x() + (parent_rect.width() - 450) // 2
            y = parent_rect.y() + (parent_rect.height() - 300) // 2
            self.move(x, y)
            debug("VerificationDialog", f"Centrerad på huvudfönster: {x}, {y}")
        else:
            # Fallback: centrera på skärm
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - 450) // 2
            y = (screen.height() - 300) // 2
            self.move(x, y)
            debug("VerificationDialog", f"Centrerad på skärm: {x}, {y}")
        
        debug("VerificationDialog", f"Dialog konfigurerad: {450}x{300}px, frameless")
    
    def _create_ui(self):
        """Skapa verification UI med global design"""
        debug("VerificationDialog", "Skapar verification UI")
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Dialog frame med rundade hörn
        dialog_frame = QFrame()
        dialog_frame.setObjectName("verificationFrame")
        dialog_frame.setStyleSheet(f"""
            QFrame#verificationFrame {{
                background-color: {Theme.SURFACE};
                border: 2px solid {Theme.BORDER};
                border-radius: 15px;
            }}
        """)
        
        # Dialog layout
        dialog_layout = QVBoxLayout(dialog_frame)
        dialog_layout.setContentsMargins(30, 30, 30, 30)
        dialog_layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Email Verification")
        title_label.setFont(Theme.get_font(size=18, bold=True))
        title_label.setStyleSheet(f"color: {Theme.TEXT}; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dialog_layout.addWidget(title_label)
        
        # Message
        message_text = f"We've sent a verification code to:\n{self.email}\n\nPlease enter the 6-digit code below:"
        message_label = QLabel(message_text)
        message_label.setFont(Theme.get_font(size=12))
        message_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; line-height: 1.4;")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)
        dialog_layout.addWidget(message_label)
        
        # Code input
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Enter 6-digit code")
        self.code_input.setMaxLength(6)
        Theme.setup_text_field(self.code_input, placeholder="Enter 6-digit code", height=40)
        self.code_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.code_input.setStyleSheet(self.code_input.styleSheet() + f"""
            font-size: 16px;
            font-weight: bold;
            letter-spacing: 2px;
        """)
        self.code_input.textChanged.connect(self._on_code_changed)
        self.code_input.returnPressed.connect(self._verify_code)
        dialog_layout.addWidget(self.code_input)
        
        # Spacer
        dialog_layout.addStretch()
        
        # Buttons
        self._create_buttons(dialog_layout)
        
        main_layout.addWidget(dialog_frame)
        
        # Sätt fokus på code input
        self.code_input.setFocus()
        
        debug("VerificationDialog", "Verification UI skapad med global design")
    
    def _create_buttons(self, layout):
        """Skapa knappar"""
        debug("VerificationDialog", "Skapar verification knappar")
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Cancel knapp
        cancel_btn = QPushButton("Cancel")
        Theme.setup_login_button(cancel_btn, width=100)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addSpacing(15)
        
        # Verify knapp
        self.verify_btn = QPushButton("Verify")
        Theme.setup_login_button(self.verify_btn, width=100)
        self.verify_btn.clicked.connect(self._verify_code)
        self.verify_btn.setEnabled(False)  # Disabled tills kod är inmatad
        button_layout.addWidget(self.verify_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        debug("VerificationDialog", "Verification knappar skapade")
    
    def _on_code_changed(self, text):
        """Hantera när koden ändras"""
        # Aktivera verify-knapp endast när 6 siffror är inmatade
        self.verify_btn.setEnabled(len(text) == 6 and text.isdigit())
        
        # Auto-verify när 6 siffror är inmatade
        if len(text) == 6 and text.isdigit():
            debug("VerificationDialog", f"6-digit code entered: {text}")
    
    def _verify_code(self):
        """Verifiera koden"""
        code = self.code_input.text().strip()
        
        if len(code) != 6 or not code.isdigit():
            debug("VerificationDialog", f"Invalid code format: {code}")
            self.code_input.setStyleSheet(self.code_input.styleSheet() + f"""
                border: 2px solid #ff4444;
            """)
            return
        
        debug("VerificationDialog", f"Verifying code: {code}")
        self.verification_code = code
        self.verification_complete.emit(code)
        self.accept()
    
    def paintEvent(self, event):
        """Rita rundade hörn"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Skapa rundad path
        path = QPainterPath()
        rect = self.rect()
        path.addRoundedRect(rect.x(), rect.y(), rect.width(), rect.height(), 15, 15)
        
        # Sätt clipping region
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)
        
        super().paintEvent(event)


# Convenience funktion
def show_verification_dialog(parent, email):
    """Visa verification dialog"""
    debug("VerificationDialog", f"Visar verification dialog för: {email}")
    dialog = VerificationDialog(parent, email)
    return dialog.exec(), dialog.verification_code


# Export
__all__ = ['VerificationDialog', 'show_verification_dialog']

"""
Custom Dialog System för Multi Team -C
Ersätter Windows popups med vår globala design
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QPainterPath, QRegion
from core.pyqt_theme import Theme
from core.debug_logger import debug


class CustomDialog(QDialog):
    """
    Custom Dialog med samma design som huvudfönster
    Rundade hörn, samma färgschema, ingen OS-chrome
    """
    
    def __init__(self, parent=None, title="Dialog", message="", dialog_type="info", large=False):
        super().__init__(parent)
        
        self.dialog_type = dialog_type  # "info", "error", "warning", "question"
        self.large = large  # För login success och andra stora popups
        
        debug("CustomDialog", f"Skapar custom dialog: {title} ({dialog_type}, large={large})")
        
        self._setup_dialog(title, message)
        self._create_ui()
        
    def _setup_dialog(self, title, message):
        """Konfigurera dialog-fönster"""
        debug("CustomDialog", "Konfigurerar dialog-fönster")
        
        # Ta bort OS-chrome och gör fönstret frameless
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Sätt storlek baserat på popup-typ
        if self.large:
            # Stor storlek för login success och andra informationsrika popups
            if self.dialog_type == "question":
                # Medelstor storlek för 2FA-frågor - precis tillräckligt för texten
                self.setFixedSize(450, 280)  # Lagom storlek för 2FA-dialog
                debug("CustomDialog", "2FA question popup storlek: 450x280px")
            else:
                # Stor storlek för login success
                self.setFixedSize(650, 540)  # Stor storlek för login-information
                debug("CustomDialog", "Stor popup storlek: 650x540px")
        else:
            # Mellanstor storlek för meddelanden med mer text
            self.setFixedSize(400, 220)  # Större för att ge plats åt text med padding
            debug("CustomDialog", "Standard popup storlek: 400x220px")
        
        # Centrera på huvudfönster
        if self.parent():
            # Hitta huvudfönstret (CustomWindow)
            main_window = self.parent()
            while main_window.parent() is not None:
                main_window = main_window.parent()
            
            # Spara parent för senare centrering efter resize
            self.parent_window = main_window
        else:
            self.parent_window = None
        
        # Spara title och message
        self.title = title
        self.message = message
        
        size_text = "480x320px" if self.large else "320x180px"
        debug("CustomDialog", f"Dialog konfigurerad: {size_text}, frameless")
    
    def _create_ui(self):
        """Skapa dialog UI med global design"""
        debug("CustomDialog", "Skapar dialog UI")
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Dialog frame med rundade hörn
        dialog_frame = QFrame()
        dialog_frame.setObjectName("dialogFrame")
        dialog_frame.setStyleSheet(f"""
            QFrame#dialogFrame {{
                background-color: {Theme.SURFACE};
                border: 2px solid {Theme.BORDER};
                border-radius: 15px;
            }}
        """)
        # Dialog layout
        dialog_layout = QVBoxLayout(dialog_frame)
        dialog_layout.setContentsMargins(20, 20, 20, 20)
        dialog_layout.setSpacing(15)
        
        # Title (mindre text)
        title_label = QLabel(self.title)
        title_label.setFont(Theme.get_font(size=16, bold=True))  # 18 -> 16
        title_label.setStyleSheet(f"color: {Theme.TEXT}; margin-bottom: 8px;")  # 10px -> 8px
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dialog_layout.addWidget(title_label)
        
        # Message (mindre text)
        message_label = QLabel(self.message)
        message_label.setFont(Theme.get_font(size=10))  # 12 -> 10
        message_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; line-height: 1.3;")  # 1.4 -> 1.3
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)
        message_label.setTextFormat(Qt.TextFormat.RichText)  # Stöd för HTML
        dialog_layout.addWidget(message_label)
        dialog_layout.addStretch()
        
        # Buttons
        self._create_buttons(dialog_layout)
        
        main_layout.addWidget(dialog_frame)
        
        # Centrera dialog med fast storlek
        self._center_dialog()
        
        debug("CustomDialog", "Dialog UI skapad med global design")
    
    def _create_buttons(self, layout):
        """Skapa knappar baserat på dialog-typ"""
        debug("CustomDialog", f"Skapar knappar för {self.dialog_type}")
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        if self.dialog_type == "question":
            # Yes/No knappar
            no_btn = QPushButton("No")
            yes_btn = QPushButton("Yes")
            
            Theme.setup_login_button(no_btn, width=80)
            Theme.setup_login_button(yes_btn, width=80)
            
            no_btn.clicked.connect(self.reject)
            yes_btn.clicked.connect(self.accept)
            
            button_layout.addWidget(no_btn)
            button_layout.addSpacing(10)
            button_layout.addWidget(yes_btn)
            
        else:
            # OK knapp
            ok_btn = QPushButton("OK")
            Theme.setup_login_button(ok_btn, width=80)
            ok_btn.clicked.connect(self.accept)
            button_layout.addWidget(ok_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        debug("CustomDialog", f"Knappar skapade för {self.dialog_type}")
    
    def _center_dialog(self):
        """Centrera dialogen efter att storleken har anpassats"""
        if self.parent_window:
            # Centrera på huvudfönster
            parent_rect = self.parent_window.geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
            self.move(x, y)
            debug("CustomDialog", f"Centrerad på huvudfönster: {x}, {y} (size: {self.width()}x{self.height()})")
        else:
            # Fallback: centrera på skärm
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 2
            self.move(x, y)
            debug("CustomDialog", f"Centrerad på skärm: {x}, {y} (size: {self.width()}x{self.height()})")
    
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


# Globala convenience funktioner
def show_info(parent, title, message, large=False):
    """Visa info dialog"""
    debug("CustomDialog", f"Visar info dialog: {title} (large={large})")
    dialog = CustomDialog(parent, title, message, "info", large=large)
    return dialog.exec()

def show_error(parent, title, message, large=False):
    """Visa error dialog"""
    debug("CustomDialog", f"Visar error dialog: {title} (large={large})")
    dialog = CustomDialog(parent, title, message, "error", large=large)
    return dialog.exec()

def show_warning(parent, title, message, large=False):
    """Visa warning dialog"""
    debug("CustomDialog", f"Visar warning dialog: {title} (large={large})")
    dialog = CustomDialog(parent, title, message, "warning", large=large)
    return dialog.exec()

def show_question(parent, title, message, large=False):
    """Visa question dialog"""
    debug("CustomDialog", f"Visar question dialog: {title} (large={large})")
    dialog = CustomDialog(parent, title, message, "question", large=large)
    return dialog.exec() == QDialog.DialogCode.Accepted

def show_login_success(parent, title, message):
    """Visa login success dialog med stor storlek"""
    debug("CustomDialog", f"Visar login success dialog: {title}")
    dialog = CustomDialog(parent, title, message, "info", large=True)
    return dialog.exec()


# Export
__all__ = ['CustomDialog', 'show_info', 'show_error', 'show_warning', 'show_question', 'show_login_success']

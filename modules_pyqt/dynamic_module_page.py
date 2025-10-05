"""
Dynamic Module Page - PyQt6 Version
Automatiskt genererad undersida för varje asset-bild
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from core.pyqt_theme import Theme
from core.debug_logger import debug, info
import os


class DynamicModulePage(QWidget):
    """Dynamisk undersida för varje modul"""
    
    back_clicked = pyqtSignal()  # Signal för att gå tillbaka
    
    def __init__(self, module_id: str, module_title: str, image_name: str = None, parent=None):
        super().__init__(parent)
        
        self.module_id = module_id
        self.module_title = module_title
        self.image_name = image_name
        
        self._create_ui()
        
        info("DynamicModulePage", f"Created page for: {module_title}")
    
    def _create_ui(self):
        """Skapa undersidans UI"""
        # Transparent bakgrund
        self.setStyleSheet("""
            DynamicModulePage {
                background-color: transparent;
            }
        """)
        
        # Huvudlayout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(100, 50, 100, 50)
        main_layout.setSpacing(30)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Card container
        card = QFrame()
        card.setFixedSize(800, 600)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.SURFACE};
                border-radius: 15px;
                border: 1px solid {Theme.BORDER};
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)
        
        # Modul-bild (om tillgänglig)
        if self.image_name:
            image_label = QLabel()
            image_path = os.path.join(os.path.dirname(__file__), "..", "assets", self.image_name)
            
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, 
                                                 Qt.TransformationMode.SmoothTransformation)
                    image_label.setPixmap(scaled_pixmap)
                    image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    card_layout.addWidget(image_label)
        
        # Titel
        title_label = QLabel(self.module_title)
        title_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {Theme.TEXT};")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {Theme.BORDER}; max-height: 1px;")
        card_layout.addWidget(separator)
        
        # Coming Soon meddelande
        coming_soon = QLabel("Coming Soon")
        coming_soon.setFont(QFont("Segoe UI", 24, QFont.Weight.Normal))
        coming_soon.setStyleSheet(f"color: {Theme.TEXT_SECONDARY};")
        coming_soon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(coming_soon)
        
        # Beskrivning
        description = QLabel(f"The {self.module_title} module is currently under development.\n"
                           "Check back soon for updates!")
        description.setFont(QFont("Segoe UI", 14))
        description.setStyleSheet(f"color: {Theme.TEXT_SECONDARY};")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        card_layout.addWidget(description)
        
        card_layout.addStretch()
        
        # Tillbaka-knapp
        back_btn = QPushButton("← Back to Dashboard")
        Theme.setup_login_button(back_btn, width=200)
        back_btn.clicked.connect(self.back_clicked.emit)
        
        back_layout = QVBoxLayout()
        back_layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addLayout(back_layout)
        
        # Lägg till card i huvudlayout
        main_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch()
        
        debug("DynamicModulePage", f"UI created for {self.module_title}")

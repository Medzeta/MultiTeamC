"""
Main Dashboard Module - PyQt6 Version
Huvuddashboard med modulkort (pusselbitar) efter inloggning
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QScrollArea, QGridLayout, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon, QPainter, QPainterPath, QBrush, QColor, QPen
from core.debug_logger import debug, info, warning, error
from core.pyqt_theme import Theme
import os
import sys


class GrootCard(QFrame):
    """Kort med bild som bakgrund"""
    
    clicked = pyqtSignal(str)  # Signal med modul-ID
    
    def __init__(self, module_id: str, title: str, image_name: str = None, parent=None):
        super().__init__(parent)
        
        self.module_id = module_id
        self.title = title
        self.image_name = image_name  # Specifik bild för detta kort
        
        self._create_ui()
        self._setup_styling()
        
        debug("GrootCard", f"Created card: {title} (image: {image_name})")
    
    def _create_ui(self):
        """Skapa kortets UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Bakgrundsbild
        self.background_label = QLabel()
        
        # PyInstaller-compatible asset loading
        if self.image_name:
            # Try PyInstaller bundle path first
            if hasattr(sys, '_MEIPASS'):
                # Running in PyInstaller bundle
                image_path = os.path.join(sys._MEIPASS, "assets", self.image_name)
                debug("GrootCard", f"PyInstaller mode - Loading from bundle: {image_path}")
            else:
                # Development mode
                image_path = os.path.join(os.path.dirname(__file__), "..", "assets", self.image_name)
                debug("GrootCard", f"Development mode - Loading from source: {image_path}")
            
            debug("GrootCard", f"Loading image: {self.image_name}")
            debug("GrootCard", f"Absolute path: {os.path.abspath(image_path)}")
            debug("GrootCard", f"File exists: {os.path.exists(image_path)}")
            
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                debug("GrootCard", f"QPixmap loaded, isNull: {pixmap.isNull()}, size: {pixmap.width()}x{pixmap.height()}")
                if not pixmap.isNull():
                    # Skala bilden för att passa 300x300px kortet
                    scaled_pixmap = pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                    self.background_label.setPixmap(scaled_pixmap)
                    info("GrootCard", f"✅ Successfully loaded: {self.image_name}")
                else:
                    error("GrootCard", f"❌ QPixmap is null for: {image_path}")
                    self._show_placeholder()
            else:
                error("GrootCard", f"❌ File not found: {os.path.abspath(image_path)}")
                self._show_placeholder()
        else:
            error("GrootCard", "❌ No image_name provided!")
            self._show_placeholder()
        
        self.background_label.setScaledContents(True)
        layout.addWidget(self.background_label)
    
    def _show_placeholder(self):
        """Visa placeholder när bild saknas"""
        self.background_label.setStyleSheet("background-color: #2b2b2b; color: #888888;")
        self.background_label.setText(self.title)
        self.background_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def _setup_styling(self):
        """Sätt upp kortets styling för Groot-kort"""
        # STÖRRE KORT - 300x300px
        self.setMinimumSize(300, 300)  # Kvadratiska kort 300x300px
        self.setMaximumHeight(300)  # Fast höjd 300px
        self.setFixedHeight(300)  # Tvinga exakt 300px höjd
        
        # Expanding size policy för att fylla hela bredden
        size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setSizePolicy(size_policy)
        
        # Ta bort QFrame margins och padding
        self.setContentsMargins(0, 0, 0, 0)
        self.setFrameShape(QFrame.Shape.NoFrame)  # Ingen frame
        
        # Ta bort alla borders och ramar
        self.setStyleSheet("""
            GrootCard {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Gör kortet klickbart
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Ingen hover-effekt
    
    def mousePressEvent(self, event):
        """Hantera klick på kortet"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.module_id)
        super().mousePressEvent(event)
    
    


class MainDashboardModule(QWidget):
    """Huvuddashboard med modulkort"""
    
    module_selected = pyqtSignal(str)  # Signal när modul väljs
    
    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        
        debug("MainDashboardModule", "Initializing main dashboard")
        
        self.current_user = current_user
        self.user_id = None
        self.is_superadmin = False
        
        # Kontrollera om användaren är superadmin
        if self.current_user:
            self.user_id = self.current_user.get('id')
            username = self.current_user.get('username', '').lower()
            self.is_superadmin = username == 'superadmin'
            debug("MainDashboardModule", f"User: {self.current_user.get('email')} (SuperAdmin: {self.is_superadmin})")
        
        self._create_ui()
        self._populate_modules()
        
        # Auto-refresh timer - använder global setting
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._check_and_refresh_modules)
        self.refresh_timer.start(Theme.DASHBOARD_REFRESH_INTERVAL)
        debug("MainDashboardModule", f"Auto-refresh timer started ({Theme.DASHBOARD_REFRESH_INTERVAL}ms interval)")
        
        # Spara nuvarande antal moduler för att upptäcka ändringar
        self.last_module_count = len(self._get_available_modules())
        
        info("MainDashboardModule", "Dashboard with dynamic asset cards initialized")
    
    def _create_ui(self):
        """Skapa dashboard med kort som har Groot-bilden som bakgrund"""
        debug("MainDashboardModule", "Creating dashboard with Groot cards")
        
        # Huvudlayout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Transparent bakgrund - låt huvudfönstrets rundade hörn synas
        self.setStyleSheet("""
            MainDashboardModule {
                background-color: transparent;
            }
        """)
        
        # Ingen header - direkt till kort
        
        # Scroll area transparent - låt huvudfönstrets rundade hörn synas
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2b2b2b;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #3a3a3a;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4a4a4a;
            }
        """)
        
        # Widget för kort transparent - låt huvudfönstrets rundade hörn synas
        self.cards_widget = QWidget()
        self.cards_widget.setStyleSheet("background-color: transparent;")
        self.modules_layout = QGridLayout(self.cards_widget)
        self.modules_layout.setHorizontalSpacing(4)  # 4px horisontellt spacing
        self.modules_layout.setVerticalSpacing(4)  # 4px vertikalt spacing (samma som horisontellt)
        self.modules_layout.setContentsMargins(100, 20, 100, 20)  # 100px från sidorna, 20px från topp/botten
        
        # Stretch för 4 kolumner (300px kort)
        for i in range(4):  # 4 kolumner för 300px kort
            self.modules_layout.setColumnStretch(i, 1)  # Jämn fördelning
        
        # Sätt row stretch till 0 för att undvika extra vertikal spacing
        for i in range(3):  # 3 rader (4+4+3 kort)
            self.modules_layout.setRowStretch(i, 0)  # Ingen extra stretch vertikalt
        
        scroll_area.setWidget(self.cards_widget)
        main_layout.addWidget(scroll_area)
        
        debug("MainDashboardModule", "Dashboard UI created successfully")
    
    
    def _populate_modules(self):
        """Fyll dashboard med modulkort"""
        debug("MainDashboardModule", "Populating dashboard with modules")
        
        modules = self._get_available_modules()
        
        row = 0
        col = 0
        max_cols = 4  # 4 kort per rad (300x300px kort)
        
        for module in modules:
            # Skapa modulkort med specifik bild
            image_name = module.get('image')
            debug("MainDashboardModule", f"Creating card for {module['title']} with image: {image_name}")
            card = GrootCard(
                module_id=module['id'],
                title=module['title'],
                image_name=image_name  # Hämta image_name från modul
            )
            
            # Koppla klick-signal
            card.clicked.connect(self._handle_module_click)
            
            # Lägg till i grid
            self.modules_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Lägg till stretch för att fylla ut resterande utrymme
        self.modules_layout.setRowStretch(row + 1, 1)
        
        info("MainDashboardModule", f"Added {len(modules)} Groot cards to dashboard")
    
    def _get_available_modules(self):
        """Hämta tillgängliga moduler dynamiskt från assets-mappen"""
        modules = []
        
        # Hitta assets-mappen
        assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
        assets_dir = os.path.abspath(assets_dir)
        
        debug("MainDashboardModule", f"Scanning assets directory: {assets_dir}")
        
        # Kolla om assets-mappen finns
        if not os.path.exists(assets_dir):
            error("MainDashboardModule", f"Assets directory not found: {assets_dir}")
            return modules
        
        # Hitta alla bilderfiler - använder global setting
        image_extensions = Theme.DASHBOARD_SUPPORTED_FORMATS
        image_files = []
        
        try:
            for filename in os.listdir(assets_dir):
                file_path = os.path.join(assets_dir, filename)
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(filename)
                    if ext.lower() in image_extensions:
                        image_files.append(filename)
                        debug("MainDashboardModule", f"Found image: {filename}")
        except Exception as e:
            error("MainDashboardModule", f"Error scanning assets directory: {e}")
            return modules
        
        # Sortera bilderna alfabetiskt för konsistent ordning
        image_files.sort()
        
        # Skapa ett kort för varje bild
        for image_file in image_files:
            # Skapa ett ID från filnamnet (ta bort extension och ersätt mellanslag)
            module_id = os.path.splitext(image_file)[0].lower().replace(' ', '_')
            
            # Skapa en titel från filnamnet (ta bort extension)
            title = os.path.splitext(image_file)[0]
            
            modules.append({
                'id': module_id,
                'title': title,
                'image': image_file
            })
            
            info("MainDashboardModule", f"Created module: {title} (image: {image_file})")
        
        debug("MainDashboardModule", f"Generated {len(modules)} modules from assets directory")
        return modules
    
    def _check_and_refresh_modules(self):
        """Kolla om assets-mappen har ändrats och uppdatera kort vid behov"""
        current_modules = self._get_available_modules()
        current_count = len(current_modules)
        
        # Kolla om antalet moduler har ändrats
        if current_count != self.last_module_count:
            info("MainDashboardModule", f"Assets changed: {self.last_module_count} → {current_count} modules")
            self.last_module_count = current_count
            
            # Rensa befintliga kort
            self._clear_modules()
            
            # Lägg till nya kort
            self._populate_modules()
            
            info("MainDashboardModule", "Dashboard refreshed with new assets")
    
    def _clear_modules(self):
        """Rensa alla befintliga modulkort från grid"""
        debug("MainDashboardModule", "Clearing existing module cards")
        
        # Ta bort alla widgets från grid layout
        while self.modules_layout.count():
            item = self.modules_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        debug("MainDashboardModule", "All module cards cleared")
    
    def _handle_module_click(self, module_id: str):
        """Hantera klick på modulkort"""
        info("MainDashboardModule", f"Module clicked: {module_id}")
        
        if module_id == 'superadmin_settings' and not self.is_superadmin:
            warning("MainDashboardModule", "Non-superadmin tried to access SuperAdmin Settings")
            return
        
        # Emit signal för att huvudappen ska hantera modulväxling
        self.module_selected.emit(module_id)

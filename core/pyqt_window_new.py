"""
PyQt6 Custom Window - Helt Ny Implementation
Använder QWidget istället för QMainWindow för perfekt smooth rundade hörn
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QColor
from core.pyqt_theme import Theme
from core.debug_logger import debug, info
from core.version import get_version
import uuid
import platform


class ColoredCircleButton(QPushButton):
    """Custom button with colored circle"""
    
    def __init__(self, color):
        super().__init__()
        self.circle_color = QColor(color)
        self.setFixedSize(18, 18)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
        """)
    
    def paintEvent(self, event):
        """Paint colored circle"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw circle
        painter.setBrush(self.circle_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, 18, 18)
        
        # Hover effect
        if self.underMouse():
            painter.setBrush(QColor(255, 255, 255, 50))
            painter.drawEllipse(0, 0, 18, 18)


class CustomTitleBar(QWidget):
    """Custom titlebar with window controls"""
    
    logout_clicked = pyqtSignal()  # Signal för logout
    
    def __init__(self, parent, title="Multi Team -C"):
        super().__init__(parent)
        self.parent_window = parent
        self.title = title
        self.drag_position = QPoint()
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup titlebar UI"""
        self.setFixedHeight(75)
        self.setStyleSheet(f"""
            background-color: {Theme.BACKGROUND};
            border-top-left-radius: {Theme.RADIUS_LG}px;
            border-top-right-radius: {Theme.RADIUS_LG}px;
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 8, 0, 0)
        layout.setSpacing(0)
        
        # Vänster sida: Title + User info
        left_layout = QVBoxLayout()
        left_layout.setSpacing(1)
        left_layout.setContentsMargins(10, 8, 0, 8)
        
        # Title med version
        app_version = get_version()
        title_with_version = f"{self.title} v{app_version}"
        title_label = QLabel(title_with_version)
        title_label.setStyleSheet(f"""
            color: {Theme.TEXT};
            font-size: 14px;
            font-weight: 500;
        """)
        left_layout.addWidget(title_label)
        
        # Username + Status
        username_layout = QHBoxLayout()
        username_layout.setSpacing(5)
        
        self.username_label = QLabel("Ej inloggad")
        self.username_label.setStyleSheet(f"""
            color: {Theme.TEXT_SECONDARY};
            font-size: 11px;
        """)
        username_layout.addWidget(self.username_label)
        
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("""
            color: #888888;
            font-size: 12px;
        """)
        username_layout.addWidget(self.status_indicator)
        username_layout.addStretch()
        
        left_layout.addLayout(username_layout)
        
        # Machine UID
        self.machine_uid_label = QLabel("")
        self.machine_uid_label.setStyleSheet(f"""
            color: {Theme.TEXT_SECONDARY};
            font-size: 10px;
        """)
        left_layout.addWidget(self.machine_uid_label)
        
        # Stats
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet(f"""
            color: {Theme.TEXT_SECONDARY};
            font-size: 9px;
            padding-top: 2px;
        """)
        left_layout.addWidget(self.stats_label)
        
        self._set_machine_uid()
        
        layout.addLayout(left_layout)
        layout.addStretch()
        
        # Window controls container (vertikal layout för cirklar + logout)
        controls_container = QWidget()
        controls_container.setFixedHeight(65)  # Extra höjd för att hela knappen ska synas
        controls_main_layout = QVBoxLayout(controls_container)
        controls_main_layout.setContentsMargins(0, 0, 0, 10)  # 10px bottom margin för knappen
        controls_main_layout.setSpacing(8)  # 8px mellan cirklar och logout
        
        # Färgade cirklar (horisontell layout)
        circles_widget = QWidget()
        circles_layout = QHBoxLayout(circles_widget)
        circles_layout.setContentsMargins(0, 0, 0, 0)
        circles_layout.setSpacing(12)
        
        self.close_btn = ColoredCircleButton("#d32f2f")
        self.close_btn.clicked.connect(self.parent_window.close)
        
        self.maximize_btn = ColoredCircleButton("#f5c542")
        self.maximize_btn.clicked.connect(self._toggle_maximize)
        
        self.minimize_btn = ColoredCircleButton("#388e3c")
        self.minimize_btn.clicked.connect(self.parent_window.showMinimized)
        
        circles_layout.addWidget(self.minimize_btn)
        circles_layout.addWidget(self.maximize_btn)
        circles_layout.addWidget(self.close_btn)
        
        controls_main_layout.addWidget(circles_widget)
        
        # Logout button under cirklarna (exakt samma som globala knappar)
        self.logout_btn = QPushButton("Logga ut")
        Theme.setup_login_button(self.logout_btn, width=90)  # Exakt global funktion, 90x25px
        self.logout_btn.clicked.connect(self.logout_clicked.emit)
        controls_main_layout.addWidget(self.logout_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(controls_container, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addSpacing(10)
    
    def _toggle_maximize(self):
        """Toggle maximize/restore"""
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
        else:
            self.parent_window.showMaximized()
    
    def _set_machine_uid(self):
        """Set Machine UID"""
        node = uuid.getnode()
        mac_bytes = []
        for i in range(6):
            mac_bytes.append('{:02x}'.format((node >> (i * 8)) & 0xff))
        machine_uid = ':'.join(reversed(mac_bytes))
        computer_name = platform.node()
        
        uid_text = f"{computer_name} | UID: {machine_uid}"
        self.machine_uid_label.setText(uid_text)
        self.update_peer_stats(1, 1, 1, 1)
    
    def update_user_info(self, username=None, status="online"):
        """Update user info in titlebar"""
        if username:
            status_colors = {
                "online": "#388e3c",
                "away": "#f5c542",
                "offline": "#d32f2f"
            }
            color = status_colors.get(status, "#888888")
            self.status_indicator.setStyleSheet(f"color: {color}; font-size: 12px;")
            self.username_label.setText(username)
        else:
            self.status_indicator.setStyleSheet("color: #888888; font-size: 12px;")
            self.username_label.setText("Ej inloggad")
    
    def update_peer_stats(self, team_online, team_total, peers_online, peers_total):
        """Update peer and team statistics"""
        stats_html = f"""
        <span style='color: #b0b0b0;'>Team: </span>
        <span style='color: #388e3c; font-weight: 500;'>{team_online}</span>
        <span style='color: #b0b0b0;'> / </span>
        <span style='color: #666666;'>{team_total}</span>
        <span style='color: #b0b0b0;'> online  •  Peers: </span>
        <span style='color: #388e3c; font-weight: 500;'>{peers_online}</span>
        <span style='color: #b0b0b0;'> / </span>
        <span style='color: #666666;'>{peers_total}</span>
        <span style='color: #b0b0b0;'> online</span>
        """
        self.stats_label.setText(stats_html)
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.parent_window.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseDoubleClickEvent(self, event):
        """Handle double click to maximize"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle_maximize()


class CustomWindow(QWidget):
    """
    Helt nytt custom window - QWidget istället för QMainWindow
    Ger perfekt smooth rundade hörn med CSS border-radius
    """
    
    def __init__(self, title="MultiTeam Communication", width=1400, height=900):
        super().__init__()
        
        self.title = title
        self.window_width = width
        self.window_height = height
        
        debug("CustomWindow", "="*60)
        debug("CustomWindow", "INITIALIZING NEW CUSTOM WINDOW (QWidget approach)")
        debug("CustomWindow", "="*60)
        debug("CustomWindow", f"Title: {title}")
        debug("CustomWindow", f"Size: {width}x{height}")
        
        self._setup_window()
        self._create_ui()
        
        debug("CustomWindow", "="*60)
        debug("CustomWindow", "NEW CUSTOM WINDOW INITIALIZED SUCCESSFULLY")
        debug("CustomWindow", "="*60)
        info("CustomWindow", "NEW custom window initialized")
    
    def _setup_window(self):
        """Setup window properties"""
        debug("CustomWindow", "")
        debug("CustomWindow", "[SETUP] Setting up window properties...")
        
        # Frameless window
        debug("CustomWindow", "[SETUP] Setting window flags: FramelessWindowHint")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowSystemMenuHint
        )
        
        # Transparent background for rounded corners
        debug("CustomWindow", "[SETUP] Setting transparent background: WA_TranslucentBackground")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Fixed size
        debug("CustomWindow", f"[SETUP] Setting fixed size: {self.window_width}x{self.window_height}")
        self.setFixedSize(self.window_width, self.window_height)
        
        # Center window
        debug("CustomWindow", "[SETUP] Centering window on screen...")
        self._center_window()
        
        # Apply global stylesheet
        debug("CustomWindow", "[SETUP] Applying global stylesheet from Theme")
        self.setStyleSheet(Theme.get_stylesheet())
        
        debug("CustomWindow", f"[SETUP] Window configured successfully: {self.window_width}x{self.window_height}")
        debug("CustomWindow", "")
    
    def _center_window(self):
        """Center window on screen"""
        from PyQt6.QtGui import QScreen
        screen = QScreen.availableGeometry(self.screen())
        x = (screen.width() - self.window_width) // 2
        y = (screen.height() - self.window_height) // 2
        self.move(x, y)
    
    def _create_ui(self):
        """Create main UI structure"""
        debug("CustomWindow", "")
        debug("CustomWindow", "[UI] Creating UI structure...")
        
        # Main container with rounded corners (CSS - samma som login-kort)
        debug("CustomWindow", "[UI] Creating main_widget (QFrame) with CSS border-radius")
        self.main_widget = QFrame()
        self.main_widget.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.BACKGROUND};
                border-radius: {Theme.RADIUS_LG}px;
            }}
        """)
        debug("CustomWindow", f"[UI] Main widget styled: background={Theme.BACKGROUND}, radius={Theme.RADIUS_LG}px")
        
        # Main layout
        debug("CustomWindow", "[UI] Creating main layout (VBoxLayout)")
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        debug("CustomWindow", "[UI] Main layout: margins=0, spacing=0")
        
        # Custom titlebar
        debug("CustomWindow", "[UI] Creating custom titlebar...")
        self.titlebar = CustomTitleBar(self, self.title)
        main_layout.addWidget(self.titlebar)
        debug("CustomWindow", "[UI] Titlebar added to main layout")
        
        # Content area
        debug("CustomWindow", "[UI] Creating content area (transparent)...")
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet(f"""
            background-color: transparent;
        """)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.content_widget)
        debug("CustomWindow", "[UI] Content area added: transparent background, centered alignment")
        
        # Outer layout (för att centrera main_widget)
        debug("CustomWindow", "[UI] Creating outer layout...")
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.main_widget)
        debug("CustomWindow", "[UI] Outer layout created: margins=0")
        
        debug("CustomWindow", "[UI] UI structure created successfully")
        debug("CustomWindow", "")
    
    def set_content(self, widget):
        """Set content widget"""
        debug("CustomWindow", "")
        debug("CustomWindow", f"[CONTENT] Setting content widget: {widget.__class__.__name__}")
        
        # Clear existing content
        debug("CustomWindow", "[CONTENT] Clearing existing content...")
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                debug("CustomWindow", f"[CONTENT] Removing widget: {item.widget().__class__.__name__}")
                item.widget().deleteLater()
        
        # Add new content
        debug("CustomWindow", f"[CONTENT] Adding new widget: {widget.__class__.__name__}")
        self.content_layout.addWidget(widget)
        
        debug("CustomWindow", "[CONTENT] Content widget set successfully")
        debug("CustomWindow", "")


# Export
__all__ = ['CustomWindow']

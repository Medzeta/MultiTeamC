"""
PyQt6 Custom Borderless Window
Borderless window with rounded corners and custom titlebar
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt, QPoint, QRect, QSize
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QRegion, QPen
from core.pyqt_theme import Theme
from core.debug_logger import debug, info


class CustomTitleBar(QWidget):
    """Custom titlebar with window controls"""
    
    def __init__(self, parent, title="Multi Team -C"):
        super().__init__(parent)
        self.parent_window = parent
        self.title = title
        self.drag_position = QPoint()
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup titlebar UI"""
        self.setFixedHeight(75)  # Högre för 4 rader (med stats)
        self.setObjectName("titleBar")
        self.setStyleSheet(f"""
            #titleBar {{
                background-color: {Theme.BACKGROUND};
                border-top-left-radius: {Theme.RADIUS_LG}px;
                border-top-right-radius: {Theme.RADIUS_LG}px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 8, 0, 0)  # Lägg till 8px top margin
        layout.setSpacing(0)
        
        # Vänster sida: Title + User info (vertikal layout)
        left_layout = QVBoxLayout()
        left_layout.setSpacing(1)  # Mindre spacing
        left_layout.setContentsMargins(10, 8, 0, 8)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            color: {Theme.TEXT};
            font-size: 14px;
            font-weight: 500;
        """)
        left_layout.addWidget(title_label)
        
        # Username + Status (horizontal layout)
        username_layout = QHBoxLayout()
        username_layout.setSpacing(5)
        
        # Username label (först)
        self.username_label = QLabel("Ej inloggad")
        self.username_label.setStyleSheet(f"""
            color: {Theme.TEXT_SECONDARY};
            font-size: 11px;
        """)
        username_layout.addWidget(self.username_label)
        
        # Status indicator (cirkel) - efter användarnamn
        self.status_indicator = QLabel("●")  # Fylld cirkel
        self.status_indicator.setStyleSheet("""
            color: #888888;
            font-size: 12px;
        """)
        username_layout.addWidget(self.status_indicator)
        
        username_layout.addStretch()
        
        left_layout.addLayout(username_layout)
        
        # Machine UID label
        self.machine_uid_label = QLabel("")
        self.machine_uid_label.setStyleSheet(f"""
            color: {Theme.TEXT_SECONDARY};
            font-size: 10px;
        """)
        left_layout.addWidget(self.machine_uid_label)
        
        # Peer/Team stats (subtil)
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet(f"""
            color: {Theme.TEXT_SECONDARY};
            font-size: 9px;
            padding-top: 2px;
        """)
        left_layout.addWidget(self.stats_label)
        
        # Sätt UID direkt vid start
        self._set_machine_uid()
        
        layout.addLayout(left_layout)
        
        # Spacer
        layout.addStretch()
        
        # Spacing från höger (flyttat 2 spaces åt vänster)
        layout.addSpacing(5)
        
        # Window controls container för specifik positionering
        controls_container = QWidget()
        controls_container.setFixedHeight(20)  # Fast höjd för kontroll
        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(12)
        
        # Window controls (färgade cirklar)
        self.close_btn = self._create_control_button("", self.parent_window.close, "#d32f2f")  # Röd (X)
        self.maximize_btn = self._create_control_button("", self._toggle_maximize, "#f5c542")  # Gul (=)
        self.minimize_btn = self._create_control_button("", self.parent_window.showMinimized, "#388e3c")  # Grön (-)
        
        # Ordning: Grön, Gul, Röd (bytt plats på röd och grön)
        controls_layout.addWidget(self.minimize_btn)  # Grön först
        controls_layout.addWidget(self.maximize_btn)  # Gul i mitten
        controls_layout.addWidget(self.close_btn)  # Röd sist
        
        # Lägg till controls container med specifik top-alignment
        layout.addWidget(controls_container, alignment=Qt.AlignmentFlag.AlignTop)
        
        # Extra spacing från kanten
        layout.addSpacing(10)
    
    def _create_control_button(self, text, callback, color):
        """Create window control button with color"""
        btn = ColoredCircleButton(color)
        btn.setFixedSize(18, 18)  # 1 tredjedel större (14 -> 18)
        btn.clicked.connect(callback)
        return btn
    
    def _toggle_maximize(self):
        """Toggle maximize/restore"""
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
        else:
            self.parent_window.showMaximized()
    
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
    
    def _set_machine_uid(self):
        """Sätt Maskin UID (körs vid start)"""
        import uuid
        import platform
        
        # Windows Maskin UID (baserat på MAC-adress)
        node = uuid.getnode()
        mac_bytes = []
        for i in range(6):
            mac_bytes.append('{:02x}'.format((node >> (i * 8)) & 0xff))
        machine_uid = ':'.join(reversed(mac_bytes))
        computer_name = platform.node()
        
        # Visa UID direkt (utan dator-ikon)
        uid_text = f"{computer_name} | UID: {machine_uid}"
        self.machine_uid_label.setText(uid_text)
        
        # Initiera stats (visa egen klient som online)
        self.update_peer_stats(1, 1, 1, 1)  # 1/1 (egen klient)
    
    def update_user_info(self, username=None, status="online"):
        """Update user info in titlebar
        
        Args:
            username: Användarnamn eller None
            status: "online" (grön), "away" (gul), "offline" (röd)
        """
        if username:
            # Sätt status färg
            status_colors = {
                "online": "#388e3c",   # Grön
                "away": "#f5c542",     # Gul
                "offline": "#d32f2f"   # Röd
            }
            color = status_colors.get(status, "#888888")
            self.status_indicator.setStyleSheet(f"color: {color}; font-size: 12px;")
            
            # Visa användarnamn
            self.username_label.setText(username)
            
            # UID visas redan från _set_machine_uid(), behöver inte uppdateras
        else:
            self.status_indicator.setStyleSheet("color: #888888; font-size: 12px;")
            self.username_label.setText("Ej inloggad")
            # UID förblir synlig även när ej inloggad
    
    def update_peer_stats(self, team_online, team_total, peers_online, peers_total):
        """Update peer and team statistics
        
        Args:
            team_online: Antal online i första teamet
            team_total: Totalt antal i första teamet (alla kända klienter)
            peers_online: Antal online peers totalt
            peers_total: Totalt antal peers (alla kända klienter i nätverket)
        """
        # Färgkodad visning: grön för online, grå för totalt
        # Format: "X/Y" där X=online (grön), Y=totalt (grå)
        
        # HTML för färgkodning (enligt GLOBAL_DESIGN.md: SUCCESS=#388e3c, TEXT_DISABLED=#666666)
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


class ColoredCircleButton(QPushButton):
    """Custom button with colored circle"""
    
    def __init__(self, color):
        super().__init__()
        self.circle_color = QColor(color)
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
        painter.drawEllipse(0, 0, 18, 18)  # 1 tredjedel större
        
        # Hover effect
        if self.underMouse():
            painter.setBrush(QColor(255, 255, 255, 50))
            painter.drawEllipse(0, 0, 18, 18)


class CustomWindow(QMainWindow):
    """Custom borderless window with rounded corners"""
    
    def __init__(self, title="MultiTeam Communication", width=1400, height=900):
        super().__init__()
        
        self.title = title
        self.window_width = width
        self.window_height = height
        self.drag_position = QPoint()  # För att dra hela fönstret
        
        debug("CustomWindow", f"Initializing custom window: {title}")
        
        self._setup_window()
        self._create_ui()
        
        info("CustomWindow", "Custom window initialized")
    
    def _setup_window(self):
        """Setup window properties"""
        debug("CustomWindow", "Setting up window properties")
        
        # Borderless window
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowSystemMenuHint
        )
        
        # Transparent background for rounded corners
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Window size - FIXED to prevent resizing
        self.setFixedSize(self.window_width, self.window_height)
        
        # Center window
        self._center_window()
        
        # Apply global stylesheet
        self.setStyleSheet(Theme.get_stylesheet())
        
        debug("CustomWindow", f"Window configured: {self.window_width}x{self.window_height}")
    
    def _center_window(self):
        """Center window on screen"""
        from PyQt6.QtGui import QScreen
        screen = QScreen.availableGeometry(self.screen())
        x = (screen.width() - self.window_width) // 2
        y = (screen.height() - self.window_height) // 2
        self.move(x, y)
    
    def _create_ui(self):
        """Create main UI structure"""
        debug("CustomWindow", "Creating UI structure")
        
        # Main container widget with rounded corners
        self.main_widget = QWidget()
        self.main_widget.setObjectName("mainWidget")  # For CSS targeting
        self.main_widget.setStyleSheet(f"""
            #mainWidget {{
                background-color: {Theme.BACKGROUND};
                border-radius: {Theme.RADIUS_LG}px;
            }}
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Custom titlebar
        self.titlebar = CustomTitleBar(self, self.title)
        main_layout.addWidget(self.titlebar)
        
        # Content area
        self.content_widget = QWidget()
        self.content_widget.setObjectName("contentWidget")
        self.content_widget.setStyleSheet(f"""
            #contentWidget {{
                background-color: transparent;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                border-bottom-left-radius: {Theme.RADIUS_LG}px;
                border-bottom-right-radius: {Theme.RADIUS_LG}px;
            }}
        """)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.content_widget)
        
        # Container without margins - rundade hörn ska synas
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)  # Inga marginaler
        container_layout.addWidget(self.main_widget)
        
        self.setCentralWidget(container)
        
        debug("CustomWindow", "UI structure created")
    
    def set_content(self, widget):
        """
        Set content widget
        
        Args:
            widget: QWidget to display
        """
        debug("CustomWindow", "Setting content widget")
        
        # Clear existing content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add new content without alignment to fill entire area
        self.content_layout.addWidget(widget)
        
        debug("CustomWindow", "Content widget set")
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging entire window"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            debug("CustomWindow", "Window drag started")
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging entire window"""
        if event.buttons() == Qt.MouseButton.LeftButton and not self.drag_position.isNull():
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = QPoint()
            event.accept()
            debug("CustomWindow", "Window drag ended")
    


# Export
__all__ = ['CustomWindow']

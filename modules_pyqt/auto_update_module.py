"""
Auto-Update Module - PyQt6 Version
Hanterar automatisk uppdatering från GitHub releases
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QProgressBar, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont, QPixmap
from core.pyqt_theme import Theme
from core.debug_logger import debug, info, warning, error
from core.version import version_manager, get_version, get_version_info
import sys
import os


class UpdateWorker(QThread):
    """Worker thread för uppdateringsprocessen"""
    
    progress = pyqtSignal(str)  # Progress meddelanden
    finished = pyqtSignal(dict)  # Slutresultat
    
    def __init__(self, action: str, **kwargs):
        super().__init__()
        self.action = action
        self.kwargs = kwargs
    
    def run(self):
        try:
            if self.action == "check":
                result = version_manager.check_for_updates()
                self.finished.emit(result)
                
            elif self.action == "download":
                self.progress.emit("Downloading update...")
                result = version_manager.download_update(
                    self.kwargs["download_url"], 
                    self.kwargs["asset_name"]
                )
                self.finished.emit(result)
                
            elif self.action == "install":
                self.progress.emit("Installing update...")
                result = version_manager.install_update(self.kwargs["zip_path"])
                self.finished.emit(result)
                
        except Exception as e:
            error("UpdateWorker", f"Worker error: {e}")
            self.finished.emit({"success": False, "error": str(e)})


class AutoUpdateModule(QWidget):
    """Auto-update modul för GitHub releases"""
    
    back_clicked = pyqtSignal()
    restart_required = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.update_data = None
        self.worker = None
        
        self._create_ui()
        
        # Auto-check för uppdateringar vid start
        QTimer.singleShot(1000, self._check_for_updates)
        
        info("AutoUpdateModule", "Auto-update module initialized")
    
    def _create_ui(self):
        """Skapa uppdaterings-UI"""
        # Transparent bakgrund
        self.setStyleSheet("""
            AutoUpdateModule {
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
        card.setFixedSize(900, 700)
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
        
        # Header
        header_layout = QHBoxLayout()
        
        # Titel
        title_label = QLabel("Software Update")
        title_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {Theme.TEXT};")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Nuvarande version
        version_info = get_version_info()
        current_version_label = QLabel(f"Current: v{version_info['version']}")
        current_version_label.setFont(QFont("Segoe UI", 14))
        current_version_label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY};")
        header_layout.addWidget(current_version_label)
        
        card_layout.addLayout(header_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {Theme.BORDER}; max-height: 1px;")
        card_layout.addWidget(separator)
        
        # Status område
        self.status_label = QLabel("Checking for updates...")
        self.status_label.setFont(QFont("Segoe UI", 16))
        self.status_label.setStyleSheet(f"color: {Theme.TEXT};")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {Theme.BORDER};
                border-radius: 5px;
                text-align: center;
                background-color: {Theme.SURFACE_VARIANT};
                color: {Theme.TEXT};
            }}
            QProgressBar::chunk {{
                background-color: {Theme.PRIMARY};
                border-radius: 4px;
            }}
        """)
        card_layout.addWidget(self.progress_bar)
        
        # Update info område
        self.info_area = QTextEdit()
        self.info_area.setVisible(False)
        self.info_area.setMaximumHeight(200)
        self.info_area.setReadOnly(True)
        self.info_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Theme.SURFACE_VARIANT};
                border: 1px solid {Theme.BORDER};
                border-radius: 5px;
                padding: 10px;
                color: {Theme.TEXT};
                font-family: 'Segoe UI';
                font-size: 12px;
            }}
        """)
        card_layout.addWidget(self.info_area)
        
        card_layout.addStretch()
        
        # Knappar
        button_layout = QHBoxLayout()
        
        # Tillbaka-knapp
        self.back_btn = QPushButton("← Back to Dashboard")
        Theme.setup_login_button(self.back_btn, width=180)
        self.back_btn.clicked.connect(self.back_clicked.emit)
        button_layout.addWidget(self.back_btn)
        
        button_layout.addStretch()
        
        # Check Updates knapp
        self.check_btn = QPushButton("Check for Updates")
        Theme.setup_login_button(self.check_btn, width=150)
        self.check_btn.clicked.connect(self._check_for_updates)
        button_layout.addWidget(self.check_btn)
        
        # Download knapp
        self.download_btn = QPushButton("Download Update")
        Theme.setup_login_button(self.download_btn, width=150)
        self.download_btn.clicked.connect(self._download_update)
        self.download_btn.setVisible(False)
        button_layout.addWidget(self.download_btn)
        
        # Install knapp
        self.install_btn = QPushButton("Install & Restart")
        Theme.setup_login_button(self.install_btn, width=150)
        self.install_btn.clicked.connect(self._install_update)
        self.install_btn.setVisible(False)
        button_layout.addWidget(self.install_btn)
        
        card_layout.addLayout(button_layout)
        
        # Lägg till card i huvudlayout
        main_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch()
        
        debug("AutoUpdateModule", "UI created")
    
    def _check_for_updates(self):
        """Kolla efter uppdateringar"""
        debug("AutoUpdateModule", "Checking for updates...")
        
        self.status_label.setText("Checking for updates...")
        self.check_btn.setEnabled(False)
        self.download_btn.setVisible(False)
        self.install_btn.setVisible(False)
        self.info_area.setVisible(False)
        
        # Starta worker thread
        self.worker = UpdateWorker("check")
        self.worker.finished.connect(self._on_check_finished)
        self.worker.start()
    
    def _on_check_finished(self, result: dict):
        """Hantera resultat från update-check"""
        debug("AutoUpdateModule", f"Check result: {result}")
        
        self.check_btn.setEnabled(True)
        
        if result.get("development_mode"):
            # Development mode - inga releases än
            self.status_label.setText("Development Mode")
            self.status_label.setStyleSheet(f"color: {Theme.WARNING};")
            
            # Visa development info
            self.info_area.setVisible(True)
            info_text = f"""
<h3>Development Mode Active</h3>
<p><strong>Current Version:</strong> v{result['current_version']}</p>
<p><strong>Repository:</strong> Medzeta/MultiTeamC</p>

<h4>Status:</h4>
<p>No GitHub releases found yet. This is normal during development.</p>

<h4>Next Steps:</h4>
<p>1. Push code to GitHub repository<br>
2. Run <code>release_github.bat 0.20</code> to create first release<br>
3. Auto-update will then work normally</p>
            """.strip()
            self.info_area.setHtml(info_text)
            
        elif result.get("error"):
            self.status_label.setText(f"Error: {result['error']}")
            self.status_label.setStyleSheet(f"color: {Theme.ERROR};")
            
        elif result.get("update_available"):
            self.update_data = result
            
            self.status_label.setText(f"Update Available: v{result['latest_version']}")
            self.status_label.setStyleSheet(f"color: {Theme.SUCCESS};")
            
            # Visa update info
            self.info_area.setVisible(True)
            info_text = f"""
<h3>Version {result['latest_version']}</h3>
<p><strong>Release:</strong> {result.get('release_name', '')}</p>
<p><strong>Date:</strong> {result.get('release_date', '')[:10]}</p>

<h4>Release Notes:</h4>
<p>{result.get('release_notes', 'No release notes available.')}</p>
            """.strip()
            self.info_area.setHtml(info_text)
            
            # Visa download-knapp
            self.download_btn.setVisible(True)
            
        else:
            self.status_label.setText("You have the latest version!")
            self.status_label.setStyleSheet(f"color: {Theme.SUCCESS};")
    
    def _download_update(self):
        """Ladda ner uppdatering"""
        if not self.update_data or not self.update_data.get("download_url"):
            warning("AutoUpdateModule", "No download URL available")
            return
        
        debug("AutoUpdateModule", "Starting download...")
        
        self.status_label.setText("Downloading update...")
        self.download_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Starta download worker
        self.worker = UpdateWorker(
            "download",
            download_url=self.update_data["download_url"],
            asset_name=self.update_data["asset_name"]
        )
        self.worker.progress.connect(self.status_label.setText)
        self.worker.finished.connect(self._on_download_finished)
        self.worker.start()
    
    def _on_download_finished(self, result: dict):
        """Hantera download-resultat"""
        debug("AutoUpdateModule", f"Download result: {result}")
        
        self.progress_bar.setVisible(False)
        self.download_btn.setEnabled(True)
        
        if result.get("success"):
            self.status_label.setText("Download completed!")
            self.status_label.setStyleSheet(f"color: {Theme.SUCCESS};")
            
            # Spara zip path för installation
            self.update_data["zip_path"] = result["zip_path"]
            
            # Visa install-knapp
            self.install_btn.setVisible(True)
            self.download_btn.setVisible(False)
            
        else:
            self.status_label.setText(f"Download failed: {result.get('error', 'Unknown error')}")
            self.status_label.setStyleSheet(f"color: {Theme.ERROR};")
    
    def _install_update(self):
        """Installera uppdatering"""
        if not self.update_data or not self.update_data.get("zip_path"):
            warning("AutoUpdateModule", "No ZIP file to install")
            return
        
        debug("AutoUpdateModule", "Starting installation...")
        
        self.status_label.setText("Installing update...")
        self.install_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        # Starta install worker
        self.worker = UpdateWorker(
            "install",
            zip_path=self.update_data["zip_path"]
        )
        self.worker.progress.connect(self.status_label.setText)
        self.worker.finished.connect(self._on_install_finished)
        self.worker.start()
    
    def _on_install_finished(self, result: dict):
        """Hantera install-resultat"""
        debug("AutoUpdateModule", f"Install result: {result}")
        
        self.progress_bar.setVisible(False)
        self.install_btn.setEnabled(True)
        
        if result.get("success"):
            self.status_label.setText("Update installed successfully!")
            self.status_label.setStyleSheet(f"color: {Theme.SUCCESS};")
            
            if result.get("restart_required"):
                # Visa restart-meddelande
                self.info_area.setVisible(True)
                self.info_area.setHtml("""
                <h3>Restart Required</h3>
                <p>The update has been installed successfully. Please restart the application to use the new version.</p>
                <p><strong>Click 'Restart Now' to restart automatically.</strong></p>
                """)
                
                # Ändra install-knapp till restart-knapp
                self.install_btn.setText("Restart Now")
                self.install_btn.clicked.disconnect()
                self.install_btn.clicked.connect(self._restart_application)
        else:
            self.status_label.setText(f"Installation failed: {result.get('error', 'Unknown error')}")
            self.status_label.setStyleSheet(f"color: {Theme.ERROR};")
    
    def _restart_application(self):
        """Starta om applikationen"""
        info("AutoUpdateModule", "Restarting application...")
        
        self.restart_required.emit()
        
        # Starta om via subprocess och avsluta nuvarande process
        try:
            import subprocess
            subprocess.Popen([sys.executable] + sys.argv)
            sys.exit(0)
        except Exception as e:
            error("AutoUpdateModule", f"Restart failed: {e}")
            self.status_label.setText("Please restart manually")

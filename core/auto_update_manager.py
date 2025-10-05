"""
Auto Update Manager för Multi Team -C
Hanterar automatisk uppdatering vid app start och varje timme
"""

import sys
import os
import subprocess
from pathlib import Path
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, QThread
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton, QHBoxLayout
from core.debug_logger import debug, info, warning, error
from core.version import version_manager, get_version
from core.pyqt_theme import Theme
from core.custom_dialog import show_info, show_error

class UpdateDownloader(QThread):
    """Thread för att ladda ner uppdateringar"""
    progress = pyqtSignal(int)  # Progress 0-100
    status = pyqtSignal(str)    # Status meddelande
    finished = pyqtSignal(bool, str)  # Success, message
    
    def __init__(self, download_url, asset_name):
        super().__init__()
        self.download_url = download_url
        self.asset_name = asset_name
    
    def run(self):
        """Ladda ner uppdatering"""
        try:
            self.status.emit("Checking for updates...")
            self.progress.emit(10)
            
            # Ladda ner uppdatering
            self.status.emit("Downloading update...")
            self.progress.emit(30)
            
            result = version_manager.download_update(self.download_url, self.asset_name)
            
            if result.get('success'):
                self.progress.emit(70)
                self.status.emit("Preparing update...")
                
                # Installera uppdatering (skapar update script)
                install_result = version_manager.install_update(result['exe_path'])
                
                if install_result.get('success'):
                    self.progress.emit(100)
                    self.status.emit("Update ready!")
                    # Skicka update_script path också
                    self.finished.emit(True, install_result.get('update_script', ''))
                else:
                    self.finished.emit(False, f"Installation failed: {install_result.get('error', 'Unknown error')}")
            else:
                self.finished.emit(False, f"Download failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            error("UpdateDownloader", f"Update failed: {e}")
            self.finished.emit(False, f"Update failed: {str(e)}")

class UpdateDialog(QDialog):
    """Tvingande uppdateringsdialog med progress bar"""
    
    def __init__(self, parent=None, latest_version="", current_version=""):
        super().__init__(parent)
        self.latest_version = latest_version
        self.current_version = current_version
        self.downloader = None
        self.update_data = None
        
        self.setWindowTitle("MultiTeam Update Required")
        self.setModal(True)
        self.setFixedSize(500, 300)
        
        # Frameless window med rundade hörn
        from PyQt6.QtCore import Qt
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self._setup_ui()
        self._apply_styling()
    
    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Update Required")
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                color: {Theme.TEXT};
                margin-bottom: 10px;
            }}
        """)
        layout.addWidget(title_label)
        
        # Version info
        version_info = QLabel(f"""
        <div style='color: {Theme.TEXT_SECONDARY}; line-height: 1.4;'>
        A new version of MultiTeam is available and must be installed.<br><br>
        <b>Current version:</b> v{self.current_version}<br>
        <b>Latest version:</b> v{self.latest_version}<br><br>
        The update will download and install automatically.
        </div>
        """)
        version_info.setWordWrap(True)
        layout.addWidget(version_info)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {Theme.BORDER};
                border-radius: 8px;
                text-align: center;
                background-color: {Theme.SURFACE};
                color: {Theme.TEXT};
                font-size: 12px;
                height: 25px;
            }}
            QProgressBar::chunk {{
                background-color: {Theme.PRIMARY};
                border-radius: 6px;
            }}
        """)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Preparing update...")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT_SECONDARY};
                font-size: 12px;
                margin-top: 5px;
            }}
        """)
        layout.addWidget(self.status_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # OK button (initially disabled)
        self.ok_button = QPushButton("Restart Application")
        Theme.setup_login_button(self.ok_button, width=150)
        self.ok_button.setEnabled(False)
        self.ok_button.clicked.connect(self._restart_application)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
    
    def _apply_styling(self):
        """Apply dialog styling"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.SURFACE};
                border-radius: 15px;
                border: 1px solid {Theme.BORDER};
            }}
        """)
    
    def start_update(self, update_data):
        """Starta uppdateringsprocessen"""
        self.update_data = update_data
        
        download_url = update_data.get('download_url')
        asset_name = update_data.get('asset_name')
        
        if not download_url or not asset_name:
            self._update_failed("No download URL available")
            return
        
        # Starta downloader thread
        self.downloader = UpdateDownloader(download_url, asset_name)
        self.downloader.progress.connect(self.progress_bar.setValue)
        self.downloader.status.connect(self.status_label.setText)
        self.downloader.finished.connect(self._update_finished)
        self.downloader.start()
    
    def _update_finished(self, success, update_script_path):
        """Uppdatering klar"""
        if success:
            self.update_script_path = update_script_path
            self.status_label.setText("Update ready! Click to restart.")
            self.ok_button.setEnabled(True)
            self.ok_button.setText("Restart Now")
        else:
            self._update_failed(update_script_path)  # message är i update_script_path vid fel
    
    def _update_failed(self, message):
        """Uppdatering misslyckades"""
        self.status_label.setText(f"Update failed: {message}")
        self.ok_button.setEnabled(True)
        self.ok_button.setText("Close Application")
        self.update_script_path = None
    
    def _restart_application(self):
        """Starta om applikationen med update script"""
        info("AutoUpdateManager", "Restarting application after update")
        
        # Stäng dialog
        self.accept()
        
        # Om vi har ett update script, kör det
        if hasattr(self, 'update_script_path') and self.update_script_path:
            info("AutoUpdateManager", f"Running update script: {self.update_script_path}")
            # Kör update script som startar om appen efter uppdatering
            subprocess.Popen(['cmd', '/c', self.update_script_path], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            # Stäng nuvarande app
            sys.exit(0)
        else:
            # Ingen uppdatering, bara restart
            if hasattr(sys, '_MEIPASS'):
                exe_path = sys.executable
            else:
                exe_path = sys.argv[0]
            
            subprocess.Popen([exe_path])
            sys.exit(0)

class AutoUpdateManager(QObject):
    """Manager för automatiska uppdateringar"""
    
    update_available = pyqtSignal(dict)  # Update data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self._check_for_updates)
        
        info("AutoUpdateManager", "Auto Update Manager initialized")
    
    def start_monitoring(self):
        """Starta automatisk övervakning"""
        info("AutoUpdateManager", "Starting update monitoring")
        
        # Kolla direkt vid start
        self._check_for_updates()
        
        # Kolla varje timme (3600000 ms)
        self.check_timer.start(3600000)  # 1 timme
        debug("AutoUpdateManager", "Update monitoring started - checking every hour")
    
    def stop_monitoring(self):
        """Stoppa automatisk övervakning"""
        self.check_timer.stop()
        debug("AutoUpdateManager", "Update monitoring stopped")
    
    def _check_for_updates(self):
        """Kolla efter uppdateringar"""
        info("AutoUpdateManager", "Checking for updates...")
        
        try:
            current_version = get_version()
            debug("AutoUpdateManager", f"Current version: {current_version}")
            
            # Kolla efter uppdateringar
            update_info = version_manager.check_for_updates()
            debug("AutoUpdateManager", f"Update check result: {update_info}")
            
            if update_info.get('update_available'):
                latest_version = update_info.get('latest_version')
                info("AutoUpdateManager", f"Update available: {current_version} -> {latest_version}")
                
                # Visa tvingande uppdateringsdialog
                self._show_forced_update_dialog(update_info, current_version, latest_version)
            else:
                debug("AutoUpdateManager", "No updates available")
                
        except Exception as e:
            error("AutoUpdateManager", f"Update check failed: {e}")
    
    def _show_forced_update_dialog(self, update_info, current_version, latest_version):
        """Visa tvingande uppdateringsdialog"""
        info("AutoUpdateManager", f"Showing forced update dialog: {current_version} -> {latest_version}")
        
        # Skapa och visa dialog
        dialog = UpdateDialog(
            parent=self.parent_window,
            latest_version=latest_version,
            current_version=current_version
        )
        
        # Starta uppdateringsprocessen direkt
        dialog.start_update(update_info)
        
        # Visa modal dialog (blockerar appen tills uppdatering är klar)
        dialog.exec()

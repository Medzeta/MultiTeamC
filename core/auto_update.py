"""
Auto-Update System
Automatisk uppdatering av applikationen
"""

import json
import requests
import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, Callable
from packaging import version
from core.debug_logger import debug, info, warning, error, exception


class AutoUpdate:
    """System för automatiska uppdateringar"""
    
    # Update server URL (change to your actual server)
    UPDATE_SERVER = "https://api.multiteam.app/updates"
    CURRENT_VERSION = "3.5.0"
    
    def __init__(self):
        """Initialize auto-update system"""
        debug("AutoUpdate", "Initializing auto-update system")
        
        self.enabled = True
        self.check_on_startup = True
        self.auto_download = False  # Require user confirmation
        self.update_available = False
        self.latest_version = None
        self.download_url = None
        
        # Callbacks
        self.on_update_available: Optional[Callable] = None
        self.on_update_downloaded: Optional[Callable] = None
        self.on_update_error: Optional[Callable] = None
        
        info("AutoUpdate", f"Auto-update initialized (current version: {self.CURRENT_VERSION})")
    
    def check_for_updates(self) -> Optional[Dict]:
        """
        Check for available updates
        
        Returns:
            Update info dict if available, None otherwise
        """
        if not self.enabled:
            debug("AutoUpdate", "Auto-update disabled")
            return None
        
        info("AutoUpdate", "Checking for updates...")
        
        try:
            # Make request to update server
            response = requests.get(
                f"{self.UPDATE_SERVER}/latest",
                params={'current_version': self.CURRENT_VERSION},
                timeout=10
            )
            
            if response.status_code != 200:
                warning("AutoUpdate", f"Update check failed: {response.status_code}")
                return None
            
            update_info = response.json()
            
            latest_version = update_info.get('version')
            if not latest_version:
                warning("AutoUpdate", "No version info in response")
                return None
            
            # Compare versions
            if version.parse(latest_version) > version.parse(self.CURRENT_VERSION):
                info("AutoUpdate", f"Update available: {latest_version}")
                
                self.update_available = True
                self.latest_version = latest_version
                self.download_url = update_info.get('download_url')
                
                # Trigger callback
                if self.on_update_available:
                    self.on_update_available(update_info)
                
                return update_info
            else:
                info("AutoUpdate", "Application is up to date")
                return None
                
        except requests.exceptions.RequestException as e:
            exception("AutoUpdate", f"Network error checking for updates: {e}")
            return None
        except Exception as e:
            exception("AutoUpdate", f"Error checking for updates: {e}")
            return None
    
    def download_update(self, download_url: str, save_path: str) -> bool:
        """
        Download update file
        
        Args:
            download_url: URL to download from
            save_path: Path to save file
            
        Returns:
            True if successful
        """
        info("AutoUpdate", f"Downloading update from: {download_url}")
        
        try:
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Log progress
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            if downloaded % (1024 * 1024) == 0:  # Every MB
                                debug("AutoUpdate", f"Download progress: {progress:.1f}%")
            
            info("AutoUpdate", "Update downloaded successfully")
            
            # Trigger callback
            if self.on_update_downloaded:
                self.on_update_downloaded(save_path)
            
            return True
            
        except Exception as e:
            exception("AutoUpdate", f"Error downloading update: {e}")
            
            if self.on_update_error:
                self.on_update_error(str(e))
            
            return False
    
    def install_update(self, installer_path: str) -> bool:
        """
        Install downloaded update
        
        Args:
            installer_path: Path to installer file
            
        Returns:
            True if installation started
        """
        info("AutoUpdate", f"Installing update: {installer_path}")
        
        try:
            # Verify file exists
            if not Path(installer_path).exists():
                error("AutoUpdate", "Installer file not found")
                return False
            
            # Start installer
            # Use subprocess to run installer and exit current app
            subprocess.Popen([installer_path, '/SILENT'])
            
            info("AutoUpdate", "Update installation started")
            return True
            
        except Exception as e:
            exception("AutoUpdate", f"Error installing update: {e}")
            return False
    
    def get_update_info(self) -> Optional[Dict]:
        """
        Get current update information
        
        Returns:
            Update info dict if available
        """
        if not self.update_available:
            return None
        
        return {
            'current_version': self.CURRENT_VERSION,
            'latest_version': self.latest_version,
            'download_url': self.download_url,
            'update_available': self.update_available
        }
    
    def enable(self):
        """Enable auto-update"""
        debug("AutoUpdate", "Enabling auto-update")
        self.enabled = True
    
    def disable(self):
        """Disable auto-update"""
        debug("AutoUpdate", "Disabling auto-update")
        self.enabled = False
    
    def set_check_on_startup(self, enabled: bool):
        """Set whether to check for updates on startup"""
        self.check_on_startup = enabled
        debug("AutoUpdate", f"Check on startup: {enabled}")
    
    def set_auto_download(self, enabled: bool):
        """Set whether to automatically download updates"""
        self.auto_download = enabled
        debug("AutoUpdate", f"Auto download: {enabled}")


class UpdateChecker:
    """Helper class for checking updates in background"""
    
    def __init__(self, auto_update: AutoUpdate):
        """
        Initialize update checker
        
        Args:
            auto_update: AutoUpdate instance
        """
        self.auto_update = auto_update
    
    def check_now(self) -> Optional[Dict]:
        """
        Check for updates now
        
        Returns:
            Update info if available
        """
        return self.auto_update.check_for_updates()
    
    def download_and_install(self, update_info: Dict) -> bool:
        """
        Download and install update
        
        Args:
            update_info: Update information dict
            
        Returns:
            True if successful
        """
        download_url = update_info.get('download_url')
        if not download_url:
            error("UpdateChecker", "No download URL in update info")
            return False
        
        # Download to temp directory
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        installer_path = temp_dir / f"MultiTeam_Setup_v{update_info['version']}.exe"
        
        # Download
        if not self.auto_update.download_update(download_url, str(installer_path)):
            return False
        
        # Install
        return self.auto_update.install_update(str(installer_path))

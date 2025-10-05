"""
Version Management System för Multi Team -C
Centraliserad versionshantering och auto-update funktionalitet
"""

import os
import json
import requests
import zipfile
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from core.debug_logger import debug, info, warning, error

# AKTUELL VERSION
APP_VERSION = "0.31"
APP_NAME = "MultiTeam"
GITHUB_OWNER = "Medzeta"
GITHUB_REPO = "MultiTeamC"

# VERSION INFO
VERSION_INFO = {
    "version": APP_VERSION,
    "build_date": "2025-10-05",
    "build_type": "Release",
    "features": [
        "Dynamiskt Asset-System",
        "Auto-Refresh Dashboard", 
        "Klickbara Modulkort",
        "GitHub Release Automation",
        "Auto-Update System"
    ]
}

class VersionManager:
    """Hanterar versionsinfo och auto-update funktionalitet"""
    
    def __init__(self):
        self.current_version = APP_VERSION
        self.github_api_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
        self.update_dir = Path("updates")
        self.backup_dir = Path("backup")
        
    def get_current_version(self) -> str:
        """Hämta nuvarande version"""
        return self.current_version
    
    def get_version_info(self) -> dict:
        """Hämta komplett versionsinfo"""
        return {
            **VERSION_INFO,
            "current_version": self.current_version,
            "github_repo": f"{GITHUB_OWNER}/{GITHUB_REPO}",
            "check_time": datetime.now().isoformat()
        }
    
    def check_for_updates(self) -> dict:
        """Kolla efter nya versioner på GitHub"""
        info("VersionManager", "Checking for updates...")
        
        try:
            # Hämta senaste release från GitHub API
            headers = {
                'Accept': 'application/vnd.github+json',
                'User-Agent': 'MultiTeam-AutoUpdater/0.20'
            }
            
            response = requests.get(f"{self.github_api_url}/releases/latest", 
                                  timeout=30, headers=headers)
            
            if response.status_code == 404:
                # Repository finns inte eller inga releases
                warning("VersionManager", "No GitHub releases found - using development mode")
                return {
                    "update_available": False,
                    "latest_version": self.current_version,
                    "current_version": self.current_version,
                    "message": "No releases available yet. This is normal for development.",
                    "development_mode": True
                }
            
            elif response.status_code == 403:
                # Rate limit
                warning("VersionManager", "GitHub API rate limit exceeded")
                return {
                    "update_available": False,
                    "error": "GitHub API rate limit exceeded. Try again later.",
                    "current_version": self.current_version
                }
            
            elif response.status_code == 200:
                release_data = response.json()
                latest_version = release_data["tag_name"].replace("v", "")
                
                debug("VersionManager", f"Current: {self.current_version}, Latest: {latest_version}")
                
                # Jämför versioner
                if self._is_newer_version(latest_version, self.current_version):
                    info("VersionManager", f"Update available: {latest_version}")
                    
                    # Hitta EXE-asset (MultiTeam.exe)
                    exe_asset = None
                    for asset in release_data.get("assets", []):
                        if asset["name"].endswith(".exe") and "MultiTeam" in asset["name"]:
                            exe_asset = asset
                            break
                    
                    if not exe_asset:
                        warning("VersionManager", "No EXE asset found in release")
                        return {
                            "update_available": False,
                            "error": "No executable found in release",
                            "current_version": self.current_version
                        }
                    
                    return {
                        "update_available": True,
                        "latest_version": latest_version,
                        "current_version": self.current_version,
                        "release_notes": release_data.get("body", ""),
                        "download_url": exe_asset["browser_download_url"],
                        "asset_name": exe_asset["name"],
                        "release_date": release_data.get("published_at", ""),
                        "release_name": release_data.get("name", f"Version {latest_version}")
                    }
                else:
                    info("VersionManager", "No updates available")
                    return {
                        "update_available": False,
                        "latest_version": latest_version,
                        "current_version": self.current_version,
                        "message": "You have the latest version"
                    }
            
            else:
                warning("VersionManager", f"GitHub API error: {response.status_code}")
                return {
                    "update_available": False,
                    "error": f"API Error: {response.status_code}",
                    "current_version": self.current_version
                }
                
        except requests.RequestException as e:
            error("VersionManager", f"Network error checking updates: {e}")
            return {
                "update_available": False,
                "error": f"Network error: {str(e)}",
                "current_version": self.current_version
            }
        except Exception as e:
            error("VersionManager", f"Unexpected error: {e}")
            return {
                "update_available": False,
                "error": f"Unexpected error: {str(e)}",
                "current_version": self.current_version
            }
    
    def download_update(self, download_url: str, asset_name: str) -> dict:
        """Ladda ner uppdatering från GitHub (EXE)"""
        info("VersionManager", f"Downloading update: {asset_name}")
        
        try:
            # Skapa update-mapp
            self.update_dir.mkdir(exist_ok=True)
            
            # Ladda ner EXE
            response = requests.get(download_url, timeout=120, stream=True)
            response.raise_for_status()
            
            exe_path = self.update_dir / asset_name
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(exe_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            debug("VersionManager", f"Download progress: {progress}%")
            
            info("VersionManager", f"Download completed: {exe_path}")
            
            return {
                "success": True,
                "exe_path": str(exe_path),
                "message": "Update downloaded successfully"
            }
            
        except Exception as e:
            error("VersionManager", f"Download failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def install_update(self, exe_path: str) -> dict:
        """Installera uppdatering från EXE"""
        info("VersionManager", f"Installing update from: {exe_path}")
        
        try:
            # Skapa backup av nuvarande EXE
            self._create_backup()
            
            # Hitta nuvarande EXE-fil
            current_exe = Path(sys.executable)
            
            if not current_exe.exists():
                raise Exception(f"Current executable not found: {current_exe}")
            
            # Ersätt nuvarande EXE med ny version
            # Vi kan inte ersätta en körande EXE direkt, så vi skapar en batch-fil
            update_script = self.update_dir / "update.bat"
            
            with open(update_script, 'w') as f:
                f.write('@echo off\n')
                f.write('echo Waiting for application to close...\n')
                f.write('timeout /t 2 /nobreak >nul\n')
                f.write(f'copy /Y "{exe_path}" "{current_exe}"\n')
                f.write('echo Update completed!\n')
                f.write(f'start "" "{current_exe}"\n')
                f.write(f'del "{update_script}"\n')
            
            info("VersionManager", "Update script created successfully")
            
            return {
                "success": True,
                "message": "Update ready. Application will restart.",
                "restart_required": True,
                "update_script": str(update_script)
            }
            
        except Exception as e:
            error("VersionManager", f"Installation failed: {e}")
            # Återställ från backup vid fel
            self._restore_backup()
            return {
                "success": False,
                "error": str(e)
            }
    
    def _is_newer_version(self, latest: str, current: str) -> bool:
        """Jämför versioner med korrekt decimal-hantering"""
        try:
            # Dela upp i major.minor för korrekt jämförelse
            def parse_version(v):
                parts = v.split('.')
                if len(parts) == 1:
                    return (int(parts[0]), 0)
                return (int(parts[0]), int(parts[1]))
            
            latest_tuple = parse_version(latest)
            current_tuple = parse_version(current)
            
            debug("VersionManager", f"Comparing versions: {current_tuple} < {latest_tuple}")
            return latest_tuple > current_tuple
        except Exception as e:
            error("VersionManager", f"Version comparison error: {e}")
            # Fallback till string-jämförelse
            return latest != current
    
    def _create_backup(self):
        """Skapa backup av nuvarande installation"""
        info("VersionManager", "Creating backup...")
        
        self.backup_dir.mkdir(exist_ok=True)
        
        # Backup viktiga filer
        files_to_backup = [
            "MultiTeam.exe",
            "README.md",
            "ROADMAP.md"
        ]
        
        for file_name in files_to_backup:
            src = Path(file_name)
            if src.exists():
                dst = self.backup_dir / file_name
                shutil.copy2(src, dst)
                debug("VersionManager", f"Backed up: {file_name}")
    
    def _restore_backup(self):
        """Återställ från backup"""
        warning("VersionManager", "Restoring from backup...")
        
        if self.backup_dir.exists():
            for backup_file in self.backup_dir.iterdir():
                if backup_file.is_file():
                    dst = Path(backup_file.name)
                    shutil.copy2(backup_file, dst)
                    debug("VersionManager", f"Restored: {backup_file.name}")
    
    def _copy_update_files(self, package_dir: Path):
        """Kopiera uppdateringsfiler (exklusive databas/loggar)"""
        info("VersionManager", f"Copying files from: {package_dir}")
        
        # Filer att kopiera
        files_to_update = [
            "MultiTeam.exe",
            "README.md", 
            "ROADMAP.md",
            "QUICK_START.txt"
        ]
        
        for file_name in files_to_update:
            src = package_dir / file_name
            if src.exists():
                dst = Path(file_name)
                shutil.copy2(src, dst)
                info("VersionManager", f"Updated: {file_name}")
        
        # Skapa mappar om de inte finns (men kopiera inte innehåll)
        dirs_to_create = ["data", "logs"]
        for dir_name in dirs_to_create:
            Path(dir_name).mkdir(exist_ok=True)


# Global version manager instance
version_manager = VersionManager()

def get_version() -> str:
    """Hämta nuvarande version (convenience function)"""
    return APP_VERSION

def get_version_info() -> dict:
    """Hämta versionsinfo (convenience function)"""
    return version_manager.get_version_info()

def check_for_updates() -> dict:
    """Kolla efter uppdateringar (convenience function)"""
    return version_manager.check_for_updates()

def increment_version() -> str:
    """Räkna upp version med 0.01 för nästa release"""
    global APP_VERSION
    try:
        current_float = float(APP_VERSION)
        new_version = round(current_float + 0.01, 2)
        new_version_str = f"{new_version:.2f}"
        
        # Uppdatera version i filen
        version_file = Path(__file__)
        content = version_file.read_text(encoding='utf-8')
        
        # Ersätt APP_VERSION rad
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('APP_VERSION = '):
                lines[i] = f'APP_VERSION = "{new_version_str}"'
                break
        
        # Skriv tillbaka till fil
        version_file.write_text('\n'.join(lines), encoding='utf-8')
        
        # Uppdatera global variabel
        APP_VERSION = new_version_str
        
        info("VersionManager", f"Version incremented: {APP_VERSION} -> {new_version_str}")
        return new_version_str
        
    except Exception as e:
        error("VersionManager", f"Failed to increment version: {e}")
        return APP_VERSION

def get_next_version() -> str:
    """Hämta nästa version utan att uppdatera filen"""
    try:
        current_float = float(APP_VERSION)
        next_version = round(current_float + 0.01, 2)
        return f"{next_version:.2f}"
    except:
        return APP_VERSION

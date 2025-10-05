"""
Global Settings System
Centraliserad hantering av applikationsinställningar
"""

import json
from pathlib import Path
from typing import Dict, Any
from core.debug_logger import debug, info, warning, error, exception


class GlobalSettings:
    """Global settings manager"""
    
    _instance = None
    _initialized = False
    
    # Default settings
    DEFAULT_SETTINGS = {
        "email_verification_enabled": True,
        "2fa_enabled": True,
        "2fa_required_for_all": False,
        "session_timeout_minutes": 60,
        "remember_me_days": 30,
        "max_login_attempts": 5,
        "password_reset_enabled": True,
        "google_oauth_enabled": False,
        "minimize_to_tray": False,
        "app_theme": "dark",
        "log_level": "DEBUG"
    }
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            debug("GlobalSettings", "Creating new GlobalSettings instance")
            cls._instance = super(GlobalSettings, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize settings"""
        if not GlobalSettings._initialized:
            debug("GlobalSettings", "Initializing global settings system")
            self.settings_file = Path("data/settings.json")
            self.settings = {}
            self._load_settings()
            GlobalSettings._initialized = True
            info("GlobalSettings", "Global settings system initialized")
    
    def _load_settings(self):
        """Load settings from file"""
        debug("GlobalSettings", f"Loading settings from: {self.settings_file}")
        
        # Ensure data directory exists
        self.settings_file.parent.mkdir(exist_ok=True)
        
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                info("GlobalSettings", f"Settings loaded: {len(self.settings)} items")
                debug("GlobalSettings", f"Settings content: {self.settings}")
            except Exception as e:
                exception("GlobalSettings", "Error loading settings file")
                self.settings = self.DEFAULT_SETTINGS.copy()
                self._save_settings()
        else:
            debug("GlobalSettings", "Settings file not found, creating with defaults")
            self.settings = self.DEFAULT_SETTINGS.copy()
            self._save_settings()
    
    def _save_settings(self):
        """Save settings to file"""
        debug("GlobalSettings", "Saving settings to file")
        
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            info("GlobalSettings", "Settings saved successfully")
        except Exception as e:
            exception("GlobalSettings", "Error saving settings file")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value"""
        value = self.settings.get(key, default)
        debug("GlobalSettings", f"Get setting: {key} = {value}")
        return value
    
    def set(self, key: str, value: Any):
        """Set setting value"""
        debug("GlobalSettings", f"Set setting: {key} = {value}")
        old_value = self.settings.get(key)
        self.settings[key] = value
        self._save_settings()
        info("GlobalSettings", f"Setting updated: {key} (old: {old_value}, new: {value})")
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings"""
        debug("GlobalSettings", "Getting all settings")
        return self.settings.copy()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        warning("GlobalSettings", "Resetting all settings to defaults")
        self.settings = self.DEFAULT_SETTINGS.copy()
        self._save_settings()
        info("GlobalSettings", "Settings reset to defaults")
    
    # Convenience methods for common settings
    
    def is_email_verification_enabled(self) -> bool:
        """Check if email verification is enabled"""
        return self.get("email_verification_enabled", True)
    
    def is_2fa_enabled(self) -> bool:
        """Check if 2FA is enabled globally"""
        return self.get("2fa_enabled", True)
    
    def is_2fa_required(self) -> bool:
        """Check if 2FA is required for all users"""
        return self.get("2fa_required_for_all", False)
    
    def get_session_timeout(self) -> int:
        """Get session timeout in minutes"""
        return self.get("session_timeout_minutes", 60)
    
    def get_remember_me_duration(self) -> int:
        """Get remember me duration in days"""
        return self.get("remember_me_days", 30)


# Global instance
settings = GlobalSettings()


if __name__ == "__main__":
    # Test settings
    info("TEST", "Testing GlobalSettings...")
    
    print("\n=== Default Settings ===")
    print(json.dumps(settings.get_all(), indent=2))
    
    print("\n=== Testing Get/Set ===")
    print(f"Email verification: {settings.is_email_verification_enabled()}")
    print(f"2FA enabled: {settings.is_2fa_enabled()}")
    
    settings.set("email_verification_enabled", False)
    print(f"Email verification after change: {settings.is_email_verification_enabled()}")
    
    settings.set("email_verification_enabled", True)
    
    info("TEST", "GlobalSettings test completed")

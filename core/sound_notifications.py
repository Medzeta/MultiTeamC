"""
Sound Notifications System
Ljudnotiser för viktiga händelser
"""

import os
from pathlib import Path
from typing import Optional
from core.debug_logger import debug, info, warning, error, exception

# Try to import playsound
try:
    from playsound import playsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False
    warning("SoundNotifications", "playsound not available - install with: pip install playsound")


class SoundNotifications:
    """System för ljudnotiser"""
    
    # Default sound files (can be customized)
    SOUNDS = {
        'message': 'sounds/message.wav',
        'file': 'sounds/file.wav',
        'notification': 'sounds/notification.wav',
        'alert': 'sounds/alert.wav',
        'success': 'sounds/success.wav',
        'error': 'sounds/error.wav'
    }
    
    def __init__(self, sounds_dir: str = "sounds"):
        """
        Initialize sound notifications
        
        Args:
            sounds_dir: Directory containing sound files
        """
        debug("SoundNotifications", "Initializing sound notifications")
        
        self.enabled = True
        self.sounds_dir = Path(sounds_dir)
        self.volume = 0.5  # 0.0 to 1.0
        
        if not SOUND_AVAILABLE:
            warning("SoundNotifications", "playsound not installed")
            self.enabled = False
        else:
            # Create sounds directory if it doesn't exist
            self.sounds_dir.mkdir(parents=True, exist_ok=True)
            info("SoundNotifications", "Sound notifications initialized")
    
    def play_sound(self, sound_file: str, block: bool = False) -> bool:
        """
        Play sound file
        
        Args:
            sound_file: Path to sound file
            block: Wait for sound to finish (default: False)
            
        Returns:
            True if sound played successfully
        """
        if not self.enabled or not SOUND_AVAILABLE:
            debug("SoundNotifications", "Sound notifications disabled or not available")
            return False
        
        sound_path = Path(sound_file)
        
        # If not absolute path, look in sounds directory
        if not sound_path.is_absolute():
            sound_path = self.sounds_dir / sound_file
        
        if not sound_path.exists():
            debug("SoundNotifications", f"Sound file not found: {sound_path}")
            return False
        
        try:
            debug("SoundNotifications", f"Playing sound: {sound_path}")
            playsound(str(sound_path), block=block)
            return True
            
        except Exception as e:
            exception("SoundNotifications", f"Error playing sound: {e}")
            return False
    
    def play_message_sound(self) -> bool:
        """Play new message sound"""
        return self.play_sound(self.SOUNDS['message'])
    
    def play_file_sound(self) -> bool:
        """Play file received sound"""
        return self.play_sound(self.SOUNDS['file'])
    
    def play_notification_sound(self) -> bool:
        """Play general notification sound"""
        return self.play_sound(self.SOUNDS['notification'])
    
    def play_alert_sound(self) -> bool:
        """Play alert sound"""
        return self.play_sound(self.SOUNDS['alert'])
    
    def play_success_sound(self) -> bool:
        """Play success sound"""
        return self.play_sound(self.SOUNDS['success'])
    
    def play_error_sound(self) -> bool:
        """Play error sound"""
        return self.play_sound(self.SOUNDS['error'])
    
    def enable(self):
        """Enable sound notifications"""
        debug("SoundNotifications", "Enabling sound notifications")
        self.enabled = True
    
    def disable(self):
        """Disable sound notifications"""
        debug("SoundNotifications", "Disabling sound notifications")
        self.enabled = False
    
    def set_volume(self, volume: float):
        """
        Set volume level
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        debug("SoundNotifications", f"Volume set to: {self.volume}")
    
    def is_available(self) -> bool:
        """
        Check if sound notifications are available
        
        Returns:
            True if available
        """
        return self.enabled and SOUND_AVAILABLE
    
    def create_default_sounds(self):
        """
        Create default sound files using system beeps
        (Placeholder - in production, use actual sound files)
        """
        info("SoundNotifications", "Creating default sound files")
        
        # This is a placeholder
        # In production, you would include actual .wav files
        # or generate them programmatically
        
        for sound_name, sound_file in self.SOUNDS.items():
            sound_path = self.sounds_dir / Path(sound_file).name
            if not sound_path.exists():
                debug("SoundNotifications", f"Sound file missing: {sound_name}")
                # You could generate simple beep sounds here
                # or copy from a resources directory

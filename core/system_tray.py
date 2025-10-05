"""
System Tray Integration
Minimera applikationen till system tray
"""

import pystray
from PIL import Image, ImageDraw
from threading import Thread
from core.debug_logger import debug, info, warning
from core.global_settings import settings


class SystemTray:
    """System tray manager"""
    
    def __init__(self, app_window):
        """Initialize system tray"""
        debug("SystemTray", "Initializing system tray")
        
        self.app_window = app_window
        self.icon = None
        self.is_running = False
        
        info("SystemTray", "System tray initialized")
    
    def create_icon(self):
        """Create tray icon"""
        debug("SystemTray", "Creating tray icon")
        
        # Create a simple icon (blue circle with M)
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color=(26, 26, 26))
        draw = ImageDraw.Draw(image)
        
        # Draw circle
        draw.ellipse([8, 8, 56, 56], fill=(31, 106, 165), outline=(20, 80, 130))
        
        # Draw M
        draw.text((20, 18), "M", fill=(255, 255, 255), font=None)
        
        debug("SystemTray", "Tray icon created")
        return image
    
    def show(self):
        """Show system tray icon"""
        if self.is_running:
            debug("SystemTray", "Tray already running")
            return
        
        info("SystemTray", "Showing system tray icon")
        
        # Create menu
        menu = pystray.Menu(
            pystray.MenuItem("Show MultiTeam", self._on_show, default=True),
            pystray.MenuItem("Settings", self._on_settings),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self._on_exit)
        )
        
        # Create icon
        icon_image = self.create_icon()
        self.icon = pystray.Icon(
            "MultiTeam",
            icon_image,
            "MultiTeam Communication",
            menu
        )
        
        # Run in separate thread
        self.is_running = True
        tray_thread = Thread(target=self._run_tray, daemon=True)
        tray_thread.start()
        
        info("SystemTray", "System tray icon shown")
    
    def _run_tray(self):
        """Run tray icon (blocking)"""
        debug("SystemTray", "Starting tray icon loop")
        try:
            self.icon.run()
        except Exception as e:
            warning("SystemTray", f"Tray icon error: {e}")
        finally:
            self.is_running = False
            debug("SystemTray", "Tray icon loop stopped")
    
    def hide(self):
        """Hide system tray icon"""
        if not self.is_running or not self.icon:
            return
        
        info("SystemTray", "Hiding system tray icon")
        self.icon.stop()
        self.is_running = False
        debug("SystemTray", "System tray icon hidden")
    
    def _on_show(self, icon=None, item=None):
        """Show main window"""
        debug("SystemTray", "Show window clicked")
        self.app_window.after(0, self._show_window)
    
    def _show_window(self):
        """Show window (must run in main thread)"""
        info("SystemTray", "Showing main window from tray")
        self.app_window.deiconify()
        self.app_window.lift()
        self.app_window.focus_force()
    
    def _on_settings(self, icon=None, item=None):
        """Open settings"""
        debug("SystemTray", "Settings clicked from tray")
        self.app_window.after(0, self._show_window)
        # TODO: Navigate to settings
    
    def _on_exit(self, icon=None, item=None):
        """Exit application"""
        info("SystemTray", "Exit clicked from tray")
        self.hide()
        self.app_window.after(0, self.app_window.destroy)


if __name__ == "__main__":
    info("TEST", "SystemTray module loaded")
    print("System Tray Integration Ready")

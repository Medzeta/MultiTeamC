"""
License Activation Window
Separate window for license activation to avoid widget cleanup issues
"""

import customtkinter as ctk
from core.debug_logger import debug, info, error
from modules.license_activation_module import LicenseActivationModule


class LicenseActivationWindow(ctk.CTkToplevel):
    """Separate window for license activation"""
    
    def __init__(self, parent, on_success=None, on_close=None):
        """
        Initialize license activation window
        
        Args:
            parent: Parent window
            on_success: Callback when activation succeeds
            on_close: Callback when window closes
        """
        super().__init__(parent)
        
        self.on_success = on_success
        self.on_close = on_close
        
        debug("LicenseActivationWindow", "Initializing license activation window")
        
        self._setup_window()
        self._create_content()
        
        info("LicenseActivationWindow", "License activation window initialized")
    
    def _setup_window(self):
        """Setup window properties"""
        debug("LicenseActivationWindow", "Setting up window properties")
        
        # Window title
        self.title("🔑 License Activation")
        
        # Window size
        window_width = 900
        window_height = 700
        
        # Center window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Window properties
        self.configure(fg_color=("#2b2b2b", "#2b2b2b"))
        self.resizable(True, True)
        
        # Make modal (blocks parent window)
        self.transient(self.master)
        self.grab_set()
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._handle_close)
        
        debug("LicenseActivationWindow", f"Window configured: {window_width}x{window_height}")
    
    def _create_content(self):
        """Create window content"""
        debug("LicenseActivationWindow", "Creating window content")
        
        # Create license activation module
        self.module = LicenseActivationModule(
            self,
            on_success=self._handle_success
        )
        self.module.pack(fill="both", expand=True)
        
        debug("LicenseActivationWindow", "Content created")
    
    def _handle_success(self):
        """Handle successful activation"""
        info("LicenseActivationWindow", "License activation successful")
        
        # Call success callback
        if self.on_success:
            try:
                self.on_success()
            except Exception as e:
                error("LicenseActivationWindow", f"Error in success callback: {e}")
        
        # Close window
        self._handle_close()
    
    def _handle_close(self):
        """Handle window close"""
        debug("LicenseActivationWindow", "Closing window")
        
        # Call close callback
        if self.on_close:
            try:
                self.on_close()
            except Exception as e:
                error("LicenseActivationWindow", f"Error in close callback: {e}")
        
        # Release grab and destroy
        try:
            self.grab_release()
        except:
            pass
        
        try:
            self.destroy()
        except:
            pass
        
        info("LicenseActivationWindow", "Window closed")


if __name__ == "__main__":
    # Test window
    import sys
    sys.path.insert(0, '..')
    
    from core.debug_logger import info
    
    info("TEST", "Testing LicenseActivationWindow...")
    
    root = ctk.CTk()
    root.geometry("400x300")
    root.title("Test Parent")
    
    def show_window():
        window = LicenseActivationWindow(
            root,
            on_success=lambda: print("Success!"),
            on_close=lambda: print("Closed!")
        )
    
    btn = ctk.CTkButton(root, text="Open License Activation", command=show_window)
    btn.pack(pady=50)
    
    root.mainloop()

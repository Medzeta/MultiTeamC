"""
Custom Borderless Window System
Alla fönster i appen använder detta custom design system
"""

import customtkinter as ctk
from typing import Optional, Callable
from core.debug_logger import debug, info, warning, error


class CustomWindow(ctk.CTk):
    """Base class för alla custom borderless windows"""
    
    def __init__(
        self,
        title: str = "MultiTeam",
        width: int = 2200,  # EXTRA BRED - Full Machine ID + Approved knapp synlig
        height: int = 1200,  # Mycket större fast höjd
        resizable: bool = True
    ):
        """Initialize custom window"""
        super().__init__()
        
        self.window_title = title
        self.window_width = width
        self.window_height = height
        
        debug("CustomWindow", f"Initializing window: {title} ({width}x{height})")
        
        # Remove default decorations
        self.overrideredirect(True)
        
        # Window state
        self._is_maximized = False
        self._normal_geometry = None
        self._dragging = False
        self._drag_start_x = 0
        self._drag_start_y = 0
        
        # Setup window
        self._setup_window()
        self._create_main_container()
        
        info("CustomWindow", f"Window created successfully: {title}")
    
    def _setup_window(self):
        """Setup window properties"""
        debug("CustomWindow", "Setting up window properties")
        
        # Set background color
        self.configure(fg_color=("#2b2b2b", "#2b2b2b"))
        
        # Get screen dimensions for positioning
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        debug("CustomWindow", f"Screen size: {screen_width}x{screen_height}")
        debug("CustomWindow", f"Window size: {self.window_width}x{self.window_height}")
        
        # Set window icon
        try:
            from PIL import Image, ImageDraw
            # Create icon
            icon_size = 32
            icon_image = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(icon_image)
            # Draw blue circle
            draw.ellipse([2, 2, icon_size-2, icon_size-2], fill=(31, 106, 165, 255))
            # Save as temporary ico file
            import tempfile
            import os
            temp_ico = os.path.join(tempfile.gettempdir(), 'multiteam_icon.ico')
            icon_image.save(temp_ico, format='ICO')
            self.iconbitmap(temp_ico)
            debug("CustomWindow", f"Window icon set: {temp_ico}")
        except Exception as e:
            debug("CustomWindow", f"Could not set window icon: {e}")
        
        # Center horizontally, position at very top
        x = (screen_width - self.window_width) // 2
        y = 0  # No margin from top - use full height
        
        self.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
        self.minsize(1200, 800)  # Större minsize
        
        # Configure grid - endast en rad för main container
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        debug("CustomWindow", "Grid configured")
    
    def _create_main_container(self):
        """Create main container with rounded corners containing everything"""
        debug("CustomWindow", "Creating main container")
        
        # Main container
        self.main_container = ctk.CTkFrame(
            self,
            fg_color=("#2b2b2b", "#2b2b2b"),
            corner_radius=0
        )
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Custom title bar INUTI main container
        title_bar_frame = ctk.CTkFrame(
            self.main_container,
            height=55,  # Ökad höjd för att undvika klippning
            fg_color=("transparent"),
            corner_radius=0
        )
        title_bar_frame.grid(row=0, column=0, sticky="ew")
        title_bar_frame.grid_propagate(False)
        title_bar_frame.grid_columnconfigure(1, weight=1)
        title_bar_frame.grid_rowconfigure(0, weight=1)
        
        # Left side - App name and user info
        left_container = ctk.CTkFrame(
            title_bar_frame,
            fg_color="transparent"
        )
        left_container.grid(row=0, column=0, padx=15, pady=6, sticky="w")  # Mer padding
        
        # App name (top)
        app_name_label = ctk.CTkLabel(
            left_container,
            text=self.window_title,
            font=("Segoe UI", 11, "bold"),
            text_color=("#ffffff", "#ffffff"),
            height=18  # Explicit höjd
        )
        app_name_label.pack(anchor="w", pady=(0, 1))  # Lite spacing
        
        # User info container (bottom)
        self.user_info_frame = ctk.CTkFrame(
            left_container,
            fg_color="transparent"
        )
        self.user_info_frame.pack(anchor="w", pady=(2, 0))
        
        # Username
        self.username_label = ctk.CTkLabel(
            self.user_info_frame,
            text="Not logged in",
            font=("Segoe UI", 11, "bold"),  # Samma som appnamn
            text_color=("#cccccc", "#cccccc"),
            height=18  # Explicit höjd för att undvika klippning
        )
        self.username_label.pack(side="left", padx=(0, 6))
        
        # Client ID (UID)
        self.client_id_label = ctk.CTkLabel(
            self.user_info_frame,
            text="",
            font=("Segoe UI", 9),
            text_color=("#888888", "#888888"),
            height=18
        )
        self.client_id_label.pack(side="left", padx=(0, 6))
        
        # Status indicator (colored dot) - after username
        self.status_dot = ctk.CTkLabel(
            self.user_info_frame,
            text="●",
            font=("Segoe UI", 16),
            text_color=("#c42b1c", "#c42b1c"),  # Default: red (offline)
            width=25,
            height=20
        )
        self.status_dot.pack(side="left")
        
        # Button container
        button_frame = ctk.CTkFrame(
            title_bar_frame,
            fg_color="transparent"
        )
        button_frame.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        
        # Minimize button
        self.minimize_btn = ctk.CTkButton(
            button_frame,
            text="─",
            width=40,
            height=30,
            fg_color="transparent",
            hover_color=("#3a3a3a", "#3a3a3a"),
            command=self._minimize_window,
            font=("Segoe UI", 14)
        )
        self.minimize_btn.grid(row=0, column=0, padx=2)
        
        # Maximize button
        self.maximize_btn = ctk.CTkButton(
            button_frame,
            text="□",
            width=40,
            height=30,
            fg_color="transparent",
            hover_color=("#3a3a3a", "#3a3a3a"),
            command=self._toggle_maximize,
            font=("Segoe UI", 14)
        )
        self.maximize_btn.grid(row=0, column=1, padx=2)
        
        # Close button
        self.close_btn = ctk.CTkButton(
            button_frame,
            text="✕",
            width=40,
            height=30,
            fg_color="transparent",
            hover_color=("#c42b1c", "#c42b1c"),
            command=self._close_window,
            font=("Segoe UI", 14)
        )
        self.close_btn.grid(row=0, column=2, padx=2)
        
        # Bind dragging to title bar and app name
        title_bar_frame.bind("<Button-1>", self._start_drag)
        title_bar_frame.bind("<B1-Motion>", self._on_drag)
        title_bar_frame.bind("<ButtonRelease-1>", self._stop_drag)
        app_name_label.bind("<Button-1>", self._start_drag)
        app_name_label.bind("<B1-Motion>", self._on_drag)
        app_name_label.bind("<ButtonRelease-1>", self._stop_drag)
        left_container.bind("<Button-1>", self._start_drag)
        left_container.bind("<B1-Motion>", self._on_drag)
        left_container.bind("<ButtonRelease-1>", self._stop_drag)
        
        # Content frame INUTI main container
        self.content_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=("transparent"),
            corner_radius=0
        )
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        debug("CustomWindow", "Main container created with rounded corners")
    
    def update_user_status(self, username: str = None, status: str = "offline", avatar_text: str = None):
        """Update user status widget with colored dot
        
        Args:
            username: User's display name
            status: 'online' (green), 'offline' (red), 'away' (yellow), 'connecting' (gray)
            avatar_text: Not used anymore (kept for compatibility)
        """
        debug("CustomWindow", f"Updating user status: {username}, {status}")
        
        # Status dot colors
        status_colors = {
            "online": ("#107c10", "#0d5e0d"),      # Green
            "offline": ("#c42b1c", "#a52318"),     # Red
            "away": ("#f7630c", "#d15a0a"),        # Yellow/Orange
            "connecting": ("#808080", "#666666")   # Gray
        }
        
        dot_color = status_colors.get(status, status_colors["offline"])
        
        # Update status dot color
        self.status_dot.configure(text_color=dot_color)
        
        # Update username
        if username:
            self.username_label.configure(text=username, text_color=("#ffffff", "#ffffff"))
        else:
            self.username_label.configure(text="Not logged in", text_color=("#999999", "#999999"))
        
        info("CustomWindow", f"User status updated: {username} - {status}")
    
    def update_client_id(self, client_id: str):
        """
        Update client ID display
        
        Args:
            client_id: P2P Client ID (UUID)
        """
        if client_id:
            # Show first 8 characters of UUID
            short_id = client_id[:8]
            self.client_id_label.configure(text=f"[{short_id}]")
            debug("CustomWindow", f"Client ID updated: {short_id}...")
        else:
            self.client_id_label.configure(text="")
            debug("CustomWindow", "Client ID cleared")
    
    def _start_drag(self, event):
        """Start window dragging"""
        if not self._is_maximized:
            self._dragging = True
            self._drag_start_x = event.x
            self._drag_start_y = event.y
            debug("CustomWindow", f"Drag started at ({event.x}, {event.y})")
    
    def _on_drag(self, event):
        """Handle window dragging"""
        if self._dragging and not self._is_maximized:
            x = self.winfo_x() + event.x - self._drag_start_x
            y = self.winfo_y() + event.y - self._drag_start_y
            self.geometry(f"+{x}+{y}")
    
    def _stop_drag(self, event):
        """Stop window dragging"""
        if self._dragging:
            self._dragging = False
            debug("CustomWindow", "Drag stopped")
    
    def _minimize_window(self):
        """Minimize window"""
        debug("CustomWindow", "Minimizing window")
        try:
            # Temporarily disable overrideredirect to allow minimize
            self.overrideredirect(False)
            self.update()  # Force update
            self.iconify()
            # Re-enable overrideredirect when restored
            self.bind("<Map>", self._on_restore)
            info("CustomWindow", "Window minimized to taskbar")
        except Exception as e:
            debug("CustomWindow", f"Minimize error: {e}")
            # Fallback: just hide the window
            self.withdraw()
            info("CustomWindow", "Window hidden")
    
    def _on_restore(self, event=None):
        """Called when window is restored from minimize"""
        debug("CustomWindow", "Window restored from minimize")
        self.overrideredirect(True)
        self.unbind("<Map>")
        info("CustomWindow", "Overrideredirect restored")
    
    def _toggle_maximize(self):
        """Toggle maximize/restore window"""
        if self._is_maximized:
            debug("CustomWindow", "Restoring window")
            if self._normal_geometry:
                self.geometry(self._normal_geometry)
            self._is_maximized = False
            self.maximize_btn.configure(text="□")
            info("CustomWindow", "Window restored")
        else:
            debug("CustomWindow", "Maximizing window")
            self._normal_geometry = self.geometry()
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            self.geometry(f"{screen_width}x{screen_height}+0+0")
            self._is_maximized = True
            self.maximize_btn.configure(text="❐")
            info("CustomWindow", "Window maximized")
    
    def _close_window(self):
        """Close window"""
        debug("CustomWindow", f"Closing window: {self.window_title}")
        self.destroy()
        info("CustomWindow", f"Window closed: {self.window_title}")
    
    def set_content(self, widget):
        """Set content widget in content area"""
        debug("CustomWindow", f"Setting content widget: {type(widget).__name__}")
        widget.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        info("CustomWindow", "Content widget set successfully")


class CustomDialog(ctk.CTkToplevel):
    """Custom dialog/popup window"""
    
    def __init__(
        self,
        parent,
        title: str = "Dialog",
        width: int = 400,
        height: int = 300
    ):
        """Initialize custom dialog"""
        debug("CustomDialog", f"Initializing dialog: {title} ({width}x{height})")
        super().__init__(parent)
        
        self.dialog_title = title
        self.dialog_width = width
        self.dialog_height = height
        
        # Remove default decorations (no Windows title bar)
        self.overrideredirect(True)
        
        # Dialog state
        self._dragging = False
        self._drag_start_x = 0
        self._drag_start_y = 0
        
        # Setup dialog
        self._setup_dialog()
        self._create_title_bar()
        self._create_content_area()
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        info("CustomDialog", f"Dialog created: {title}")
    
    def _setup_dialog(self):
        """Setup dialog properties"""
        debug("CustomDialog", "Setting up dialog properties")
        
        # Center on parent - wait for parent to be fully rendered
        self.update_idletasks()
        
        # Get parent window position and size
        try:
            # Try to get the root window (main window)
            root = self.master.winfo_toplevel()
            parent_x = root.winfo_x()
            parent_y = root.winfo_y()
            parent_width = root.winfo_width()
            parent_height = root.winfo_height()
        except:
            # Fallback to master if root fails
            parent_x = self.master.winfo_x()
            parent_y = self.master.winfo_y()
            parent_width = self.master.winfo_width()
            parent_height = self.master.winfo_height()
        
        # Calculate center position
        x = parent_x + (parent_width - self.dialog_width) // 2
        y = parent_y + (parent_height - self.dialog_height) // 2
        
        # Ensure dialog is on screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        if x < 0:
            x = 50
        if y < 0:
            y = 50
        if x + self.dialog_width > screen_width:
            x = screen_width - self.dialog_width - 50
        if y + self.dialog_height > screen_height:
            y = screen_height - self.dialog_height - 50
        
        debug("CustomDialog", f"Position: ({x}, {y}), Parent: ({parent_x}, {parent_y}, {parent_width}x{parent_height})")
        self.geometry(f"{self.dialog_width}x{self.dialog_height}+{x}+{y}")
        
        # Set background to match app background for seamless rounded corners
        self.configure(fg_color=("#1a1a1a", "#1a1a1a"))
        
        # Create border frame (wrapper) - Global popup design
        # Note: True rounded corners not possible with overrideredirect(True)
        # This creates a subtle border effect
        self.border_frame = ctk.CTkFrame(
            self,
            fg_color=("#2b2b2b", "#2b2b2b"),  # Samma mörka färg som innehållet
            corner_radius=0,  # Måste vara 0 med overrideredirect
            border_width=1,
            border_color=("#3a3a3a", "#3a3a3a")  # Subtil border
        )
        self.border_frame.pack(fill="both", expand=True, padx=1, pady=1)  # 1px = tunn border
        
        # Add transparency for modern glass effect
        try:
            self.attributes('-alpha', 0.92)  # Mer genomskinlighet (92%)
        except:
            pass
        
        # Lift dialog above parent
        self.lift()
        self.focus_force()
        
        # Configure grid on border_frame instead
        self.border_frame.grid_rowconfigure(1, weight=1)
        self.border_frame.grid_columnconfigure(0, weight=1)
        debug("CustomDialog", "Grid configured with border frame")
    
    def _create_title_bar(self):
        """Create dialog title bar"""
        debug("CustomDialog", "Creating title bar")
        
        self.title_bar = ctk.CTkFrame(
            self.border_frame,  # Parent är nu border_frame
            height=35,
            fg_color=("#2b2b2b", "#2b2b2b"),  # Samma mörka färg som innehållet
            corner_radius=0
        )
        self.title_bar.grid(row=0, column=0, sticky="ew")
        self.title_bar.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.title_bar,
            text=self.dialog_title,
            font=("Segoe UI", 11, "bold"),
            text_color=("#ffffff", "#ffffff")  # Vit text
        )
        self.title_label.grid(row=0, column=0, padx=15, pady=7, sticky="w")
        
        # Close button
        self.close_btn = ctk.CTkButton(
            self.title_bar,
            text="✕",
            width=35,
            height=25,
            fg_color="transparent",
            hover_color=("#c42b1c", "#c42b1c"),
            command=self._close_dialog,
            font=("Segoe UI", 12)
        )
        self.close_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # Bind dragging
        self.title_bar.bind("<Button-1>", self._start_drag)
        self.title_bar.bind("<B1-Motion>", self._on_drag)
        self.title_bar.bind("<ButtonRelease-1>", self._stop_drag)
        self.title_label.bind("<Button-1>", self._start_drag)
        self.title_label.bind("<B1-Motion>", self._on_drag)
        self.title_label.bind("<ButtonRelease-1>", self._stop_drag)
        
        debug("CustomDialog", "Title bar created")
    
    def _create_content_area(self):
        """Create dialog content area"""
        debug("CustomDialog", "Creating content area")
        
        self.content_frame = ctk.CTkFrame(
            self.border_frame,  # Parent är nu border_frame
            fg_color=("#2b2b2b", "#2b2b2b"),  # Samma mörka färg som resten
            corner_radius=0
        )
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)  # Ingen padding
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        debug("CustomDialog", "Content area created")
    
    def _start_drag(self, event):
        """Start dialog dragging"""
        self._dragging = True
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        debug("CustomDialog", f"Drag started at ({event.x}, {event.y})")
    
    def _on_drag(self, event):
        """Handle dialog dragging"""
        if self._dragging:
            x = self.winfo_x() + event.x - self._drag_start_x
            y = self.winfo_y() + event.y - self._drag_start_y
            self.geometry(f"+{x}+{y}")
    
    def _stop_drag(self, event):
        """Stop dialog dragging"""
        self._dragging = False
        debug("CustomDialog", "Drag stopped")
    
    def _close_dialog(self):
        """Close dialog"""
        debug("CustomDialog", f"Closing dialog: {self.dialog_title}")
        self.grab_release()
        self.destroy()
        info("CustomDialog", f"Dialog closed: {self.dialog_title}")
    
    def set_content(self, widget):
        """Set content widget"""
        debug("CustomDialog", f"Setting content widget: {type(widget).__name__}")
        widget.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        info("CustomDialog", "Content widget set successfully")


if __name__ == "__main__":
    # Test custom window
    info("TEST", "Testing CustomWindow...")
    app = CustomWindow(title="Test Window", width=600, height=400)
    
    # Add test content
    test_label = ctk.CTkLabel(
        app.content_frame,
        text="Custom Borderless Window Test",
        font=("Segoe UI", 20, "bold")
    )
    test_label.pack(expand=True)
    
    info("TEST", "Starting mainloop...")
    app.mainloop()

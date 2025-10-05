"""
Flet Custom Borderless Window
Custom window with rounded corners and draggable titlebar
"""

import flet as ft
from core.flet_theme import Theme
from core.debug_logger import debug, info


class CustomWindow:
    """Custom borderless window with rounded corners"""
    
    def __init__(self, page: ft.Page, title="MultiTeam Communication"):
        """
        Initialize custom window
        
        Args:
            page: Flet page
            title: Window title
        """
        self.page = page
        self.title = title
        self.content = None
        
        debug("CustomWindow", f"Initializing custom window: {title}")
        
        self._setup_window()
        self._create_titlebar()
        
        info("CustomWindow", "Custom window initialized")
    
    def _setup_window(self):
        """Setup window properties"""
        debug("CustomWindow", "Setting up window properties")
        
        # Window properties
        self.page.title = self.title
        self.page.window.width = 1400
        self.page.window.height = 900
        self.page.window.resizable = True
        self.page.window.frameless = True  # Borderless!
        self.page.window.title_bar_hidden = True
        self.page.window.title_bar_buttons_hidden = True
        self.page.bgcolor = "transparent"  # Transparent for rounded effect
        self.page.padding = 0
        self.page.spacing = 0
        
        # Center window (calculate position)
        try:
            screen_width = 1920  # Default, Flet doesn't provide screen size easily
            screen_height = 1080
            x = (screen_width - 1400) // 2
            y = (screen_height - 900) // 2
            self.page.window.top = y
            self.page.window.left = x
        except:
            pass  # Ignore if positioning fails
        
        # Theme
        self.page.theme = Theme.get_theme()
        self.page.theme_mode = ft.ThemeMode.DARK
        
        debug("CustomWindow", "Window properties configured")
    
    def _create_titlebar(self):
        """Create custom draggable titlebar"""
        debug("CustomWindow", "Creating custom titlebar")
        
        # Titlebar content
        titlebar_content = ft.Container(
            content=ft.Row(
                [
                    # Logo/Icon
                    ft.Container(
                        content=ft.Text(
                            "🔷",
                            size=20,
                        ),
                        padding=ft.padding.only(left=15, right=10),
                    ),
                    
                    # Title
                    ft.Text(
                        self.title,
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color=Theme.TEXT,
                    ),
                    
                    # Spacer
                    ft.Container(expand=True),
                    
                    # Window controls
                    ft.Row(
                        [
                            ft.IconButton(
                                icon="minimize",
                                icon_size=16,
                                icon_color=Theme.TEXT,
                                on_click=self._minimize_window,
                                tooltip="Minimize",
                            ),
                            ft.IconButton(
                                icon="crop_square",
                                icon_size=16,
                                icon_color=Theme.TEXT,
                                on_click=self._maximize_window,
                                tooltip="Maximize",
                            ),
                            ft.IconButton(
                                icon="close",
                                icon_size=16,
                                icon_color=Theme.TEXT,
                                on_click=self._close_window,
                                tooltip="Close",
                            ),
                        ],
                        spacing=0,
                    ),
                ],
                spacing=0,
            ),
            bgcolor=Theme.SURFACE,
            height=40,
            border_radius=ft.border_radius.only(
                top_left=Theme.RADIUS_LG,
                top_right=Theme.RADIUS_LG
            ),
        )
        
        # Make titlebar draggable
        self.titlebar = ft.WindowDragArea(
            content=titlebar_content,
        )
        
        debug("CustomWindow", "Titlebar created")
    
    def _minimize_window(self, e):
        """Minimize window"""
        debug("CustomWindow", "Minimizing window")
        self.page.window.minimized = True
        self.page.update()
    
    def _maximize_window(self, e):
        """Toggle maximize window"""
        debug("CustomWindow", "Toggling maximize")
        self.page.window.maximized = not self.page.window.maximized
        self.page.update()
    
    def _close_window(self, e):
        """Close window"""
        info("CustomWindow", "Closing window")
        self.page.window.destroy()
    
    def set_content(self, content):
        """
        Set window content
        
        Args:
            content: Flet control to display
        """
        debug("CustomWindow", "Setting window content")
        
        self.content = content
        
        # Main container with rounded corners and custom titlebar
        main_container = ft.Container(
            content=ft.Column(
                [
                    self.titlebar,
                    ft.Container(
                        content=content,
                        expand=True,
                        bgcolor=Theme.BACKGROUND,
                        padding=0,
                    ),
                ],
                spacing=0,
            ),
            bgcolor=Theme.SURFACE,
            border_radius=Theme.RADIUS_LG,
            border=ft.border.all(1, Theme.BORDER),
            padding=0,
            margin=10,  # Larger margin to show rounded corners better
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color="#33000000",  # Black with 20% opacity
            ),
        )
        
        # Clear and add to page
        self.page.controls.clear()
        self.page.add(main_container)
        self.page.update()
        
        debug("CustomWindow", "Content set")
    
    def update(self):
        """Update page"""
        self.page.update()


# Export
__all__ = ['CustomWindow']

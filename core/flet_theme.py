"""
Flet Global Design System
Centralized theme and styling for consistent UI
"""

import flet as ft


class Theme:
    """Global design system"""
    
    # Colors
    BACKGROUND = "#1a1a1a"
    SURFACE = "#2b2b2b"
    SURFACE_VARIANT = "#1f1f1f"
    PRIMARY = "#1f6aa5"
    PRIMARY_HOVER = "#1557a0"
    PRIMARY_PRESSED = "#144a8a"
    SECONDARY = "#3a3a3a"
    SECONDARY_HOVER = "#4a4a4a"
    TEXT = "#ffffff"
    TEXT_SECONDARY = "#888888"
    ERROR = "#d32f2f"
    SUCCESS = "#388e3c"
    WARNING = "#f57c00"
    BORDER = "#3a3a3a"
    
    # Spacing
    SPACING_XS = 5
    SPACING_SM = 10
    SPACING_MD = 20
    SPACING_LG = 30
    SPACING_XL = 40
    
    # Border Radius
    RADIUS_SM = 5
    RADIUS_MD = 10
    RADIUS_LG = 15
    
    # Font Sizes
    FONT_XS = 10
    FONT_SM = 11
    FONT_MD = 14
    FONT_LG = 16
    FONT_XL = 20
    FONT_XXL = 24
    FONT_XXXL = 28
    
    @staticmethod
    def get_theme():
        """Get Flet theme configuration"""
        return ft.Theme(
            color_scheme_seed=Theme.PRIMARY,
            use_material3=True,
        )
    
    @staticmethod
    def text_heading(text, **kwargs):
        """Create heading text"""
        return ft.Text(
            text,
            size=Theme.FONT_XXL,
            weight=ft.FontWeight.BOLD,
            color=Theme.TEXT,
            **kwargs
        )
    
    @staticmethod
    def text_title(text, **kwargs):
        """Create title text"""
        return ft.Text(
            text,
            size=Theme.FONT_XL,
            weight=ft.FontWeight.BOLD,
            color=Theme.TEXT,
            **kwargs
        )
    
    @staticmethod
    def text_body(text, **kwargs):
        """Create body text"""
        return ft.Text(
            text,
            size=Theme.FONT_MD,
            color=Theme.TEXT,
            **kwargs
        )
    
    @staticmethod
    def text_caption(text, **kwargs):
        """Create caption text"""
        return ft.Text(
            text,
            size=Theme.FONT_SM,
            color=Theme.TEXT_SECONDARY,
            **kwargs
        )
    
    @staticmethod
    def button_primary(text, on_click=None, **kwargs):
        """Create primary button"""
        return ft.ElevatedButton(
            text=text,
            on_click=on_click,
            bgcolor=Theme.PRIMARY,
            color=Theme.TEXT,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=Theme.RADIUS_SM),
            ),
            **kwargs
        )
    
    @staticmethod
    def button_secondary(text, on_click=None, **kwargs):
        """Create secondary button"""
        return ft.OutlinedButton(
            text=text,
            on_click=on_click,
            style=ft.ButtonStyle(
                color=Theme.TEXT,
                side=ft.BorderSide(1, Theme.BORDER),
                shape=ft.RoundedRectangleBorder(radius=Theme.RADIUS_SM),
            ),
            **kwargs
        )
    
    @staticmethod
    def input_field(label, password=False, **kwargs):
        """Create input field"""
        return ft.TextField(
            label=label,
            password=password,
            bgcolor=Theme.SURFACE_VARIANT,
            border_color=Theme.BORDER,
            focused_border_color=Theme.PRIMARY,
            text_style=ft.TextStyle(color=Theme.TEXT),
            label_style=ft.TextStyle(color=Theme.TEXT_SECONDARY),
            cursor_color=Theme.PRIMARY,
            **kwargs
        )
    
    @staticmethod
    def card(content, **kwargs):
        """Create card container"""
        return ft.Container(
            content=content,
            bgcolor=Theme.SURFACE,
            border_radius=Theme.RADIUS_MD,
            border=ft.border.all(1, Theme.BORDER),
            padding=Theme.SPACING_MD,
            **kwargs
        )
    
    @staticmethod
    def surface(content, **kwargs):
        """Create surface container"""
        return ft.Container(
            content=content,
            bgcolor=Theme.SURFACE_VARIANT,
            border_radius=Theme.RADIUS_SM,
            padding=Theme.SPACING_SM,
            **kwargs
        )


# Export for easy import
__all__ = ['Theme']

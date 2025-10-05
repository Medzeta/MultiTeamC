"""
Global Design Theme
Centraliserad design och styling för hela applikationen
"""

from core.debug_logger import debug, info

# ============================================================
# COLOR PALETTE
# ============================================================

COLORS = {
    # Primary Colors
    "primary": ("#1f6aa5", "#144870"),
    "primary_hover": ("#2980b9", "#1a5a8a"),
    
    # Success Colors
    "success": ("#107c10", "#0d5e0d"),
    "success_hover": ("#0f6b0f", "#0a4d0a"),
    
    # Danger/Error Colors
    "danger": ("#c42b1c", "#a02318"),
    "danger_hover": ("#a82318", "#8a1d14"),
    
    # Warning Colors
    "warning": ("#f7630c", "#d15a0a"),
    "warning_hover": ("#e05a0b", "#b84e09"),
    
    # Secondary Colors
    "secondary": ("#4a4a4a", "#3a3a3a"),
    "secondary_hover": ("#5a5a5a", "#4a4a4a"),
    
    # Background Colors
    "bg_dark": ("#1a1a1a", "#0d0d0d"),
    "bg_medium": ("#2b2b2b", "#1a1a1a"),
    "bg_light": ("#3a3a3a", "#2a2a2a"),
    "bg_lighter": ("#4a4a4a", "#3a3a3a"),
    
    # Text Colors
    "text_primary": ("#ffffff", "#ffffff"),
    "text_secondary": ("#cccccc", "#cccccc"),
    "text_tertiary": ("#999999", "#999999"),
    "text_disabled": ("#666666", "#666666"),
    
    # Border Colors
    "border_dark": ("#2a2a2a", "#1a1a1a"),
    "border_medium": ("#3a3a3a", "#2a2a2a"),
    "border_light": ("#4a4a4a", "#3a3a3a"),
    
    # Transparent
    "transparent": "transparent"
}

# ============================================================
# TYPOGRAPHY
# ============================================================

FONTS = {
    "family": "Segoe UI",
    "family_mono": "Courier New",
    
    # Font Sizes
    "size_tiny": 9,
    "size_small": 10,
    "size_normal": 11,
    "size_medium": 12,
    "size_large": 14,
    "size_xlarge": 16,
    "size_xxlarge": 18,
    "size_huge": 22,
    "size_massive": 28,
    "size_icon": 40,
    "size_icon_large": 64,
}

# ============================================================
# SPACING
# ============================================================

SPACING = {
    "xs": 3,
    "sm": 5,
    "md": 10,
    "lg": 15,
    "xl": 20,
    "xxl": 30,
    "xxxl": 40,
}

# ============================================================
# COMPONENT SIZES
# ============================================================

SIZES = {
    # Buttons
    "button_height_small": 35,
    "button_height_normal": 40,
    "button_height_large": 45,
    "button_width_small": 100,
    "button_width_normal": 150,
    "button_width_large": 200,
    "button_width_xlarge": 250,
    "button_width_full": 420,
    
    # Input Fields
    "entry_height": 40,
    "entry_width_normal": 300,
    "entry_width_large": 420,
    
    # Checkboxes
    "checkbox_size": 20,
    
    # Borders
    "border_width": 1,
    "border_radius": 6,
    "border_radius_small": 4,
    "border_radius_large": 8,
    
    # Windows
    "window_width": 1200,  # 900 * 1.33
    "window_height": 933,  # 700 * 1.33
    "window_min_width": 800,
    "window_min_height": 600,
    
    # Dialogs
    "dialog_width_small": 400,
    "dialog_width_normal": 450,
    "dialog_width_large": 600,
    "dialog_height_small": 200,
    "dialog_height_normal": 250,
    "dialog_height_large": 350,
    
    # Title Bar
    "titlebar_height": 40,
    "titlebar_button_width": 50,
}

# ============================================================
# BUTTON STYLES
# ============================================================

BUTTON_STYLES = {
    "primary": {
        "fg_color": COLORS["primary"],
        "hover_color": COLORS["primary_hover"],
        "text_color": COLORS["text_primary"],
        "border_width": 0,
    },
    "success": {
        "fg_color": COLORS["success"],
        "hover_color": COLORS["success_hover"],
        "text_color": COLORS["text_primary"],
        "border_width": 0,
    },
    "danger": {
        "fg_color": COLORS["danger"],
        "hover_color": COLORS["danger_hover"],
        "text_color": COLORS["text_primary"],
        "border_width": 0,
    },
    "warning": {
        "fg_color": COLORS["warning"],
        "hover_color": COLORS["warning_hover"],
        "text_color": COLORS["text_primary"],
        "border_width": 0,
    },
    "secondary": {
        "fg_color": COLORS["secondary"],
        "hover_color": COLORS["secondary_hover"],
        "text_color": COLORS["text_primary"],
        "border_width": 0,
    },
    "transparent": {
        "fg_color": "transparent",
        "hover_color": COLORS["bg_light"],
        "text_color": COLORS["text_secondary"],
        "border_width": 1,
        "border_color": COLORS["border_medium"],
    },
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_color(name: str, default: tuple = None):
    """Get color by name"""
    return COLORS.get(name, default or COLORS["text_primary"])

def get_font_size(name: str, default: int = None):
    """Get font size by name"""
    return FONTS.get(name, default or FONTS["size_normal"])

def get_spacing(name: str, default: int = None):
    """Get spacing by name"""
    return SPACING.get(name, default or SPACING["md"])

def get_size(name: str, default: int = None):
    """Get size by name"""
    return SIZES.get(name, default or 0)

def get_button_style(style: str):
    """Get button style configuration"""
    return BUTTON_STYLES.get(style, BUTTON_STYLES["primary"])

def apply_theme():
    """Apply global theme settings"""
    debug("Theme", "Applying global theme")
    import customtkinter as ctk
    
    # Set appearance mode
    ctk.set_appearance_mode("dark")
    
    # Set default color theme
    ctk.set_default_color_theme("blue")
    
    info("Theme", "Global theme applied successfully")


# ============================================================
# THEME DOCUMENTATION
# ============================================================

THEME_GUIDE = """
MultiTeam Design Theme Guide
============================

COLORS:
- Primary: Blue (#1f6aa5) - Main actions, links
- Success: Green (#107c10) - Confirmations, success states
- Danger: Red (#c42b1c) - Errors, destructive actions
- Warning: Orange (#f7630c) - Warnings, cautions
- Secondary: Gray (#4a4a4a) - Secondary actions

TYPOGRAPHY:
- Font Family: Segoe UI (Windows standard)
- Monospace: Courier New (for codes, tokens)
- Sizes: 9-64px (tiny to icon_large)

SPACING:
- xs: 3px, sm: 5px, md: 10px, lg: 15px, xl: 20px, xxl: 30px, xxxl: 40px

COMPONENTS:
- Buttons: 35-45px height, rounded corners
- Inputs: 40px height, consistent width
- Checkboxes: 20px size
- Border radius: 6px standard

USAGE:
from core.theme import COLORS, FONTS, SPACING, SIZES, get_color, get_button_style

# Get colors
primary_color = get_color("primary")
text_color = get_color("text_primary")

# Get button style
style = get_button_style("success")

# Use in components
button = CustomButton(..., **style)
"""

if __name__ == "__main__":
    info("TEST", "Theme module loaded")
    print(THEME_GUIDE)
    apply_theme()

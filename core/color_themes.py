"""
Color Themes for Multi Team -C
5 olika färgteman som kan väljas i settings
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class ColorTheme:
    """Color theme dataclass"""
    name: str
    # Primära färger
    BACKGROUND: str
    SURFACE: str
    SURFACE_VARIANT: str
    PRIMARY: str
    PRIMARY_HOVER: str
    SECONDARY: str
    SECONDARY_HOVER: str
    
    # Text färger
    TEXT: str
    TEXT_SECONDARY: str
    TEXT_DISABLED: str
    
    # Status färger
    SUCCESS: str
    WARNING: str
    ERROR: str
    INFO: str
    
    # UI Element färger
    BORDER: str
    HOVER: str
    ACTIVE: str


# ============================================================================
# TEMA 1: DARK BLUE (NUVARANDE/DEFAULT)
# ============================================================================
DARK_BLUE = ColorTheme(
    name="Dark Blue",
    # Primära färger
    BACKGROUND="#1a1a1a",
    SURFACE="#2b2b2b",
    SURFACE_VARIANT="#1f1f1f",
    PRIMARY="#1f6aa5",
    PRIMARY_HOVER="#2980b9",
    SECONDARY="#3a3a3a",
    SECONDARY_HOVER="#4a4a4a",
    
    # Text färger
    TEXT="#ffffff",
    TEXT_SECONDARY="#b0b0b0",
    TEXT_DISABLED="#666666",
    
    # Status färger
    SUCCESS="#388e3c",
    WARNING="#f5c542",
    ERROR="#d32f2f",
    INFO="#1f6aa5",
    
    # UI Element färger
    BORDER="#3a3a3a",
    HOVER="#2a2a2a",
    ACTIVE="#353535"
)


# ============================================================================
# TEMA 2: MIDNIGHT PURPLE
# ============================================================================
MIDNIGHT_PURPLE = ColorTheme(
    name="Midnight Purple",
    # Primära färger - Mörk lila/purple tema
    BACKGROUND="#1a1520",
    SURFACE="#2a2030",
    SURFACE_VARIANT="#1f1a25",
    PRIMARY="#7c3aed",  # Djup lila
    PRIMARY_HOVER="#8b5cf6",
    SECONDARY="#3a2f45",
    SECONDARY_HOVER="#4a3f55",
    
    # Text färger
    TEXT="#ffffff",
    TEXT_SECONDARY="#c4b5fd",  # Ljus lila tint
    TEXT_DISABLED="#6b5b7b",
    
    # Status färger
    SUCCESS="#10b981",  # Grön
    WARNING="#f59e0b",  # Orange
    ERROR="#ef4444",    # Röd
    INFO="#7c3aed",     # Lila
    
    # UI Element färger
    BORDER="#3a2f45",
    HOVER="#2a2535",
    ACTIVE="#3a3545"
)


# ============================================================================
# TEMA 3: FOREST GREEN
# ============================================================================
FOREST_GREEN = ColorTheme(
    name="Forest Green",
    # Primära färger - Mörk grön/natur tema
    BACKGROUND="#161d16",
    SURFACE="#1f2b1f",
    SURFACE_VARIANT="#1a221a",
    PRIMARY="#059669",  # Smaragdgrön
    PRIMARY_HOVER="#10b981",
    SECONDARY="#2d3a2d",
    SECONDARY_HOVER="#3d4a3d",
    
    # Text färger
    TEXT="#ffffff",
    TEXT_SECONDARY="#a7f3d0",  # Ljus grön tint
    TEXT_DISABLED="#5a6a5a",
    
    # Status färger
    SUCCESS="#10b981",  # Grön
    WARNING="#fbbf24",  # Gul
    ERROR="#ef4444",    # Röd
    INFO="#06b6d4",     # Cyan
    
    # UI Element färger
    BORDER="#2d3a2d",
    HOVER="#252f25",
    ACTIVE="#303d30"
)


# ============================================================================
# TEMA 4: CRIMSON RED
# ============================================================================
CRIMSON_RED = ColorTheme(
    name="Crimson Red",
    # Primära färger - Mörk röd/energisk tema
    BACKGROUND="#1d1416",
    SURFACE="#2b1f21",
    SURFACE_VARIANT="#221a1c",
    PRIMARY="#dc2626",  # Djup röd
    PRIMARY_HOVER="#ef4444",
    SECONDARY="#3a2f31",
    SECONDARY_HOVER="#4a3f41",
    
    # Text färger
    TEXT="#ffffff",
    TEXT_SECONDARY="#fca5a5",  # Ljus röd tint
    TEXT_DISABLED="#6a5a5c",
    
    # Status färger
    SUCCESS="#10b981",  # Grön
    WARNING="#f59e0b",  # Orange
    ERROR="#dc2626",    # Röd
    INFO="#3b82f6",     # Blå
    
    # UI Element färger
    BORDER="#3a2f31",
    HOVER="#2a2526",
    ACTIVE="#353035"
)


# ============================================================================
# TEMA 5: OCEAN TEAL
# ============================================================================
OCEAN_TEAL = ColorTheme(
    name="Ocean Teal",
    # Primära färger - Mörk cyan/ocean tema
    BACKGROUND="#14191d",
    SURFACE="#1e2a2f",
    SURFACE_VARIANT="#192025",
    PRIMARY="#0891b2",  # Djup cyan/teal
    PRIMARY_HOVER="#06b6d4",
    SECONDARY="#2f3a3f",
    SECONDARY_HOVER="#3f4a4f",
    
    # Text färger
    TEXT="#ffffff",
    TEXT_SECONDARY="#a5f3fc",  # Ljus cyan tint
    TEXT_DISABLED="#5a6a6f",
    
    # Status färger
    SUCCESS="#10b981",  # Grön
    WARNING="#f59e0b",  # Orange
    ERROR="#ef4444",    # Röd
    INFO="#0891b2",     # Cyan
    
    # UI Element färger
    BORDER="#2f3a3f",
    HOVER="#252f34",
    ACTIVE="#303a3f"
)


# ============================================================================
# TEMA DICTIONARY
# ============================================================================
THEMES: Dict[str, ColorTheme] = {
    "dark_blue": DARK_BLUE,
    "midnight_purple": MIDNIGHT_PURPLE,
    "forest_green": FOREST_GREEN,
    "crimson_red": CRIMSON_RED,
    "ocean_teal": OCEAN_TEAL
}

# Default tema
DEFAULT_THEME = "dark_blue"


def get_theme(theme_name: str = DEFAULT_THEME) -> ColorTheme:
    """
    Hämta ett färgtema
    
    Args:
        theme_name: Namnet på temat (dark_blue, midnight_purple, etc.)
        
    Returns:
        ColorTheme objekt
    """
    return THEMES.get(theme_name, DARK_BLUE)


def get_available_themes() -> list[str]:
    """
    Hämta lista över tillgängliga teman
    
    Returns:
        Lista med tema-namn
    """
    return list(THEMES.keys())


def get_theme_display_names() -> Dict[str, str]:
    """
    Hämta display-namn för alla teman
    
    Returns:
        Dictionary med theme_id: display_name
    """
    return {key: theme.name for key, theme in THEMES.items()}


# Export
__all__ = [
    'ColorTheme',
    'DARK_BLUE',
    'MIDNIGHT_PURPLE',
    'FOREST_GREEN',
    'CRIMSON_RED',
    'OCEAN_TEAL',
    'THEMES',
    'DEFAULT_THEME',
    'get_theme',
    'get_available_themes',
    'get_theme_display_names'
]

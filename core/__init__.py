"""
Core Package - Kärnfunktionalitet för MultiTeam (PyQt6)
"""

from core.debug_logger import debug, info, warning, error, exception, logger
from core.pyqt_window_new import CustomWindow, CustomTitleBar
from core.custom_dialog import show_info, show_error, show_warning, show_question, show_login_success
from core.auth_system import AuthSystem
from core.email_service import EmailService
from core.global_settings import GlobalSettings, settings
from core.twofa_system import TwoFASystem
from core.pyqt_theme import Theme
from core.version import get_version, version_manager

__all__ = [
    # Logger
    'debug', 'info', 'warning', 'error', 'exception', 'logger',
    # Windows (PyQt6)
    'CustomWindow', 'CustomTitleBar',
    # Dialogs (PyQt6)
    'show_info', 'show_error', 'show_warning', 'show_question', 'show_login_success',
    # Systems
    'AuthSystem', 'EmailService', 'GlobalSettings', 'settings', 'TwoFASystem',
    # Theme (PyQt6)
    'Theme',
    # Version
    'get_version', 'version_manager'
]

__version__ = '0.1.0'
__author__ = 'MultiTeam Development Team'

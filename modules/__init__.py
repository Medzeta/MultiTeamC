"""
Modules Package - Applikationsmoduler för MultiTeam
"""

from modules.login_module import LoginModule
from modules.registration_module import RegistrationModule
from modules.settings_module import SettingsModule
from modules.twofa_setup_module import TwoFASetupModule
from modules.twofa_verify_module import TwoFAVerifyModule

__all__ = [
    'LoginModule',
    'RegistrationModule',
    'SettingsModule',
    'TwoFASetupModule',
    'TwoFAVerifyModule'
]

__version__ = '0.1.0'

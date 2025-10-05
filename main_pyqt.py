"""
MultiTeam P2P Communication - PyQt6 Version
Main entry point for PyQt6 application with REAL rounded corners!
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from core.pyqt_theme import Theme
from core.debug_logger import debug, info, error, warning
from core.pyqt_window_new import CustomWindow
from core.auto_update_manager import AutoUpdateManager
from modules_pyqt.modern_login_module import ModernLoginModule
from modules_pyqt.new_registration_module import NewRegistrationModule
from modules_pyqt.auto_update_module import AutoUpdateModule

# Fix for PyInstaller EXE - ensure Qt plugins are found
if hasattr(sys, '_MEIPASS'):
    # Running in PyInstaller bundle
    os.environ['QT_PLUGIN_PATH'] = os.path.join(sys._MEIPASS, 'PyQt6', 'Qt6', 'plugins')
    debug("MAIN", f"PyInstaller detected - Qt plugin path: {os.environ.get('QT_PLUGIN_PATH')}")


class MultiTeamApp:
    """Main application class"""
    
    def __init__(self):
        """Initialize application"""
        info("MultiTeamApp", "=" * 60)
        info("MultiTeamApp", "Starting MultiTeam P2P Communication (PyQt6)")
        info("MultiTeamApp", "=" * 60)
        
        self.window = None
        self.current_module = None
        self.auto_update_manager = None
        
        self._setup_app()
    
    def _setup_app(self):
        """Setup application"""
        debug("MultiTeamApp", "Setting up application")
        
        # Create main window
        from core.pyqt_window_new import CustomWindow
        self.window = CustomWindow()
        
        # Connect logout signal
        self.window.titlebar.logout_clicked.connect(self._handle_logout)
        
        # Show login module
        self._show_login()
        
        # Show window
        self.window.show()
        debug("MultiTeamApp", "Window shown successfully")
        
        # Initialize auto-update manager
        self._setup_auto_update()
        
        debug("MultiTeamApp", "Application initialized successfully")
        info("MultiTeamApp", "Application initialized successfully")
        
        # Initialize 2FA flags
        self._offer_2fa_setup_after_popup = False
        self.current_user = None
    
    def _handle_logout(self):
        """Handle logout"""
        debug("MultiTeamApp", "Logout requested")
        
        # Clear current user
        self.current_user = None
        
        # Reset titlebar user info
        self.window.titlebar.update_user_info(None)
        
        # Show login module
        info("MultiTeamApp", "User logged out, showing login")
        self._show_login()
    
    def _show_login(self):
        """Show login module"""
        info("MultiTeamApp", "Showing login module")
        login_module = ModernLoginModule()
        login_module.login_success.connect(self._handle_login_success)
        login_module.register_clicked.connect(self._show_registration)
        login_module.forgot_password_clicked.connect(self._show_forgot_password)
        login_module.license_clicked.connect(self._show_license_activation)
        
        self.current_module = login_module
        self.window.set_content(login_module)
        
        debug("MultiTeamApp", "Login module displayed")
    
    def _handle_login_success(self, user):
        """Handle successful login"""
        info("MultiTeamApp", f"Login successful: {user['email']}")
        debug("MultiTeamApp", "Starting login success handling")
        
        # Spara current user för 2FA setup
        self.current_user = user
        
        # Debug: Visa användarens 2FA-status
        debug("MultiTeamApp", f"User 2FA status: twofa_enabled={user.get('twofa_enabled')}")
        
        # SuperAdmin hoppar över 2FA
        if user.get('email') == '1':  # SuperAdmin
            debug("MultiTeamApp", "SuperAdmin login - skipping 2FA")
            self._offer_2fa_setup_after_popup = False
        # Kolla om användaren har 2FA aktiverat
        elif user.get('twofa_enabled'):
            debug("MultiTeamApp", f"User {user['email']} has 2FA enabled - showing verify module")
            self._show_2fa_verify(user)
            return
        else:
            debug("MultiTeamApp", f"User {user['email']} does not have 2FA - will offer setup")
            # Erbjud 2FA setup för alla användare utan 2FA
            self._offer_2fa_setup_after_popup = True
        
        # Logga inloggningen i historiken
        from core.login_history import login_history
        login_history.log_login(user['email'], user.get('name', user['email']))
        
        # Hämta senaste inloggning (föregående) för denna användare
        user_email_for_stats = user.get('email', 'Unknown')
        last_login = login_history.get_last_login(user_email_for_stats, exclude_current=True)
        debug("MultiTeamApp", f"Last login data for {user_email_for_stats}: {last_login}")
        
        # Hämta statistik för denna användare
        stats = login_history.get_login_stats(user_email_for_stats)
        debug("MultiTeamApp", f"Login stats for {user_email_for_stats}: {stats}")
        
        # Hämta belöningsmeddelande
        achievement = login_history.get_achievement_message(stats)
        debug("MultiTeamApp", f"Achievement: {achievement}")
        
        # Uppdatera användarinfo i titlebar
        self.window.titlebar.update_user_info(user.get('name', user['email']))
        
        # Simulera nätverksstatistik (TODO: ersätt med riktiga värden från P2P-systemet)
        team_online = 3  # Antal online i teamet
        team_total = 5   # Totalt antal i teamet
        peers_online = 12  # Antal online peers totalt
        peers_total = 18   # Totalt antal peers i nätverket
        
        # Uppdatera titlebar stats
        self.window.titlebar.update_peer_stats(team_online, team_total, peers_online, peers_total)
        
        # Skapa meddelande med nätverksstatistik (samma formatering som topbar)
        network_stats_html = f"""
        <span style='color: #b0b0b0;'>Team: </span>
        <span style='color: #388e3c; font-weight: 500;'>{team_online}</span>
        <span style='color: #b0b0b0;'> / </span>
        <span style='color: #666666;'>{team_total}</span>
        <span style='color: #b0b0b0;'> online  •  Peers: </span>
        <span style='color: #388e3c; font-weight: 500;'>{peers_online}</span>
        <span style='color: #b0b0b0;'> / </span>
        <span style='color: #666666;'>{peers_total}</span>
        <span style='color: #b0b0b0;'> online</span>
        """
        
        # Skapa last login information
        last_login_html = ""
        if last_login:
            last_login_html = f"""
<br><br><span style='color: #b0b0b0;'>Last Login:</span><br>
<span style='color: #888888;'>{last_login['formatted_date']} at {last_login['formatted_time']}</span>
<span style='color: #666666;'> ({last_login['weekday']})</span>"""
        else:
            # Visa total antal inloggningar istället
            total_logins = stats.get('total_logins', 1)
            if total_logins == 1:
                last_login_html = f"""
<br><br><span style='color: #b0b0b0;'>Welcome!</span><br>
<span style='color: #888888;'>This is your first login</span>"""
            else:
                last_login_html = f"""
<br><br><span style='color: #b0b0b0;'>Login History:</span><br>
<span style='color: #888888;'>Total logins: {total_logins}</span>"""
        
        # Separator mellan network status och achievements
        separator_html = """
<br><br><span style='color: #444444;'>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>"""
        
        # Skapa belöningssektion (utan emojis)
        achievement_html = f"""
<br><br><span style='color: #b0b0b0;'>Achievement Unlocked:</span><br>
<span style='color: #1f6aa5; font-weight: bold;'>{achievement['title']}</span><br>
<span style='color: #888888;'>{achievement['message']}</span>"""
        
        # Skapa statistik sektion (utan emojis)
        stats_html = f"""
<br><br><span style='color: #b0b0b0;'>Your Stats:</span><br>
<span style='color: #888888;'>Today: {stats['today_logins']} • This week: {stats['week_logins']} • Total: {stats['total_logins']}</span>"""
        
        # Hämta samma UID-format som topbaren
        import uuid
        import platform
        
        # Windows Maskin UID (samma som topbar)
        node = uuid.getnode()
        mac_bytes = []
        for i in range(6):
            mac_bytes.append('{:02x}'.format((node >> (i * 8)) & 0xff))
        machine_uid = ':'.join(reversed(mac_bytes))
        computer_name = platform.node()
        uid_text = f"{computer_name} | UID: {machine_uid}"
        
        # Skapa användarinfo sektion med riktig email
        user_email = user.get('email', 'Unknown')
        # Om SuperAdmin (email = "1"), visa en riktig email istället
        if user_email == "1":
            user_email = "admin@multiteam.com"
        
        user_info_html = f"""
<br><br><span style='color: #888888;'>Welcome back, <b>{user.get('name', 'Unknown')}</b>!</span><br>
<span style='color: #888888;'>{user_email}</span><br>
<span style='color: #888888;'>{uid_text}</span>"""
        
        welcome_message = f"""<br><br><span style='color: #b0b0b0;'>Network Status:</span><br>
{network_stats_html}{separator_html}{user_info_html}{achievement_html}{stats_html}{last_login_html}"""
        
        debug("MultiTeamApp", f"Welcome message length: {len(welcome_message)} characters")
        debug("MultiTeamApp", f"Welcome message preview: {welcome_message[:200]}...")
        debug("MultiTeamApp", "About to show login success popup")
        try:
            from core.custom_dialog import show_info
            show_info(
                self.window,
                "Login Successful!",
                welcome_message,
                large=True
            )
            debug("MultiTeamApp", "Login success popup shown successfully")
        except Exception as e:
            error("MultiTeamApp", f"Error showing login success popup: {e}")
            import traceback
            error("MultiTeamApp", f"Traceback: {traceback.format_exc()}")
        
        # Kolla om vi ska erbjuda 2FA setup efter popup
        if self._offer_2fa_setup_after_popup:
            debug("MultiTeamApp", "Offering 2FA setup after popup")
            self._offer_2fa_setup(user)
        else:
            self._show_dashboard()
    
    def _show_login_success_popup(self, user):
        """Visa endast login success popup utan navigation"""
        debug("MultiTeamApp", "Showing login success popup only")
        
        # Hämta statistik för denna användare
        user_email_for_stats = user.get('email', 'Unknown')
        from core.login_history import login_history
        stats = login_history.get_login_stats(user_email_for_stats)
        last_login = login_history.get_last_login(user_email_for_stats, exclude_current=True)
        achievement = login_history.get_achievement_message(stats)
        
        # Uppdatera användarinfo i titlebar
        self.window.titlebar.update_user_info(user.get('name', user['email']))
        
        # Simulera nätverksstatistik
        team_online = 3
        team_total = 5
        peers_online = 12
        peers_total = 18
        
        # Uppdatera titlebar stats
        self.window.titlebar.update_peer_stats(team_online, team_total, peers_online, peers_total)
        
        # Skapa welcome message (samma som tidigare)
        network_stats_html = f"""
        <span style='color: #b0b0b0;'>Team: </span>
        <span style='color: #388e3c; font-weight: 500;'>{team_online}</span>
        <span style='color: #b0b0b0;'> / </span>
        <span style='color: #666666;'>{team_total}</span>
        <span style='color: #b0b0b0;'> online  •  Peers: </span>
        <span style='color: #388e3c; font-weight: 500;'>{peers_online}</span>
        <span style='color: #b0b0b0;'> / </span>
        <span style='color: #666666;'>{peers_total}</span>
        <span style='color: #b0b0b0;'> online</span>
        """
        
        # Skapa last login information
        last_login_html = ""
        if last_login:
            last_login_html = f"""
<br><br><span style='color: #b0b0b0;'>Last Login:</span><br>
<span style='color: #888888;'>{last_login['formatted_date']} at {last_login['formatted_time']}</span>
<span style='color: #666666;'> ({last_login['weekday']})</span>"""
        else:
            total_logins = stats.get('total_logins', 1)
            if total_logins == 1:
                last_login_html = f"""
<br><br><span style='color: #b0b0b0;'>Welcome!</span><br>
<span style='color: #888888;'>This is your first login</span>"""
            else:
                last_login_html = f"""
<br><br><span style='color: #b0b0b0;'>Login History:</span><br>
<span style='color: #888888;'>Total logins: {total_logins}</span>"""
        
        # Separator mellan network status och achievements
        separator_html = """
<br><br><span style='color: #444444;'>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>"""
        
        # Skapa belöningssektion
        achievement_html = f"""
<br><br><span style='color: #b0b0b0;'>Achievement Unlocked:</span><br>
<span style='color: #1f6aa5; font-weight: bold;'>{achievement['title']}</span><br>
<span style='color: #888888;'>{achievement['message']}</span>"""
        
        # Skapa statistik sektion
        stats_html = f"""
<br><br><span style='color: #b0b0b0;'>Your Stats:</span><br>
<span style='color: #888888;'>Today: {stats['today_logins']} • This week: {stats['week_logins']} • Total: {stats['total_logins']}</span>"""
        
        # Hämta samma UID-format som topbaren
        import uuid
        import platform
        
        # Windows Maskin UID (samma som topbar)
        node = uuid.getnode()
        mac_bytes = []
        for i in range(6):
            mac_bytes.append('{:02x}'.format((node >> (i * 8)) & 0xff))
        machine_uid = ':'.join(reversed(mac_bytes))
        computer_name = platform.node()
        uid_text = f"{computer_name} | UID: {machine_uid}"
        
        # Skapa användarinfo sektion med riktig email
        user_email = user.get('email', 'Unknown')
        # Om SuperAdmin (email = "1"), visa en riktig email istället
        if user_email == "1":
            user_email = "admin@multiteam.com"
        
        user_info_html = f"""
<br><br><span style='color: #888888;'>Welcome back, <b>{user.get('name', 'Unknown')}</b>!</span><br>
<span style='color: #888888;'>{user_email}</span><br>
<span style='color: #888888;'>{uid_text}</span>"""
        
        welcome_message = f"""<br><br><span style='color: #b0b0b0;'>Network Status:</span><br>
{network_stats_html}{separator_html}{user_info_html}{achievement_html}{stats_html}{last_login_html}"""
        
        try:
            from core.custom_dialog import show_info
            show_info(
                self.window,
                "Login Successful!",
                welcome_message,
                large=True
            )
            debug("MultiTeamApp", "Login success popup shown successfully")
        except Exception as e:
            error("MultiTeamApp", f"Error showing login success popup: {e}")
    
    def _offer_2fa_setup(self, user):
        """Erbjud 2FA setup för första gången användare"""
        debug("MultiTeamApp", f"Offering 2FA setup to user: {user['email']}")
        
        from core.custom_dialog import show_question
        
        result = show_question(
            self.window,
            "Enable Two-Factor Authentication",
            f"For enhanced security, we recommend enabling Two-Factor Authentication (2FA).\n\n2FA adds an extra layer of protection using Google Authenticator.\n\nWould you like to set up 2FA now?",
            large=True
        )
        
        if result:
            debug("MultiTeamApp", "User accepted 2FA setup")
            self._show_2fa_setup(user)
        else:
            debug("MultiTeamApp", "User declined 2FA setup")
            self._show_dashboard()
    
    def _show_dashboard(self):
        """Show main dashboard with module cards"""
        debug("MultiTeamApp", "Showing main dashboard with module cards")
        
        from modules_pyqt.main_dashboard_module import MainDashboardModule
        
        # Skapa dashboard med användarkontext
        dashboard = MainDashboardModule(current_user=self.current_user)
        dashboard.module_selected.connect(self._handle_module_selection)
        
        self.current_module = dashboard
        self.window.set_content(dashboard)
        
        info("MultiTeamApp", "Main dashboard displayed successfully")
    
    def _handle_module_selection(self, module_id: str):
        """Hantera val av modul från dashboard - dynamiskt system"""
        info("MultiTeamApp", f"Module selected: {module_id}")
        
        # Kontrollera SuperAdmin-behörighet
        if module_id == 'superadmin_settings':
            if not self.current_user or self.current_user.get('username', '').lower() != 'superadmin':
                warning("MultiTeamApp", "Unauthorized access attempt to SuperAdmin Settings")
                return
        
        # Specialhantering för vissa moduler
        if module_id == 'settings':
            self._show_auto_update_module()
        else:
            # Dynamiskt system - visa undersida för alla moduler
            self._show_dynamic_module_page(module_id)
    
    def _show_dynamic_module_page(self, module_id: str):
        """Visa dynamisk undersida för en modul"""
        debug("MultiTeamApp", f"Showing dynamic page for: {module_id}")
        
        from modules_pyqt.dynamic_module_page import DynamicModulePage
        
        # Hämta modul-data från dashboard
        if hasattr(self, 'current_module') and hasattr(self.current_module, '_get_available_modules'):
            modules = self.current_module._get_available_modules()
            module_data = next((m for m in modules if m['id'] == module_id), None)
            
            if module_data:
                # Skapa dynamisk undersida med modul-data
                page = DynamicModulePage(
                    module_id=module_data['id'],
                    module_title=module_data['title'],
                    image_name=module_data.get('image')
                )
                
                # Koppla tillbaka-signal
                page.back_clicked.connect(self._show_dashboard)
                
                # Visa sidan
                self.window.set_content(page)
                info("MultiTeamApp", f"Dynamic page displayed for: {module_data['title']}")
            else:
                warning("MultiTeamApp", f"Module data not found for: {module_id}")
                self._show_dashboard()
        else:
            warning("MultiTeamApp", "Cannot access module data")
            self._show_dashboard()
    
    def _show_auto_update_module(self):
        """Visa auto-update modul"""
        debug("MultiTeamApp", "Showing auto-update module")
        
        # Skapa auto-update modul
        update_module = AutoUpdateModule()
        
        # Koppla signaler
        update_module.back_clicked.connect(self._show_dashboard)
        update_module.restart_required.connect(self._handle_restart_required)
        
        # Visa modulen
        self.window.set_content(update_module)
        info("MultiTeamApp", "Auto-update module displayed")
    
    def _handle_restart_required(self):
        """Hantera restart-begäran från auto-update"""
        info("MultiTeamApp", "Application restart requested by auto-updater")
        # Här kan vi lägga till cleanup-kod innan restart
        # För nu låter vi auto-update modulen hantera restart
    
    def _show_superadmin_settings(self):
        """Visa SuperAdmin Settings modul"""
        debug("MultiTeamApp", "Showing SuperAdmin Settings")
        
        # TODO: Implementera riktig SuperAdmin Settings modul
        self._show_placeholder_module("SuperAdmin Settings", "⚙️", 
                                    "Advanced system configuration and user management.")
    
    def _show_placeholder_module(self, title: str, icon: str, description: str = None):
        """Visa placeholder för moduler som inte är implementerade än"""
        debug("MultiTeamApp", f"Showing placeholder for: {title}")
        
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QFont
        
        placeholder = QWidget()
        layout = QVBoxLayout(placeholder)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        # Icon
        icon_label = QLabel(icon)
        icon_font = QFont()
        icon_font.setPointSize(48)
        icon_label.setFont(icon_font)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Titel
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title_label)
        
        # Beskrivning
        if description:
            desc_label = QLabel(description)
            desc_font = QFont()
            desc_font.setPointSize(14)
            desc_label.setFont(desc_font)
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_label.setStyleSheet("color: #7f8c8d;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        # Status meddelande
        status_label = QLabel("This module is coming soon!")
        status_font = QFont()
        status_font.setPointSize(16)
        status_font.setItalic(True)
        status_label.setFont(status_font)
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setStyleSheet("color: #e67e22;")
        layout.addWidget(status_label)
        
        # Tillbaka-knapp
        back_btn = QPushButton("← Back to Dashboard")
        from core.pyqt_theme import Theme
        Theme.setup_login_button(back_btn, width=200)
        back_btn.clicked.connect(self._show_dashboard)
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.current_module = placeholder
        self.window.set_content(placeholder)
    
    def _show_registration(self):
        """Show registration module"""
        info("MultiTeamApp", "Showing registration module")
        debug("MultiTeamApp", "Creating ModernRegistrationModule")
        
        registration_module = NewRegistrationModule()
        registration_module.registration_complete.connect(self._handle_registration_complete)
        registration_module.back_to_login.connect(self._show_login)
        
        self.current_module = registration_module
        self.window.set_content(registration_module)
        
        debug("MultiTeamApp", "Registration module displayed")
    
    def _handle_registration_complete(self, email):
        """Handle successful registration"""
        info("MultiTeamApp", f"Registration completed for: {email}")
        debug("MultiTeamApp", "Navigating back to login with pre-filled email")
        
        # Show login with pre-filled email
        login_module = ModernLoginModule()
        login_module.login_success.connect(self._handle_login_success)
        login_module.register_clicked.connect(self._show_registration)
        login_module.forgot_password_clicked.connect(self._show_forgot_password)
        login_module.license_clicked.connect(self._show_license_activation)
        
        # Pre-fill email
        login_module.set_email(email)
        
        self.current_module = login_module
        self.window.set_content(login_module)
        debug("MultiTeamApp", "Login module displayed with pre-filled email")
    
    def _show_forgot_password(self):
        """Show forgot password module"""
        info("MultiTeamApp", "Showing forgot password module")
        
        from modules_pyqt.forgot_password_module import ForgotPasswordModule
        
        forgot_password_module = ForgotPasswordModule()
        forgot_password_module.back_to_login.connect(self._show_login)
        forgot_password_module.password_reset_success.connect(self._handle_password_reset_success)
        
        self.current_module = forgot_password_module
        self.window.set_content(forgot_password_module)
        
        debug("MultiTeamApp", "Forgot password module displayed")
    
    def _handle_password_reset_success(self):
        """Handle successful password reset"""
        info("MultiTeamApp", "Password reset successful - returning to login")
        self._show_login()
    
    def _show_license_activation(self):
        """Show license activation"""
        info("MultiTeamApp", "Showing license activation")
        
        from modules_pyqt.license_activation_module import LicenseActivationModule
        
        # Pass current_user to associate licenses with logged-in user
        license_module = LicenseActivationModule(current_user=self.current_user)
        license_module.activation_success.connect(self._handle_license_activation_success)
        license_module.back_to_login.connect(self._show_login)
        license_module.application_clicked.connect(self._show_license_application)
        
        self.current_module = license_module
        self.window.set_content(license_module)
        
        debug("MultiTeamApp", "License activation module displayed")
    
    def _show_license_application(self, machine_uid):
        """Show license application module"""
        info("MultiTeamApp", "Showing license application")
        
        from modules_pyqt.license_application_module import LicenseApplicationModule
        
        # Pass current_user to pre-fill form and associate application with user
        app_module = LicenseApplicationModule(machine_uid=machine_uid, current_user=self.current_user)
        app_module.application_submitted.connect(self._handle_application_submitted)
        app_module.back_to_license.connect(self._show_license_activation)
        
        self.current_module = app_module
        self.window.set_content(app_module)
        
        debug("MultiTeamApp", "License application module displayed")
    
    def _handle_application_submitted(self):
        """Handle successful license application"""
        info("MultiTeamApp", "License application submitted - returning to license activation")
        self._show_license_activation()
    
    def _handle_license_activation_success(self):
        """Handle successful license activation"""
        info("MultiTeamApp", "License activation successful")
        
        from core.custom_dialog import show_info
        show_info(
            self.window,
            "Activation Successful",
            "License activated successfully!\n\nYou can now log in to the application."
        )
        
        # Return to login
        self._show_login()
    
    def _show_2fa_verify(self, user):
        """Visa 2FA verifiering"""
        debug("MultiTeamApp", f"Showing 2FA verify for user: {user['email']}")
        
        try:
            from modules_pyqt.twofa_verify_module import TwoFAVerifyModule
            
            twofa_verify = TwoFAVerifyModule(user)
            twofa_verify.verification_success.connect(self._handle_2fa_success)
            twofa_verify.back_to_login.connect(self._show_login)
            
            self.current_module = twofa_verify
            self.window.set_content(twofa_verify)
            
            info("MultiTeamApp", "2FA verify module displayed")
            
        except Exception as e:
            error("MultiTeamApp", f"Error showing 2FA verify: {e}")
            self._show_login()
    
    def _handle_2fa_success(self, user):
        """Hantera lyckad 2FA verifiering"""
        debug("MultiTeamApp", f"2FA verification successful for: {user['email']}")
        
        # Fortsätt med normal login success hantering
        self._continue_login_success(user)
    
    def _show_2fa_setup(self, user):
        """Visa 2FA setup"""
        debug("MultiTeamApp", f"Showing 2FA setup for user: {user['email']}")
        
        try:
            from modules_pyqt.twofa_setup_module import TwoFASetupModule
            
            twofa_setup = TwoFASetupModule(user)
            twofa_setup.setup_completed.connect(lambda: self._handle_2fa_setup_complete(user))
            twofa_setup.back_to_settings.connect(self._show_dashboard)
            
            self.current_module = twofa_setup
            self.window.set_content(twofa_setup)
            
            info("MultiTeamApp", "2FA setup module displayed")
            
        except Exception as e:
            error("MultiTeamApp", f"Error showing 2FA setup: {e}")
            self._show_dashboard()
    
    def _handle_2fa_setup_complete(self, user):
        """Hantera slutförd 2FA setup"""
        debug("MultiTeamApp", f"2FA setup completed for: {user['email']}")
        
        # Uppdatera current_user med 2FA aktiverat
        if self.current_user and self.current_user.get('email') == user.get('email'):
            self.current_user['twofa_enabled'] = True
            debug("MultiTeamApp", f"Updated current_user 2FA status to enabled for: {user['email']}")
        
        # Gå direkt till dashboard utan popup för att undvika UI-bugg
        debug("MultiTeamApp", "2FA setup completed - going directly to dashboard")
        self._show_dashboard()
        
        # Logga framgången istället för popup
        info("MultiTeamApp", f"✅ 2FA successfully activated for {user['email']} - User can now use 2FA for login")
    
    def _continue_login_success(self, user):
        """Fortsätt med login success efter 2FA"""
        debug("MultiTeamApp", "Continuing login success after 2FA verification")
        
        # Logga inloggningen i historiken
        from core.login_history import login_history
        login_history.log_login(user['email'], user.get('name', user['email']))
        
        # Visa login success popup och gå till dashboard
        self._show_login_success_popup(user)
        self._show_dashboard()
    
    def _setup_auto_update(self):
        """Setup automatisk uppdateringshantering"""
        info("MultiTeamApp", "Setting up auto-update manager")
        
        try:
            # Skapa auto-update manager
            self.auto_update_manager = AutoUpdateManager(parent=self.window)
            
            # Starta automatisk övervakning
            self.auto_update_manager.start_monitoring()
            
            info("MultiTeamApp", "Auto-update manager initialized and monitoring started")
            
        except Exception as e:
            error("MultiTeamApp", f"Failed to setup auto-update manager: {e}")


def main():
    """Main entry point"""
    try:
        # PyInstaller EXE fixes
        if hasattr(sys, '_MEIPASS'):
            debug("MAIN", "Running in PyInstaller bundle")
            debug("MAIN", f"Bundle path: {sys._MEIPASS}")
        
        # Create QApplication with proper attributes for EXE
        app = QApplication(sys.argv)
        app.setApplicationName("MultiTeam Communication")
        app.setApplicationVersion("0.20")
        
        # Set Qt attributes for better EXE compatibility (with error handling)
        try:
            app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
            debug("MAIN", "High DPI scaling enabled")
        except Exception as e:
            debug("MAIN", f"Could not enable High DPI scaling: {e}")
        
        try:
            app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
            debug("MAIN", "High DPI pixmaps enabled")
        except Exception as e:
            debug("MAIN", f"Could not enable High DPI pixmaps: {e}")
        
        debug("MAIN", "QApplication created successfully")
        
        # APPLICERA GLOBAL STYLING - KRITISKT FÖR INPUT FÄLT OCH ALL DESIGN
        debug("MAIN", "Applicerar global stylesheet från Theme.get_stylesheet()")
        stylesheet = Theme.get_stylesheet()
        debug("MAIN", f"Stylesheet längd: {len(stylesheet)} tecken")
        debug("MAIN", f"Första 200 tecken av stylesheet: {stylesheet[:200]}")
        
        # KONTROLLERA SCROLLBAR STYLING
        if "QScrollBar:vertical" in stylesheet:
            debug("MAIN", "✓ Scrollbar styling finns i stylesheet")
        else:
            debug("MAIN", "✗ Scrollbar styling SAKNAS i stylesheet!")
            
        if "width: 0px" in stylesheet:
            debug("MAIN", "✓ Scrollbar width: 0px finns i stylesheet")
        else:
            debug("MAIN", "✗ Scrollbar width: 0px SAKNAS i stylesheet!")
            
        app.setStyleSheet(stylesheet)
        debug("MAIN", "Global stylesheet applicerad")
        
        # Create and run app
        debug("MAIN", "Creating MultiTeamApp instance...")
        multiteam_app = MultiTeamApp()
        debug("MAIN", "MultiTeamApp created successfully")
        
        # Ensure window is visible (critical for EXE)
        if multiteam_app.window:
            debug("MAIN", "Ensuring window visibility...")
            multiteam_app.window.show()
            multiteam_app.window.raise_()
            multiteam_app.window.activateWindow()
            debug("MAIN", "Window visibility ensured")
        
        # Start event loop
        debug("MAIN", "Starting Qt event loop...")
        sys.exit(app.exec())
        
    except Exception as e:
        error("MAIN", f"Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

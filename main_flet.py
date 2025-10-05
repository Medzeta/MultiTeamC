"""
MultiTeam P2P Communication - Flet Version
Main entry point for Flet application
"""

import flet as ft
from core.flet_window import CustomWindow
from core.flet_theme import Theme
from core.flet_dialogs import CustomDialog
from core.debug_logger import debug, info, error
from modules_flet.login_module import LoginModule


class MultiTeamApp:
    """Main application class"""
    
    def __init__(self, page: ft.Page):
        """
        Initialize application
        
        Args:
            page: Flet page
        """
        self.page = page
        self.window = None
        self.current_module = None
        
        info("MultiTeamApp", "=" * 60)
        info("MultiTeamApp", "Starting MultiTeam P2P Communication (Flet)")
        info("MultiTeamApp", "=" * 60)
        
        self._setup_app()
    
    def _setup_app(self):
        """Setup application"""
        debug("MultiTeamApp", "Setting up application")
        
        # Create custom window
        self.window = CustomWindow(self.page, "MultiTeam Communication")
        
        # Show login module
        self._show_login()
        
        info("MultiTeamApp", "Application initialized successfully")
    
    def _show_login(self):
        """Show login module"""
        info("MultiTeamApp", "Showing login module")
        
        login_module = LoginModule(
            self.page,
            on_login_success=self._handle_login_success,
            on_register=self._show_registration,
            on_license=self._show_license_activation
        )
        
        self.current_module = login_module
        self.window.set_content(login_module.get_content())
        
        debug("MultiTeamApp", "Login module displayed")
    
    def _handle_login_success(self, user):
        """Handle successful login"""
        info("MultiTeamApp", f"Login successful: {user['email']}")
        
        CustomDialog.show_success(
            self.page,
            "Login Successful!",
            f"Welcome back, {user['name']}!",
            on_close=self._show_dashboard
        )
    
    def _show_dashboard(self):
        """Show dashboard"""
        info("MultiTeamApp", "Showing dashboard")
        
        # Placeholder dashboard
        dashboard = ft.Container(
            content=ft.Column(
                [
                    Theme.text_heading("Dashboard"),
                    ft.Container(height=20),
                    Theme.text_body("Welcome to MultiTeam!"),
                    ft.Container(height=20),
                    Theme.button_primary(
                        "Logout",
                        on_click=lambda e: self._show_login()
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
            alignment=ft.alignment.center,
        )
        
        self.window.set_content(dashboard)
    
    def _show_registration(self):
        """Show registration"""
        info("MultiTeamApp", "Showing registration")
        
        # Placeholder
        CustomDialog.show_info(
            self.page,
            "Registration",
            "Registration module coming soon!"
        )
    
    def _show_license_activation(self):
        """Show license activation"""
        info("MultiTeamApp", "Showing license activation")
        
        # Placeholder
        CustomDialog.show_info(
            self.page,
            "License Activation",
            "License activation module coming soon!"
        )


def main(page: ft.Page):
    """
    Main entry point
    
    Args:
        page: Flet page
    """
    try:
        app = MultiTeamApp(page)
    except Exception as e:
        error("MAIN", f"Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run Flet app
    ft.app(
        target=main,
        view=ft.AppView.FLET_APP,  # Desktop app
    )

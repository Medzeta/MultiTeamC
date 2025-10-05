"""
Flet Login Module
Modern login interface with Material Design
"""

import flet as ft
from core.flet_theme import Theme
from core.flet_dialogs import CustomDialog
from core.debug_logger import debug, info, error
from core.auth_system import AuthSystem
from core.remember_me import RememberMe


class LoginModule:
    """Login module with Flet"""
    
    def __init__(self, page: ft.Page, on_login_success=None, on_register=None, on_license=None):
        """
        Initialize login module
        
        Args:
            page: Flet page
            on_login_success: Callback on successful login
            on_register: Callback for registration
            on_license: Callback for license activation
        """
        self.page = page
        self.on_login_success = on_login_success
        self.on_register = on_register
        self.on_license = on_license
        
        self.auth_system = AuthSystem()
        self.remember_me = RememberMe()
        
        debug("LoginModule", "Initializing login module")
        
        self.content = self._create_ui()
        
        info("LoginModule", "Login module initialized")
    
    def _create_ui(self):
        """Create login UI"""
        debug("LoginModule", "Creating login UI")
        
        # Email input
        self.email_input = Theme.input_field(
            label="Email",
            hint_text="Enter your email",
            prefix_icon="email",
            autofocus=True,
        )
        
        # Password input
        self.password_input = Theme.input_field(
            label="Password",
            password=True,
            can_reveal_password=True,
            hint_text="Enter your password",
            prefix_icon="lock",
        )
        
        # Remember me checkbox
        self.remember_checkbox = ft.Checkbox(
            label="Remember me",
            value=False,
        )
        
        # Login button
        login_btn = Theme.button_primary(
            "Login",
            on_click=self._handle_login,
            width=300,
            height=45,
        )
        
        # Register button
        register_btn = Theme.button_secondary(
            "Create New Account",
            on_click=self._handle_register,
            width=300,
            height=40,
        )
        
        # License activation button
        license_btn = ft.TextButton(
            "🔑 License Activation",
            on_click=self._handle_license,
            style=ft.ButtonStyle(
                color=Theme.TEXT_SECONDARY,
            ),
        )
        
        # Forgot password button
        forgot_btn = ft.TextButton(
            "Forgot Password?",
            on_click=self._handle_forgot_password,
            style=ft.ButtonStyle(
                color=Theme.TEXT_SECONDARY,
            ),
        )
        
        # SuperAdmin hint
        superadmin_hint = Theme.text_caption(
            "💡 Dev SuperAdmin: 1 / 1",
        )
        
        # Main content
        content = ft.Container(
            content=ft.Column(
                [
                    # Logo/Title
                    ft.Container(height=50),
                    ft.Icon("hexagon", size=60, color=Theme.PRIMARY),
                    ft.Container(height=10),
                    Theme.text_heading("MultiTeam Communication"),
                    Theme.text_caption("P2P Team Collaboration Platform"),
                    
                    ft.Container(height=40),
                    
                    # Login card
                    Theme.card(
                        ft.Column(
                            [
                                Theme.text_title("Welcome Back"),
                                ft.Container(height=20),
                                
                                self.email_input,
                                ft.Container(height=15),
                                
                                self.password_input,
                                ft.Container(height=10),
                                
                                ft.Row(
                                    [
                                        self.remember_checkbox,
                                        ft.Container(expand=True),
                                        forgot_btn,
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                
                                ft.Container(height=20),
                                login_btn,
                                ft.Container(height=10),
                                register_btn,
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=0,
                        ),
                        width=400,
                    ),
                    
                    ft.Container(height=20),
                    
                    # Divider
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Divider(color=Theme.BORDER),
                                expand=True,
                            ),
                            Theme.text_caption("  OR  "),
                            ft.Container(
                                content=ft.Divider(color=Theme.BORDER),
                                expand=True,
                            ),
                        ],
                        width=400,
                    ),
                    
                    ft.Container(height=10),
                    license_btn,
                    ft.Container(height=10),
                    superadmin_hint,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
            alignment=ft.alignment.center,
        )
        
        # Bind Enter key
        self.email_input.on_submit = lambda e: self.password_input.focus()
        self.password_input.on_submit = lambda e: self._handle_login(e)
        
        debug("LoginModule", "Login UI created")
        return content
    
    def _handle_login(self, e):
        """Handle login"""
        email = self.email_input.value
        password = self.password_input.value
        
        debug("LoginModule", f"Login attempt: {email}")
        
        # Validate input
        if not email or not password:
            CustomDialog.show_error(
                self.page,
                "Error",
                "Please enter both email and password"
            )
            return
        
        # Authenticate
        user = self.auth_system.authenticate(email, password)
        
        if user:
            info("LoginModule", f"Login successful: {email}")
            
            # Handle remember me
            if self.remember_checkbox.value:
                self.remember_me.save_credentials(email, password)
            
            # Call success callback
            if self.on_login_success:
                self.on_login_success(user)
        else:
            error("LoginModule", f"Login failed: {email}")
            CustomDialog.show_error(
                self.page,
                "Login Failed",
                "Invalid email or password"
            )
    
    def _handle_register(self, e):
        """Handle registration"""
        debug("LoginModule", "Register button clicked")
        if self.on_register:
            self.on_register()
    
    def _handle_license(self, e):
        """Handle license activation"""
        debug("LoginModule", "License activation button clicked")
        if self.on_license:
            self.on_license()
    
    def _handle_forgot_password(self, e):
        """Handle forgot password"""
        debug("LoginModule", "Forgot password clicked")
        CustomDialog.show_info(
            self.page,
            "Forgot Password",
            "Password reset functionality coming soon!\n\n"
            "For now, please contact support:\n"
            "MultiTeamCommunication@gmail.com"
        )
    
    def get_content(self):
        """Get module content"""
        return self.content


# Export
__all__ = ['LoginModule']

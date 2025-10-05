"""
Login Module - Första modulen användaren ser
Hanterar login med Namn, Företag, Email
"""

import customtkinter as ctk
from typing import Callable, Optional
from core.debug_logger import debug, info, warning, error
from core.ui_components import (
    CustomButton, CustomEntry, CustomLabel, 
    CustomFrame, CustomCheckbox, MessageBox
)
from core.auth_system import AuthSystem
from core.twofa_system import TwoFASystem
from core.global_settings import settings
from core.remember_me import RememberMe


class LoginModule(ctk.CTkFrame):
    """Login module med email/password authentication"""
    
    def __init__(
        self,
        master,
        on_login_success: Callable = None,
        on_register_click: Callable = None,
        on_forgot_password: Callable = None,
        on_license_activation: Callable = None,
        on_license_application: Callable = None,
        **kwargs
    ):
        """
        Initialize login module
        
        Args:
            master: Parent widget
            on_login_success: Callback for successful login
            on_register_click: Callback for register button
            on_forgot_password: Callback for forgot password
            on_license_activation: Callback for license activation
            on_license_application: Callback for license application
        """
        debug("LoginModule", "Initializing login module")
        
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.on_login_success = on_login_success
        self.on_register_click = on_register_click
        self.on_forgot_password = on_forgot_password
        self.on_license_activation = on_license_activation
        self.on_license_application = on_license_application
        self.auth_system = AuthSystem()
        self.twofa_system = TwoFASystem()
        self.remember_me = RememberMe()
        
        self._create_ui()
        
        info("LoginModule", "Login module initialized")
    
    def _create_ui(self):
        """Create login UI"""
        debug("LoginModule", "Creating login UI")
        
        # Center container
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        container = CustomFrame(self, transparent=False)
        container.grid(row=0, column=0, sticky="")
        container.configure(width=450, height=550, border_width=2, border_color=("#3a3a3a", "#3a3a3a"))
        
        # Logo/Title area
        title_frame = CustomFrame(container, transparent=True)
        title_frame.pack(pady=(40, 30))
        
        logo_label = CustomLabel(
            title_frame,
            text="🔐",
            size=48
        )
        logo_label.pack()
        
        title_label = CustomLabel(
            title_frame,
            text="MultiTeam Communication",
            size=24,
            bold=True
        )
        title_label.pack(pady=(10, 5))
        
        subtitle_label = CustomLabel(
            title_frame,
            text="P2P Team Collaboration Platform",
            size=12,
            color=("#999999", "#999999")
        )
        subtitle_label.pack()
        
        # Login form
        form_frame = CustomFrame(container, transparent=True)
        form_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Email field
        email_label = CustomLabel(form_frame, text="Email", size=11, bold=True)
        email_label.pack(anchor="w", pady=(10, 3))
        
        self.email_entry = CustomEntry(
            form_frame,
            placeholder="Enter your email",
            width=370
        )
        self.email_entry.pack(pady=(0, 5))
        self.email_entry.bind("<Return>", lambda e: self.password_entry.focus())
        
        # Password field
        password_label = CustomLabel(form_frame, text="Password", size=11, bold=True)
        password_label.pack(anchor="w", pady=(0, 3))
        
        self.password_entry = CustomEntry(
            form_frame,
            placeholder="Enter your password",
            width=370,
            show="●"
        )
        self.password_entry.pack(pady=(0, 5))
        self.password_entry.bind("<Return>", lambda e: self._handle_login())
        
        # Remember me checkbox
        options_frame = CustomFrame(form_frame, transparent=True)
        options_frame.pack(fill="x", pady=(0, 30))
        
        self.remember_checkbox = CustomCheckbox(
            options_frame,
            text="Remember me"
        )
        self.remember_checkbox.pack(side="left")
        
        # Forgot password link
        forgot_btn = CustomButton(
            options_frame,
            text="Forgot Password?",
            command=self._handle_forgot_password,
            width=120,
            height=20,
            style="secondary"
        )
        forgot_btn.pack(side="right")
        
        # Login button
        self.login_btn = CustomButton(
            form_frame,
            text="Login",
            command=self._handle_login,
            width=370,
            height=45,
            style="primary"
        )
        self.login_btn.pack(pady=(10, 8))
        
        # Register button (utan OR divider)
        self.register_btn = CustomButton(
            form_frame,
            text="Create New Account",
            command=self._handle_register_click,
            width=370,
            height=40,
            style="secondary"
        )
        self.register_btn.pack(pady=(0, 10))
        
        # License activation button (subtil)
        license_btn = ctk.CTkButton(
            form_frame,
            text="🔑 License Activation",
            command=self._handle_license_activation,
            width=370,
            height=32,
            font=("Segoe UI", 11),
            fg_color="transparent",
            hover_color=("#2b2b2b", "#2b2b2b"),
            text_color=("#888888", "#888888"),
            border_width=1,
            border_color=("#3a3a3a", "#3a3a3a"),
            corner_radius=5
        )
        license_btn.pack(pady=(0, 10))
        
        # Divider
        divider_frame = CustomFrame(form_frame, transparent=True)
        divider_frame.pack(pady=15, fill="x")
        
        CustomLabel(
            divider_frame,
            text="─────────  OR  ─────────",
            size=10,
            color=("#666666", "#666666")
        ).pack()
        
        # Google OAuth button
        self.google_btn = CustomButton(
            form_frame,
            text="🔐 Login with Google",
            command=self._handle_google_login,
            width=370,
            height=40,
            style="primary"
        )
        self.google_btn.pack(pady=(0, 10))
        
        # SuperAdmin hint
        hint_label = CustomLabel(
            form_frame,
            text="💡 Dev SuperAdmin: 1 / 1",
            size=9,
            color=("#666666", "#666666")
        )
        hint_label.pack(pady=(20, 0))
        
        debug("LoginModule", "Login UI created")
    
    def _handle_login(self):
        """Handle login button click"""
        debug("LoginModule", "Login button clicked")
        
        email = self.email_entry.get_value().strip()
        password = self.password_entry.get_value()
        
        debug("LoginModule", f"Login attempt - Email: {email}, Password length: {len(password)}")
        
        # Validate input
        if not email:
            warning("LoginModule", "Login failed: Email is empty")
            MessageBox.show_error(
                self.master,
                "Login Error",
                "Please enter your email address."
            )
            return
        
        if not password:
            warning("LoginModule", "Login failed: Password is empty")
            MessageBox.show_error(
                self.master,
                "Login Error",
                "Please enter your password."
            )
            return
        
        # Authenticate
        debug("LoginModule", "Authenticating user...")
        user = self.auth_system.authenticate(email, password)
        
        if user:
            info("LoginModule", f"Login successful for: {email}")
            
            # Check if verified (SuperAdmin is always verified)
            if not user["verified"] and user["role"] != "superadmin":
                warning("LoginModule", f"User not verified: {email}")
                
                # Check if email verification is enabled in settings
                if settings.is_email_verification_enabled():
                    MessageBox.show_error(
                        self.master,
                        "Email Not Verified",
                        "Please verify your email address before logging in.\n\nCheck your inbox for the verification code."
                    )
                    return
                else:
                    debug("LoginModule", "Email verification disabled in settings, allowing login")
            
            # Check if 2FA is enabled for this user
            if settings.is_2fa_enabled():
                is_2fa_enabled, secret = self.twofa_system.get_user_2fa_status(user["id"])
                
                if is_2fa_enabled and secret:
                    info("LoginModule", f"2FA required for user: {email}")
                    # Show 2FA verification
                    self._show_2fa_verification(user, secret)
                    return
                elif settings.is_2fa_required() and user["role"] != "superadmin":
                    warning("LoginModule", f"2FA required but not setup for user: {email}")
                    MessageBox.show_error(
                        self.master,
                        "2FA Required",
                        "Two-Factor Authentication is required for your account.\n\nPlease contact an administrator."
                    )
                    return
            
            # No 2FA required, proceed with login
            self._complete_login(user)
        else:
            error("LoginModule", f"Login failed for: {email}")
            MessageBox.show_error(
                self.master,
                "Login Failed",
                "Invalid email or password.\n\nPlease check your credentials and try again."
            )
    
    def _handle_register_click(self):
        """Handle register button click"""
        debug("LoginModule", "Register button clicked")
        info("LoginModule", "Navigating to registration")
        self.on_register_click()
    
    def clear_fields(self):
        """Clear all input fields"""
        debug("LoginModule", "Clearing input fields")
        self.email_entry.set_value("")
        self.password_entry.set_value("")
        self.remember_checkbox.deselect()
    
    def set_email(self, email: str):
        """Set email field (används efter registrering)"""
        debug("LoginModule", f"Setting email field: {email}")
        self.email_entry.set_value(email)
        self.password_entry.focus()
    
    def _show_2fa_verification(self, user: dict, secret: str):
        """Show 2FA verification screen"""
        debug("LoginModule", f"Showing 2FA verification for user: {user['email']}")
        
        # Clear current content
        for widget in self.winfo_children():
            widget.destroy()
        
        # Import and show 2FA verify module
        from modules.twofa_verify_module import TwoFAVerifyModule
        
        verify_module = TwoFAVerifyModule(
            self,
            user_id=user["id"],
            user_email=user["email"],
            secret=secret,
            on_success=lambda: self._complete_login(user),
            on_cancel=self._recreate_login_ui
        )
        verify_module.pack(fill="both", expand=True)
        
        info("LoginModule", "2FA verification screen shown")
    
    def _complete_login(self, user: dict):
        """Complete login process"""
        debug("LoginModule", f"Completing login for: {user['email']}")
        
        # Store user data
        user_data = user
        
        # Handle remember me
        if self.remember_checkbox.get():
            debug("LoginModule", "Remember me enabled - creating session")
            self.remember_me.create_session(
                user_id=user['id'],
                email=user['email'],
                name=user['name']
            )
        else:
            debug("LoginModule", "Remember me disabled - clearing session")
            self.remember_me.clear_session()
        
        # Show success message
        dialog = MessageBox.show_success(
            self.master,
            "Login Successful",
            f"Welcome back, {user['name']}!"
        )
        
        # Schedule callback after dialog shows
        self.after(100, lambda: self.on_login_success(user_data))
    
    def _recreate_login_ui(self):
        """Recreate login UI (efter 2FA cancel)"""
        debug("LoginModule", "Recreating login UI")
        
        # Clear current content
        for widget in self.winfo_children():
            widget.destroy()
        
        # Recreate UI
        self._create_ui()
        
        info("LoginModule", "Login UI recreated")
    
    def _handle_google_login(self):
        """Handle Google OAuth login"""
        debug("LoginModule", "Google login clicked")
        
        try:
            from core.google_oauth import GoogleOAuth
            from core.global_settings import settings
            
            if not settings.get("google_oauth_enabled", False):
                MessageBox.show_info(
                    self.master,
                    "Google Login Disabled",
                    "Google OAuth login is currently disabled.\n\nPlease enable it in Settings or contact your administrator."
                )
                return
            
            oauth = GoogleOAuth()
            
            # Check if credentials are configured
            if not oauth.is_configured():
                MessageBox.show_error(
                    self.master,
                    "Google OAuth Not Configured",
                    "Google OAuth credentials are not configured.\n\nPlease configure OAuth credentials in the application settings."
                )
                return
            
            # Start OAuth flow
            info("LoginModule", "Starting Google OAuth flow")
            MessageBox.show_info(
                self.master,
                "Google Login",
                "Google OAuth login will open in your browser.\n\nPlease complete the authentication process."
            )
            
            # TODO: Implement full OAuth flow
            # user_info = oauth.authenticate()
            # if user_info:
            #     self.on_login_success(user_info)
            
        except Exception as e:
            error("LoginModule", f"Google login error: {e}")
            MessageBox.show_error(
                self.master,
                "Google Login Error",
                f"Failed to initiate Google login.\n\nError: {str(e)}"
            )
    
    def _handle_forgot_password(self):
        """Handle forgot password click"""
        debug("LoginModule", "Forgot password clicked")
        
        if self.on_forgot_password:
            self.on_forgot_password()
        else:
            warning("LoginModule", "No forgot password callback set")
    
    def _handle_license_activation(self):
        """Handle license activation button click"""
        info("LoginModule", "License activation button clicked")
        
        # Anropa callback för att visa license activation i huvudfönstret
        if hasattr(self, 'on_license_activation') and self.on_license_activation:
            self.on_license_activation()
        else:
            # Fallback: Visa som dialog
            try:
                from core.license_activation import LicenseActivation
                from core.custom_window import CustomDialog
                from core.ui_components import CustomFrame, CustomLabel, CustomButton
                
                activation_system = LicenseActivation()
                machine_uid = activation_system.get_machine_uid()
                
                # Skapa dialog för license management
                dialog = CustomDialog(self.master, title="🔑 License Management", width=550, height=500)
                
                # Content
                content = CustomFrame(dialog.content_frame, transparent=True)
                content.pack(fill="both", expand=True, padx=30, pady=30)
                
                # Title
                CustomLabel(
                    content,
                    text="🔑 License Management",
                    size=20,
                    bold=True
                ).pack(pady=(0, 20))
                
                # Machine ID Card
                machine_card = CustomFrame(content, transparent=False)
                machine_card.pack(fill="x", pady=(0, 20))
                machine_card.configure(
                    border_width=1,
                    border_color=("#3a3a3a", "#3a3a3a"),
                    corner_radius=8
                )
                
                machine_content = CustomFrame(machine_card, transparent=True)
                machine_content.pack(fill="x", padx=15, pady=15)
                
                CustomLabel(
                    machine_content,
                    text="Machine ID",
                    size=11,
                    color=("#888888", "#888888")
                ).pack(anchor="w")
                
                CustomLabel(
                    machine_content,
                    text=machine_uid,
                    size=12,
                    bold=True
                ).pack(anchor="w", pady=(5, 0))
                
                # Enter License Key button
                def show_enter_key():
                    dialog._close_dialog()
                    self._show_enter_key_dialog(activation_system)
                
                CustomButton(
                    content,
                    text="🔑 Enter License Key",
                    command=show_enter_key,
                    width=350,
                    height=50,
                    style="primary"
                ).pack(pady=10)
                
                # Apply for License button
                def show_application():
                    dialog._close_dialog()
                    self._show_application_form(activation_system)
                
                CustomButton(
                    content,
                    text="📝 Apply for License",
                    command=show_application,
                    width=350,
                    height=50,
                    style="secondary"
                ).pack(pady=10)
            except Exception as e:
                error("LoginModule", f"License activation error: {e}")
                from core.ui_components import MessageBox
                MessageBox.show_error(
                    self.master,
                    "Error",
                    "Failed to open license activation screen"
                )
    
    def _show_enter_key_dialog(self, activation_system):
        """Show enter license key dialog"""
        from core.ui_components import MessageBox, CustomFrame, CustomLabel, CustomButton
        
        # Skapa input dialog
        dialog = ctk.CTkToplevel(self.master)
        dialog.title("Enter License Information")
        dialog.geometry("500x400")
        dialog.configure(fg_color=("#2b2b2b", "#2b2b2b"))
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 250
        y = (dialog.winfo_screenheight() // 2) - 200
        dialog.geometry(f"500x400+{x}+{y}")
        
        # Make modal
        dialog.transient(self.master)
        dialog.grab_set()
        
        # Content
        content = CustomFrame(dialog, transparent=True)
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Title
        CustomLabel(
            content,
            text="Enter License Information",
            size=18,
            bold=True
        ).pack(pady=(0, 20))
        
        # Company Name entry
        CustomLabel(
            content,
            text="Company Name:",
            size=12
        ).pack(anchor="w", pady=(0, 5))
        
        company_entry = ctk.CTkEntry(
            content,
            width=400,
            height=40,
            placeholder_text="Your Company Name",
            fg_color=("#2b2b2b", "#2b2b2b"),
            text_color=("#ffffff", "#ffffff"),
            placeholder_text_color=("#666666", "#666666"),
            border_width=1,
            border_color=("#3a3a3a", "#3a3a3a"),
            corner_radius=5,
            font=("Segoe UI", 12)
        )
        company_entry.pack(pady=(0, 15))
        
        # Key entry
        CustomLabel(
            content,
            text="License Key:",
            size=12
        ).pack(anchor="w", pady=(0, 5))
        
        key_entry = ctk.CTkEntry(
            content,
            width=400,
            height=40,
            placeholder_text="XXXX-XXXX-XXXX-XXXX",
            fg_color=("#2b2b2b", "#2b2b2b"),
            text_color=("#ffffff", "#ffffff"),
            placeholder_text_color=("#666666", "#666666"),
            border_width=1,
            border_color=("#3a3a3a", "#3a3a3a"),
            corner_radius=5,
            font=("Consolas", 12)
        )
        key_entry.pack(pady=(0, 10))
        
        # Force focus on company entry first
        dialog.after(200, lambda: company_entry.focus_set())
        dialog.after(250, lambda: company_entry.focus_force())
        
        # Buttons
        btn_frame = CustomFrame(content, transparent=True)
        btn_frame.pack(pady=20)
        
        def activate_key(event=None):
            company = company_entry.get().strip()
            key = key_entry.get().strip().upper()
            
            # Validera input
            if not company:
                MessageBox.show_error(dialog, "Error", "Please enter your company name")
                company_entry.focus()
                return
            
            if not key:
                MessageBox.show_error(dialog, "Error", "Please enter a license key")
                key_entry.focus()
                return
            
            # Get machine UID
            machine_uid = activation_system.get_machine_uid()
            
            # Activate license
            import sqlite3
            import hashlib
            from datetime import datetime
            
            try:
                conn = sqlite3.connect('data/license_applications.db')
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Hash license key
                key_hash = hashlib.sha256(key.encode()).hexdigest()
                
                # Check if license exists with matching company
                cursor.execute("""
                    SELECT * FROM license_applications
                    WHERE license_key = ? 
                      AND LOWER(company) = LOWER(?)
                      AND status = 'approved' 
                      AND payment_status = 'paid'
                """, (key, company))
                
                app_data = cursor.fetchone()
                
                if not app_data:
                    conn.close()
                    MessageBox.show_error(dialog, "Invalid License", 
                                        "License key or company name is incorrect.\n\n"
                                        "Please check:\n"
                                        "- License key format\n"
                                        "- Company name spelling\n"
                                        "- License status (must be approved and paid)")
                    return
                
                # Check if already activated on this machine
                cursor.execute("""
                    SELECT * FROM active_licenses
                    WHERE license_key_hash = ? AND machine_uid = ?
                """, (key_hash, machine_uid))
                
                existing = cursor.fetchone()
                
                if not existing:
                    # Activate for first time
                    cursor.execute("""
                        INSERT INTO active_licenses (
                            license_key, license_key_hash, machine_uid,
                            email, company, tier, activated_at,
                            last_validated, application_id, is_active
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                    """, (
                        key, key_hash, machine_uid,
                        app_data['email'], app_data['company'], app_data['requested_tier'],
                        datetime.now().isoformat(), datetime.now().isoformat(),
                        app_data['id']
                    ))
                    conn.commit()
                    
                    info("LicenseActivation", f"License activated for {company}: {key}")
                
                conn.close()
                
                dialog.destroy()
                MessageBox.show_success(
                    self.master,
                    "License Activated!",
                    f"Company: {app_data['company']}\n"
                    f"Tier: {app_data['requested_tier']}\n\n"
                    f"License successfully activated!"
                )
                
            except Exception as e:
                error("LicenseActivation", f"License activation error: {e}")
                MessageBox.show_error(dialog, "Error", f"Activation failed: {e}")
        
        CustomButton(
            btn_frame,
            text="Activate",
            command=activate_key,
            width=120,
            height=35,
            style="primary"
        ).pack(side="left", padx=5)
        
        CustomButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            width=100,
            height=35,
            style="secondary"
        ).pack(side="left", padx=5)
        
        # Bind Enter key
        key_entry.bind("<Return>", activate_key)
    
    def _show_application_form(self, activation_system):
        """Show license application form"""
        # Anropa callback för att visa application i huvudfönstret
        if hasattr(self, 'on_license_application') and self.on_license_application:
            self.on_license_application()
        else:
            # Fallback: Visa meddelande
            from core.ui_components import MessageBox
            MessageBox.show_info(
                self.master,
                "Apply for License",
                "To apply for a license, please contact:\n\n"
                "Email: MultiTeamCommunication@gmail.com\n\n"
                "Include your Machine ID and desired tier."
            )


if __name__ == "__main__":
    # Test login module
    info("TEST", "Testing LoginModule...")
    
    from core.custom_window import CustomWindow
    
    def on_login(user):
        print(f"Login success: {user}")
    
    def on_register():
        print("Register clicked")
    
    app = CustomWindow(title="Login Test", width=500, height=650)
    
    login_module = LoginModule(
        app.content_frame,
        on_login_success=on_login,
        on_register_click=on_register
    )
    login_module.pack(fill="both", expand=True)
    
    info("TEST", "Starting mainloop...")
    app.mainloop()

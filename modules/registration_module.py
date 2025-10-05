"""
Registration Module - Registrering med email verifiering
Namn, Företag, Email, Password
"""

import customtkinter as ctk
import re
from typing import Callable
from core.debug_logger import debug, info, warning, error
from core.ui_components import (
    CustomButton, CustomEntry, CustomLabel,
    CustomFrame, MessageBox, LoadingSpinner
)
from core.auth_system import AuthSystem
from core.email_service import EmailService


class RegistrationModule(ctk.CTkFrame):
    """Registration module med email verification"""
    
    def __init__(
        self,
        master,
        on_registration_complete: Callable,
        on_back_to_login: Callable,
        **kwargs
    ):
        """Initialize registration module"""
        debug("RegistrationModule", "Initializing registration module")
        
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.on_registration_complete = on_registration_complete
        self.on_back_to_login = on_back_to_login
        self.auth_system = AuthSystem()
        self.email_service = EmailService()
        
        self.verification_code = None
        self.user_email = None
        
        self._create_ui()
        
        info("RegistrationModule", "Registration module initialized")
    
    def _create_ui(self):
        """Create registration UI"""
        debug("RegistrationModule", "Creating registration UI")
        
        # Center container
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.container = CustomFrame(self, transparent=False)
        self.container.grid(row=0, column=0, sticky="")
        self.container.configure(width=500, height=650, border_width=2, border_color=("#3a3a3a", "#3a3a3a"))
        
        # Create registration form (initial view)
        self._create_registration_form()
        
        debug("RegistrationModule", "Registration UI created")
    
    def _create_registration_form(self):
        """Create registration form"""
        debug("RegistrationModule", "Creating registration form")
        
        # Clear container
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Title
        title_frame = CustomFrame(self.container, transparent=True)
        title_frame.pack(pady=(30, 20))
        
        title_label = CustomLabel(
            title_frame,
            text="Create Account",
            size=24,
            bold=True
        )
        title_label.pack()
        
        subtitle_label = CustomLabel(
            title_frame,
            text="Join the MultiTeam platform",
            size=12,
            color=("#999999", "#999999")
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Form
        form_frame = CustomFrame(self.container, transparent=True)
        form_frame.pack(pady=10, padx=40, fill="both", expand=True)
        
        # Name field
        name_label = CustomLabel(form_frame, text="Full Name", size=11, bold=True)
        name_label.pack(anchor="w", pady=(5, 3))
        
        self.name_entry = CustomEntry(
            form_frame,
            placeholder="Enter your full name",
            width=420
        )
        self.name_entry.pack(pady=(0, 8))
        self.name_entry.bind("<Return>", lambda e: self.company_entry.focus())
        
        # Company field
        company_label = CustomLabel(form_frame, text="Company", size=11, bold=True)
        company_label.pack(anchor="w", pady=(0, 3))
        
        self.company_entry = CustomEntry(
            form_frame,
            placeholder="Enter your company name",
            width=420
        )
        self.company_entry.pack(pady=(0, 8))
        self.company_entry.bind("<Return>", lambda e: self.email_entry.focus())
        
        # Email field
        email_label = CustomLabel(form_frame, text="Email", size=11, bold=True)
        email_label.pack(anchor="w", pady=(0, 3))
        
        self.email_entry = CustomEntry(
            form_frame,
            placeholder="Enter your email address",
            width=420
        )
        self.email_entry.pack(pady=(0, 8))
        self.email_entry.bind("<Return>", lambda e: self.password_entry.focus())
        
        # Password field
        password_label = CustomLabel(form_frame, text="Password", size=11, bold=True)
        password_label.pack(anchor="w", pady=(0, 3))
        
        self.password_entry = CustomEntry(
            form_frame,
            placeholder="Create a strong password",
            width=420,
            show="●"
        )
        self.password_entry.pack(pady=(0, 8))
        self.password_entry.bind("<Return>", lambda e: self.confirm_password_entry.focus())
        
        # Password requirements removed - user can choose freely
        # req_label = CustomLabel(
        #     form_frame,
        #     text="• At least 8 characters • Contains letters and numbers",
        #     size=9,
        #     color=("#666666", "#666666")
        # )
        # req_label.pack(anchor="w", pady=(0, 15))
        
        # Confirm password field
        confirm_label = CustomLabel(form_frame, text="Confirm Password", size=11, bold=True)
        confirm_label.pack(anchor="w", pady=(0, 3))
        
        self.confirm_password_entry = CustomEntry(
            form_frame,
            placeholder="Re-enter your password",
            width=420,
            show="●"
        )
        self.confirm_password_entry.pack(pady=(0, 15))
        self.confirm_password_entry.bind("<Return>", lambda e: self._handle_register())
        
        # Register button
        self.register_btn = CustomButton(
            form_frame,
            text="Create Account",
            command=self._handle_register,
            width=420,
            height=45,
            style="success"
        )
        self.register_btn.pack(pady=(10, 15))
        
        # Back to login
        back_btn = CustomButton(
            form_frame,
            text="← Back to Login",
            command=self._handle_back,
            width=420,
            height=40,
            style="transparent"
        )
        back_btn.pack(pady=(5, 10))
        
        debug("RegistrationModule", "Registration form created")
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = re.match(pattern, email) is not None
        debug("RegistrationModule", f"Email validation for {email}: {is_valid}")
        return is_valid
    
    def _validate_password(self, password: str) -> tuple[bool, str]:
        """Validate password - no requirements, user chooses freely"""
        debug("RegistrationModule", f"Password validation (length: {len(password)}) - no restrictions")
        
        # No password requirements - user can choose any password
        # Just check it's not empty (handled elsewhere)
        
        debug("RegistrationModule", "Password validation passed (no restrictions)")
        return True, ""
    
    def _handle_register(self):
        """Handle registration"""
        debug("RegistrationModule", "Register button clicked")
        
        # Get values
        name = self.name_entry.get_value().strip()
        company = self.company_entry.get_value().strip()
        email = self.email_entry.get_value().strip().lower()
        password = self.password_entry.get_value()
        confirm_password = self.confirm_password_entry.get_value()
        
        debug("RegistrationModule", f"Registration attempt - Name: {name}, Company: {company}, Email: {email}")
        
        # Validate fields
        if not name:
            warning("RegistrationModule", "Registration failed: Name is empty")
            MessageBox.show_error(self.master, "Validation Error", "Please enter your full name.")
            self.after(100, lambda: self.name_entry.focus_force())
            return
        
        if not company:
            warning("RegistrationModule", "Registration failed: Company is empty")
            MessageBox.show_error(self.master, "Validation Error", "Please enter your company name.")
            self.after(100, lambda: self.company_entry.focus_force())
            return
        
        if not email:
            warning("RegistrationModule", "Registration failed: Email is empty")
            MessageBox.show_error(self.master, "Validation Error", "Please enter your email address.")
            return
        
        if not self._validate_email(email):
            warning("RegistrationModule", f"Registration failed: Invalid email format: {email}")
            MessageBox.show_error(self.master, "Validation Error", "Please enter a valid email address.")
            return
        
        # Check SuperAdmin email
        if self.auth_system.is_superadmin(email):
            error("RegistrationModule", "Cannot register with SuperAdmin email")
            MessageBox.show_error(
                self.master,
                "Registration Error",
                "This email is reserved for system administration."
            )
            return
        
        if not password:
            warning("RegistrationModule", "Registration failed: Password is empty")
            MessageBox.show_error(self.master, "Validation Error", "Please enter a password.")
            self.after(100, lambda: self.password_entry.focus_force())
            return
        
        # No password validation - user can choose any password freely
        debug("RegistrationModule", "Password accepted - no restrictions applied")
        
        if password != confirm_password:
            warning("RegistrationModule", "Registration failed: Passwords don't match")
            MessageBox.show_error(self.master, "Validation Error", "Passwords do not match.")
            self.after(100, lambda: self.confirm_password_entry.focus_force())
            return
        
        # Check if user exists
        existing_user = self.auth_system.get_user_by_email(email)
        if existing_user:
            warning("RegistrationModule", f"Registration failed: User already exists: {email}")
            MessageBox.show_error(
                self.master,
                "Registration Error",
                "An account with this email already exists.\n\nPlease login or use a different email."
            )
            # Re-enable fields after error
            self.after(100, lambda: self.email_entry.focus_force())
            return
        
        # Generate verification code
        debug("RegistrationModule", "Generating verification code")
        self.verification_code = self.email_service.generate_verification_code()
        self.user_email = email
        
        # Send verification email
        info("RegistrationModule", f"Sending verification email to: {email}")
        
        # Disable button during send
        self.register_btn.configure(state="disabled", text="Sending email...")
        self.update()
        
        success = self.email_service.send_verification_email(email, name, self.verification_code)
        
        self.register_btn.configure(state="normal", text="Create Account")
        
        if not success:
            error("RegistrationModule", "Failed to send verification email")
            MessageBox.show_error(
                self.master,
                "Email Error",
                "Failed to send verification email.\n\nPlease check your internet connection and try again."
            )
            return
        
        # Register user (unverified)
        debug("RegistrationModule", "Registering user in database")
        if self.auth_system.register_user(email, password, name, company, self.verification_code):
            info("RegistrationModule", f"User registered successfully: {email}")
            
            # Store registration data for verification
            self.registration_data = {
                "name": name,
                "company": company,
                "email": email
            }
            
            # Show verification form
            self._create_verification_form()
        else:
            error("RegistrationModule", "Failed to register user")
            MessageBox.show_error(
                self.master,
                "Registration Error",
                "Failed to create account.\n\nPlease try again later."
            )
    
    def _create_verification_form(self):
        """Create email verification form"""
        debug("RegistrationModule", "Creating verification form")
        
        # Clear container
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Title
        title_frame = CustomFrame(self.container, transparent=True)
        title_frame.pack(pady=(40, 20))
        
        icon_label = CustomLabel(title_frame, text="📧", size=48)
        icon_label.pack()
        
        title_label = CustomLabel(
            title_frame,
            text="Verify Your Email",
            size=24,
            bold=True
        )
        title_label.pack(pady=(10, 5))
        
        subtitle_label = CustomLabel(
            title_frame,
            text=f"We sent a verification code to\n{self.user_email}",
            size=12,
            color=("#999999", "#999999")
        )
        subtitle_label.pack()
        
        # Verification form
        form_frame = CustomFrame(self.container, transparent=True)
        form_frame.pack(pady=30, padx=40, fill="both", expand=True)
        
        # Code entry
        code_label = CustomLabel(
            form_frame,
            text="Enter 6-digit verification code:",
            size=12,
            bold=True
        )
        code_label.pack(pady=(20, 10))
        
        self.code_entry = CustomEntry(
            form_frame,
            placeholder="000000",
            width=300,
            height=50
        )
        self.code_entry.configure(font=("Courier New", 20, "bold"), justify="center")
        self.code_entry.pack(pady=(0, 20))
        self.code_entry.bind("<Return>", lambda e: self._handle_verify())
        self.code_entry.focus()
        
        # Verify button
        verify_btn = CustomButton(
            form_frame,
            text="Verify Email",
            command=self._handle_verify,
            width=300,
            height=45,
            style="success"
        )
        verify_btn.pack(pady=(10, 15))
        
        # Resend button
        resend_btn = CustomButton(
            form_frame,
            text="Resend Code",
            command=self._handle_resend,
            width=300,
            height=40,
            style="transparent"
        )
        resend_btn.pack(pady=(5, 15))
        
        # Back button
        back_btn = CustomButton(
            form_frame,
            text="← Back to Registration",
            command=self._create_registration_form,
            width=300,
            height=35,
            style="transparent"
        )
        back_btn.pack(pady=(5, 10))
        
        info("RegistrationModule", "Verification form created")
    
    def _handle_verify(self):
        """Handle email verification"""
        debug("RegistrationModule", "Verify button clicked")
        
        code = self.code_entry.get_value().strip()
        
        debug("RegistrationModule", f"Verification attempt - Code: {code}")
        
        if not code:
            warning("RegistrationModule", "Verification failed: Code is empty")
            MessageBox.show_error(self.master, "Verification Error", "Please enter the verification code.")
            return
        
        if len(code) != 6 or not code.isdigit():
            warning("RegistrationModule", "Verification failed: Invalid code format")
            MessageBox.show_error(self.master, "Verification Error", "Please enter a valid 6-digit code.")
            return
        
        # Verify code
        debug("RegistrationModule", "Verifying code with auth system")
        if self.auth_system.verify_email(self.user_email, code):
            info("RegistrationModule", f"Email verified successfully: {self.user_email}")
            
            # Send welcome email
            self.email_service.send_welcome_email(
                self.user_email,
                self.registration_data["name"]
            )
            
            # Complete registration first (before showing dialog)
            email_to_pass = self.user_email
            name_to_show = self.registration_data['name']
            
            # Show success dialog
            dialog = MessageBox.show_success(
                self.master,
                "Email Verified!",
                f"Your account has been created successfully.\n\nWelcome to MultiTeam, {name_to_show}!"
            )
            
            # Schedule the navigation after a short delay to let dialog show
            self.after(100, lambda: self.on_registration_complete(email_to_pass))
        else:
            error("RegistrationModule", "Email verification failed: Invalid code")
            MessageBox.show_error(
                self.master,
                "Verification Failed",
                "Invalid verification code.\n\nPlease check the code and try again."
            )
    
    def _handle_resend(self):
        """Handle resend verification code"""
        debug("RegistrationModule", "Resend code button clicked")
        
        # Generate new code
        self.verification_code = self.email_service.generate_verification_code()
        
        # Update in database
        # Note: In production, you'd update the code in database here
        
        # Send email
        info("RegistrationModule", f"Resending verification email to: {self.user_email}")
        success = self.email_service.send_verification_email(
            self.user_email,
            self.registration_data["name"],
            self.verification_code
        )
        
        if success:
            MessageBox.show_info(
                self.master,
                "Code Resent",
                "A new verification code has been sent to your email."
            )
        else:
            MessageBox.show_error(
                self.master,
                "Email Error",
                "Failed to resend verification code.\n\nPlease try again."
            )
    
    def _handle_back(self):
        """Handle back to login"""
        debug("RegistrationModule", "Back to login clicked")
        self.on_back_to_login()


if __name__ == "__main__":
    # Test registration module
    info("TEST", "Testing RegistrationModule...")
    
    from core.custom_window import CustomWindow
    
    def on_complete(email):
        print(f"Registration complete: {email}")
    
    def on_back():
        print("Back to login")
    
    app = CustomWindow(title="Registration Test", width=550, height=700)
    
    reg_module = RegistrationModule(
        app.content_frame,
        on_registration_complete=on_complete,
        on_back_to_login=on_back
    )
    reg_module.pack(fill="both", expand=True)
    
    info("TEST", "Starting mainloop...")
    app.mainloop()

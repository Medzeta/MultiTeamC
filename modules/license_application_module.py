"""
License Application Module
Form for submitting license applications
"""

import customtkinter as ctk
from core.ui_components import CustomFrame, CustomLabel, CustomButton
from core.debug_logger import debug, info

class LicenseApplicationModule(CustomFrame):
    """License application form"""
    
    def __init__(self, parent, activation_system, on_back=None, on_success=None):
        super().__init__(parent, transparent=False)
        self.activation_system = activation_system
        self.on_back = on_back
        self.on_success = on_success
        
        debug("LicenseApplication", "Initializing license application module")
        
        self._create_ui()
        
        info("LicenseApplication", "License application module initialized")
    
    def _create_ui(self):
        """Create UI"""
        # Main container with MORE padding (centrerar kortet) - smalare
        main_container = CustomFrame(self, transparent=True)
        main_container.pack(expand=True, fill="both", padx=350, pady=100)
        
        # Card frame (hälften så stort)
        card_frame = CustomFrame(main_container, transparent=False)
        card_frame.pack(expand=True, fill="both")
        card_frame.configure(
            border_width=1,
            border_color=("#3a3a3a", "#3a3a3a"),
            corner_radius=10
        )
        
        # Scrollable content inside card
        scroll = ctk.CTkScrollableFrame(
            card_frame,
            fg_color="transparent",
            scrollbar_button_color=("#2a2a2a", "#2a2a2a"),
            scrollbar_button_hover_color=("#3a3a3a", "#3a3a3a")
        )
        scroll.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Title
        CustomLabel(
            scroll,
            text="📝 License Application",
            size=20,
            bold=True
        ).pack(pady=(0, 5))
        
        CustomLabel(
            scroll,
            text="Fill in the form below to apply for a license",
            size=11,
            color=("#888888", "#888888")
        ).pack(pady=(0, 20))
        
        # Form content (direkt i scroll)
        form_content = CustomFrame(scroll, transparent=True)
        form_content.pack(fill="x", pady=10)
        
        # Machine UID (read-only)
        self._create_form_field(
            form_content,
            "Machine ID",
            self.activation_system.get_machine_uid(),
            readonly=True
        )
        
        # Name
        self.name_entry = self._create_form_field(
            form_content,
            "Full Name *",
            "Enter your full name"
        )
        
        # Company
        self.company_entry = self._create_form_field(
            form_content,
            "Company Name *",
            "Enter your company name"
        )
        
        # Email
        self.email_entry = self._create_form_field(
            form_content,
            "Email Address *",
            "Enter your email address"
        )
        
        # License tier selection
        tier_frame = CustomFrame(form_content, transparent=True)
        tier_frame.pack(fill="x", pady=15)
        
        CustomLabel(
            tier_frame,
            text="Requested License Tier *",
            size=12,
            bold=True
        ).pack(anchor="w", pady=(0, 5))
        
        self.tier_var = ctk.StringVar(value="standard")
        
        tier_options = [
            ("Basic (Free)", "basic"),
            ("Standard ($9.99/month)", "standard"),
            ("Professional ($29.99/month)", "professional"),
            ("Enterprise ($99.99/month)", "enterprise"),
            ("Ultimate ($199.99/month)", "ultimate")
        ]
        
        for label, value in tier_options:
            radio = ctk.CTkRadioButton(
                tier_frame,
                text=label,
                variable=self.tier_var,
                value=value,
                font=("Segoe UI", 11)
            )
            radio.pack(anchor="w", pady=3)
        
        # Info text
        info_frame = CustomFrame(form_content, transparent=False)
        info_frame.pack(fill="x", pady=20)
        info_frame.configure(
            border_width=1,
            border_color=("#3a3a3a", "#3a3a3a"),
            corner_radius=6
        )
        
        CustomLabel(
            info_frame,
            text="ℹ️ Your application will be reviewed by our team.\nYou will receive an email with your license key once approved.",
            size=10,
            color=("#888888", "#888888")
        ).pack(padx=15, pady=15)
        
        # Buttons
        button_frame = CustomFrame(form_content, transparent=True)
        button_frame.pack(pady=20)
        
        submit_btn = CustomButton(
            button_frame,
            text="Submit Application",
            command=self._submit_application,
            width=200,
            height=45,
            style="primary"
        )
        submit_btn.pack(pady=5)
        
        # Back button
        if self.on_back:
            back_btn = CustomButton(
                button_frame,
                text="← Back",
                command=self.on_back,
                width=200,
                height=40,
                style="secondary"
            )
            back_btn.pack(pady=5)
    
    def _create_form_field(self, parent, label, placeholder, readonly=False):
        """Create a form field"""
        field_frame = CustomFrame(parent, transparent=True)
        field_frame.pack(fill="x", pady=10)
        
        CustomLabel(
            field_frame,
            text=label,
            size=12,
            bold=True
        ).pack(anchor="w", pady=(0, 5))
        
        entry = ctk.CTkEntry(
            field_frame,
            width=500,
            height=40,
            placeholder_text=placeholder if not readonly else "",
            state="disabled" if readonly else "normal",
            fg_color=("#2b2b2b", "#2b2b2b"),
            text_color=("#ffffff", "#ffffff"),
            placeholder_text_color=("#666666", "#666666"),
            border_width=1,
            border_color=("#3a3a3a", "#3a3a3a"),
            corner_radius=5,
            font=("Segoe UI", 11)
        )
        entry.pack(anchor="w")
        
        if readonly:
            entry.insert(0, placeholder)
        
        return entry
    
    def _submit_application(self):
        """Submit license application"""
        from core.ui_components import MessageBox
        
        # Validate form
        name = self.name_entry.get().strip()
        company = self.company_entry.get().strip()
        email = self.email_entry.get().strip()
        tier = self.tier_var.get()
        
        if not name:
            MessageBox.show_error(
                self.winfo_toplevel(),
                "Validation Error",
                "Please enter your full name"
            )
            return
        
        if not company:
            MessageBox.show_error(
                self.winfo_toplevel(),
                "Validation Error",
                "Please enter your company name"
            )
            return
        
        if not email or '@' not in email:
            MessageBox.show_error(
                self.winfo_toplevel(),
                "Validation Error",
                "Please enter a valid email address"
            )
            return
        
        # Submit application
        success, message = self.activation_system.submit_license_application(
            name=name,
            company=company,
            email=email,
            requested_tier=tier
        )
        
        if success:
            MessageBox.show_success(
                self.winfo_toplevel(),
                "Application Submitted!",
                f"{message}\n\nYou will receive an email once your application is reviewed."
            )
            
            # Go back or call success
            if self.on_back:
                self.on_back()
            elif self.on_success:
                self.on_success()
        else:
            MessageBox.show_error(
                self.winfo_toplevel(),
                "Submission Failed",
                message
            )


# Debug logging
debug("LicenseApplication", "License application module loaded")

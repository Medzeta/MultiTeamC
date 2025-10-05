"""
Admin License Applications Module
SuperAdmin interface for managing license applications
"""

import customtkinter as ctk
from core.ui_components import CustomFrame, CustomLabel, CustomButton
from core.debug_logger import debug, info
from core.license_activation import LicenseActivation
from core.license_system import LicenseSystem

class AdminLicenseApplications(ctk.CTkFrame):
    """
    Admin interface for managing license applications
    """
    
    # Global card size settings
    CARD_WIDTH = 350  # Ökad för full Machine ID synlighet
    CARD_HEIGHT = 293  # 220 + (220 * 1/3) = 293px
    
    def __init__(self, master, activation_system, on_back=None, **kwargs):
        super().__init__(master, fg_color=("#2b2b2b", "#2b2b2b"), **kwargs)
        self.on_back = on_back
        self.activation_system = activation_system
        self.current_filter = "all"
        
        debug("AdminLicenseApps", "Initializing admin license applications module")
        
        self._create_ui()
        
        info("AdminLicenseApps", "Admin license applications module initialized")
    
    def _create_ui(self):
        """Create UI"""
        # Header
        header = CustomFrame(self, transparent=True)
        header.pack(fill="x", padx=30, pady=20)
        
        # Back button
        if self.on_back:
            back_btn = CustomButton(
                header,
                text="← Back",
                command=self.on_back,
                width=100,
                height=35,
                style="secondary"
            )
            back_btn.pack(side="left")
        
        # Title
        title_frame = CustomFrame(header, transparent=True)
        title_frame.pack(side="left", padx=20)
        
        CustomLabel(
            title_frame,
            text="📋 License Applications",
            size=24,
            bold=True
        ).pack(anchor="w")
        
        CustomLabel(
            title_frame,
            text="Manage and process license applications",
            size=12,
            color=("#888888", "#888888")
        ).pack(anchor="w")
        
        # Filter buttons
        filter_frame = CustomFrame(self, transparent=True)
        filter_frame.pack(fill="x", padx=30, pady=10)
        
        filters = [
            ("All", "all"),
            ("Pending", "pending"),
            ("Approved", "approved"),
            ("Rejected", "rejected")
        ]
        
        for label, filter_value in filters:
            btn = CustomButton(
                filter_frame,
                text=label,
                command=lambda f=filter_value: self._apply_filter(f),
                width=100,
                height=35,
                style="primary" if filter_value == self.current_filter else "secondary"
            )
            btn.pack(side="left", padx=5)
        
        # Scrollable applications list
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=("#2a2a2a", "#2a2a2a"),
            scrollbar_button_hover_color=("#3a3a3a", "#3a3a3a")
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Load applications
        self._load_applications()
    
    def _apply_filter(self, filter_value):
        """Apply filter to applications"""
        self.current_filter = filter_value
        
        # Recreate UI
        for widget in self.winfo_children():
            widget.destroy()
        
        self._create_ui()
    
    def _load_applications(self):
        """Load and display applications"""
        # Clear current list
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        # Get applications
        if self.current_filter == "all":
            applications = self.activation_system.get_all_applications()
        else:
            applications = self.activation_system.get_all_applications(self.current_filter)
        
        if not applications:
            CustomLabel(
                self.scroll_frame,
                text="No applications found",
                size=14,
                color=("#888888", "#888888")
            ).pack(pady=50)
            return
        
        # Create application cards in grid (4 per row)
        grid_row = None
        for idx, app in enumerate(applications):
            # Create new row every 4 cards
            if idx % 4 == 0:
                grid_row = CustomFrame(self.scroll_frame, transparent=True)
                grid_row.pack(fill="x", pady=5)
            
            self._create_application_card(grid_row, app)
    
    def _create_application_card(self, parent, app):
        """Create an application card"""
        # Status colors
        status_colors = {
            'pending': ("#f7630c", "#f7630c"),
            'approved': ("#2d7a2d", "#2d7a2d"),
            'rejected': ("#c42b1c", "#c42b1c")
        }
        
        border_color = status_colors.get(app['status'], ("#3a3a3a", "#3a3a3a"))
        
        card = CustomFrame(parent, transparent=False, width=self.CARD_WIDTH, height=self.CARD_HEIGHT)
        card.pack(side="left", padx=5, pady=10)
        card.pack_propagate(False)  # Förhindra att innehållet ändrar storleken
        card.configure(
            border_width=2, 
            border_color=border_color, 
            corner_radius=10,
            fg_color=("#2b2b2b", "#2b2b2b")  # Mörk grå som License Management
        )
        
        content = CustomFrame(card, transparent=True)
        content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header row
        header_row = CustomFrame(content, transparent=True)
        header_row.pack(fill="x")
        
        # Name and company
        info_frame = CustomFrame(header_row, transparent=True)
        info_frame.pack(side="left")
        
        CustomLabel(
            info_frame,
            text=app['name'],
            size=14,
            bold=True
        ).pack(anchor="w")
        
        # Company (dubbelklick för att kopiera)
        company_label = CustomLabel(
            info_frame,
            text=app['company'],
            size=12,
            color=("#aaaaaa", "#aaaaaa")
        )
        company_label.pack(anchor="w")
        company_label.bind("<Double-Button-1>", lambda e, t=app['company']: self._copy_to_clipboard(t))
        
        # Email (dubbelklick för att kopiera)
        email_label = CustomLabel(
            info_frame,
            text=app['email'],
            size=11,
            color=("#888888", "#888888")
        )
        email_label.pack(anchor="w")
        email_label.bind("<Double-Button-1>", lambda e, t=app['email']: self._copy_to_clipboard(t))
        
        # Right side: Status badge + Edit button
        right_side = CustomFrame(header_row, transparent=True)
        right_side.pack(side="right")
        
        # Edit button FÖRST - subtil penna (till höger om status)
        edit_btn = ctk.CTkButton(
            right_side,
            text="🖊",  # Penna emoji
            command=lambda a=app: self._edit_application(a),
            width=26,
            height=26,
            font=("Segoe UI", 11),
            fg_color="transparent",
            hover_color=("#3a3a3a", "#3a3a3a"),
            text_color=("#888888", "#888888"),
            corner_radius=4
        )
        edit_btn.pack(side="right", padx=(6, 0))
        
        # Status badge EFTER (till vänster om penna)
        status_frame = CustomFrame(right_side, transparent=False)
        status_frame.pack(side="right")
        status_frame.configure(
            border_width=1,
            border_color=border_color,
            corner_radius=5
        )
        
        CustomLabel(
            status_frame,
            text=app['status'].upper(),
            size=10,
            bold=True,
            color=border_color
        ).pack(padx=10, pady=5)
        
        # Details row
        details_row = CustomFrame(content, transparent=True)
        details_row.pack(fill="x", pady=(10, 0))
        
        # Visa tier från app data (dubbelklick för att kopiera)
        details_text = f"Tier: {app.get('requested_tier', 'basic').title()} | Payment: {app['payment_status'].title()}"
        details_label = CustomLabel(
            details_row,
            text=details_text,
            size=10,
            color=("#888888", "#888888")
        )
        details_label.pack(anchor="w")
        details_label.bind("<Double-Button-1>", lambda e, t=details_text: self._copy_to_clipboard(t))
        
        # Applied date on separate line (dubbelklick för att kopiera)
        applied_text = f"Applied: {app['created_at'][:10]}"
        applied_label = CustomLabel(
            details_row,
            text=applied_text,
            size=10,
            color=("#777777", "#777777")
        )
        applied_label.pack(anchor="w")
        applied_label.bind("<Double-Button-1>", lambda e, t=app['created_at'][:10]: self._copy_to_clipboard(t))
        
        # Machine UID (dubbelklick för att kopiera)
        uid_row = CustomFrame(content, transparent=True)
        uid_row.pack(fill="x", pady=(5, 0))
        
        uid_label = CustomLabel(
            uid_row,
            text=f"Machine ID: {app['machine_uid']}",
            size=10,
            color=("#cccccc", "#cccccc")
        )
        uid_label.pack(anchor="w")
        uid_label.bind("<Double-Button-1>", lambda e, t=app['machine_uid']: self._copy_to_clipboard(t))
        
        # License key if approved (dubbelklick för att kopiera)
        if app['license_key']:
            key_label = CustomLabel(
                uid_row,
                text=f"🔑 License: {app['license_key']}",
                size=10,
                color=("#28a745", "#28a745"),
                bold=True
            )
            key_label.pack(anchor="w", pady=(3, 0))
            key_label.bind("<Double-Button-1>", lambda e, t=app['license_key']: self._copy_to_clipboard(t))
        
        # Action buttons (only for pending) - custom mini labels som knappar
        if app['status'] == 'pending':
            action_row = CustomFrame(content, transparent=True)
            action_row.pack(fill="x", pady=(8, 0))
            
            # Approve button (mini)
            approve_frame = ctk.CTkFrame(
                action_row,
                width=18,
                height=18,
                fg_color=("#2d7a2d", "#2d7a2d"),
                corner_radius=2
            )
            approve_frame.pack(side="left", padx=1)
            approve_frame.pack_propagate(False)
            
            approve_label = ctk.CTkLabel(
                approve_frame,
                text="✓",
                font=("Segoe UI", 10, "bold"),
                text_color="#ffffff"
            )
            approve_label.pack(expand=True)
            approve_frame.bind("<Button-1>", lambda e, a=app: self._approve_application(a))
            approve_label.bind("<Button-1>", lambda e, a=app: self._approve_application(a))
            approve_frame.bind("<Enter>", lambda e: approve_frame.configure(fg_color=("#3d8a3d", "#3d8a3d")))
            approve_frame.bind("<Leave>", lambda e: approve_frame.configure(fg_color=("#2d7a2d", "#2d7a2d")))
            
            # Reject button (mini)
            reject_frame = ctk.CTkFrame(
                action_row,
                width=18,
                height=18,
                fg_color=("#c42b1c", "#c42b1c"),
                corner_radius=2
            )
            reject_frame.pack(side="left", padx=1)
            reject_frame.pack_propagate(False)
            
            reject_label = ctk.CTkLabel(
                reject_frame,
                text="✗",
                font=("Segoe UI", 10, "bold"),
                text_color="#ffffff"
            )
            reject_label.pack(expand=True)
            reject_frame.bind("<Button-1>", lambda e, a=app: self._reject_application(a))
            reject_label.bind("<Button-1>", lambda e, a=app: self._reject_application(a))
            reject_frame.bind("<Enter>", lambda e: reject_frame.configure(fg_color=("#d43b2c", "#d43b2c")))
            reject_frame.bind("<Leave>", lambda e: reject_frame.configure(fg_color=("#c42b1c", "#c42b1c")))
            
            # Mark as paid (mini)
            paid_frame = ctk.CTkFrame(
                action_row,
                width=18,
                height=18,
                fg_color=("#3a3a3a", "#3a3a3a"),
                corner_radius=2
            )
            paid_frame.pack(side="left", padx=1)
            paid_frame.pack_propagate(False)
            
            paid_label = ctk.CTkLabel(
                paid_frame,
                text="💳",
                font=("Segoe UI", 8),
                text_color="#ffffff"
            )
            paid_label.pack(expand=True)
            paid_frame.bind("<Button-1>", lambda e, a=app: self._mark_as_paid(a))
            paid_label.bind("<Button-1>", lambda e, a=app: self._mark_as_paid(a))
            paid_frame.bind("<Enter>", lambda e: paid_frame.configure(fg_color=("#4a4a4a", "#4a4a4a")))
            paid_frame.bind("<Leave>", lambda e: paid_frame.configure(fg_color=("#3a3a3a", "#3a3a3a")))
    
    def _approve_application(self, app):
        """Approve application and generate license key"""
        from core.ui_components import MessageBox
        
        # Generate license key
        temp_license = LicenseSystem(user_id=app['id'])
        key = temp_license.generate_license(app['requested_tier'], duration_days=365)
        
        # Process application
        success, message = self.activation_system.process_application(
            application_id=app['id'],
            status='approved',
            payment_status=app['payment_status'],
            license_key=key,
            notes="Approved by admin",
            processed_by=1  # SuperAdmin ID
        )
        
        if success:
            MessageBox.show_success(
                self.winfo_toplevel(),
                "Application Approved!",
                f"License key generated:\n\n{key}\n\nAn email will be sent to {app['email']}"
            )
            
            # Reload applications
            self._load_applications()
        else:
            MessageBox.show_error(
                self.winfo_toplevel(),
                "Approval Failed",
                message
            )
    
    def _reject_application(self, app):
        """Reject application"""
        from core.ui_components import MessageBox
        
        success, message = self.activation_system.process_application(
            application_id=app['id'],
            status='rejected',
            payment_status=app['payment_status'],
            notes="Rejected by admin",
            processed_by=1
        )
        
        if success:
            MessageBox.show_success(
                self.winfo_toplevel(),
                "Application Rejected",
                f"Application from {app['email']} has been rejected"
            )
            
            self._load_applications()
        else:
            MessageBox.show_error(
                self.winfo_toplevel(),
                "Rejection Failed",
                message
            )
    
    def _mark_as_paid(self, app):
        """Mark application as paid"""
        from core.ui_components import MessageBox
        
        success, message = self.activation_system.process_application(
            application_id=app['id'],
            status=app['status'],
            payment_status='paid',
            notes="Marked as paid by admin",
            processed_by=1
        )
        
        if success:
            MessageBox.show_success(
                self.winfo_toplevel(),
                "Payment Updated",
                f"Application from {app['email']} marked as paid"
            )
            self._load_applications()
        else:
            MessageBox.show_error(
                self.winfo_toplevel(),
                "Update Failed",
                message
            )
    
    def _edit_application(self, app):
        """Edit application - uses CustomDialog for borderless design"""
        from core.ui_components import MessageBox, CustomLabel, CustomButton
        from core.custom_window import CustomDialog
        
        # Create borderless dialog using CustomDialog
        dialog = CustomDialog(
            self.winfo_toplevel(),
            title="✏️ Edit Application",
            width=420,
            height=280
        )
        
        # Content (no duplicate header - CustomDialog already has title)
        content = CustomFrame(dialog.content_frame, transparent=True)
        content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Tier - Buttons for selection
        tier_row = CustomFrame(content, transparent=True)
        tier_row.pack(fill="x", pady=8)
        CustomLabel(tier_row, text="Tier", size=11, bold=True).pack(side="left")
        
        tier_var = ctk.StringVar(value=app['requested_tier'])
        tier_frame = CustomFrame(tier_row, transparent=True)
        tier_frame.pack(side="right")
        
        tier_buttons = {}
        for tier in ["basic", "standard", "pro", "enterprise", "ultimate"]:
            is_selected = tier == app['requested_tier']
            btn = ctk.CTkButton(
                tier_frame,
                text=tier[:3].upper(),  # BAS, STA, PRO, ENT, ULT
                command=lambda t=tier: self._update_tier_selection(tier_var, tier_buttons, t),
                width=35,
                height=28,
                font=("Segoe UI", 9, "bold"),
                fg_color=("#1f6aa5", "#144870") if is_selected else ("#3a3a3a", "#3a3a3a"),
                hover_color=("#1a5a8f", "#0f3a5f"),
                corner_radius=4
            )
            btn.pack(side="left", padx=1)
            tier_buttons[tier] = btn
        
        # Status - Buttons for selection
        status_row = CustomFrame(content, transparent=True)
        status_row.pack(fill="x", pady=8)
        CustomLabel(status_row, text="Status", size=11, bold=True).pack(side="left")
        
        status_var = ctk.StringVar(value=app['status'])
        status_frame = CustomFrame(status_row, transparent=True)
        status_frame.pack(side="right")
        
        status_buttons = {}
        for status in ["pending", "approved", "rejected"]:
            is_selected = status == app['status']
            btn = ctk.CTkButton(
                status_frame,
                text=status.title(),
                command=lambda s=status: self._update_status_selection(status_var, status_buttons, s),
                width=60,
                height=28,
                font=("Segoe UI", 10),
                fg_color=("#1f6aa5", "#144870") if is_selected else ("#3a3a3a", "#3a3a3a"),
                hover_color=("#1a5a8f", "#0f3a5f"),
                corner_radius=4
            )
            btn.pack(side="left", padx=2)
            status_buttons[status] = btn
        
        # Payment - Buttons for selection
        payment_row = CustomFrame(content, transparent=True)
        payment_row.pack(fill="x", pady=8)
        CustomLabel(payment_row, text="Payment", size=11, bold=True).pack(side="left")
        
        payment_var = ctk.StringVar(value=app['payment_status'])
        payment_frame = CustomFrame(payment_row, transparent=True)
        payment_frame.pack(side="right")
        
        payment_buttons = {}
        for payment in ["pending", "paid", "failed"]:
            is_selected = payment == app['payment_status']
            btn = ctk.CTkButton(
                payment_frame,
                text=payment.title(),
                command=lambda p=payment: self._update_payment_selection(payment_var, payment_buttons, p),
                width=60,
                height=28,
                font=("Segoe UI", 10),
                fg_color=("#1f6aa5", "#144870") if is_selected else ("#3a3a3a", "#3a3a3a"),
                hover_color=("#1a5a8f", "#0f3a5f"),
                corner_radius=4
            )
            btn.pack(side="left", padx=2)
            payment_buttons[payment] = btn
        
        # Compact buttons
        btn_row = CustomFrame(content, transparent=True)
        btn_row.pack(pady=(20, 0))
        
        def send_email():
            """Send email to applicant"""
            try:
                from core.license_email_service import LicenseEmailService
                email_service = LicenseEmailService()
                
                # Generera license key om approved + paid
                license_key = None
                if status_var.get() == "approved" and payment_var.get() == "paid":
                    license_key = self._generate_license_key(app['machine_uid'], tier_var.get(), app['id'])
                
                # Skicka custom email med HTML (använd 'company' och 'name')
                company = app.get('company', 'Valued Customer')
                name = app.get('name', '')
                machine_uid = app.get('machine_uid', 'N/A')
                
                subject = f"License Application Update - {company}"
                
                # Bygg email med license key om approved
                license_section = ""
                if license_key:
                    license_section = f"""
                    <div style="background: #d4edda; border: 2px solid #28a745; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #155724; margin-top: 0;">🎉 License Approved!</h3>
                        <p style="font-size: 14px; color: #155724; margin-bottom: 15px;">
                            <strong>Company:</strong><br>
                            <span style="font-size: 18px; font-weight: bold;">{company}</span>
                        </p>
                        <p style="font-size: 14px; color: #155724;">
                            <strong>License Key:</strong><br>
                            <code style="background: #fff; padding: 10px; display: block; margin: 10px 0; font-size: 16px; border: 1px solid #28a745; border-radius: 4px; font-weight: bold;">{license_key}</code>
                        </p>
                        <p style="font-size: 12px; color: #155724; margin-bottom: 0;">
                            Please save this license key. You will need it to activate your application.
                        </p>
                    </div>
                    """
                
                html_body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2>License Application Update</h2>
                    <p>Dear {name or company},</p>
                    <p>Your license application has been updated:</p>
                    <ul>
                        <li><strong>Company:</strong> {company}</li>
                        <li><strong>Machine ID:</strong> <code>{machine_uid}</code></li>
                        <li><strong>Tier:</strong> {tier_var.get().title()}</li>
                        <li><strong>Status:</strong> {status_var.get().title()}</li>
                        <li><strong>Payment:</strong> {payment_var.get().title()}</li>
                    </ul>
                    {license_section}
                    <p>Best regards,<br>MultiTeam License Team</p>
                </body>
                </html>
                """
                success = email_service._send_email(
                    to_email=app['email'],
                    subject=subject,
                    html_body=html_body
                )
                
                if success:
                    MessageBox.show_success(
                        self.winfo_toplevel(),
                        "Email Sent",
                        f"Email sent to {app['email']}"
                    )
                else:
                    MessageBox.show_error(
                        self.winfo_toplevel(),
                        "Email Failed",
                        "Failed to send email"
                    )
            except Exception as e:
                from core.debug_logger import error
                error("AdminLicenseApps", f"Email error: {e}")
                MessageBox.show_error(
                    self.winfo_toplevel(),
                    "Email Error",
                    str(e)
                )
        
        def save_changes():
            # Uppdatera tier i databasen FÖRST
            try:
                import sqlite3
                conn = sqlite3.connect('data/license_applications.db')
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE license_applications SET requested_tier = ? WHERE id = ?",
                    (tier_var.get(), app['id'])
                )
                conn.commit()
                conn.close()
                from core.debug_logger import info
                info("AdminLicenseApps", f"Tier updated to {tier_var.get()} for app {app['id']}")
            except Exception as e:
                from core.debug_logger import error
                error("AdminLicenseApps", f"Failed to update tier: {e}")
            
            # Sedan process_application för status/payment
            success, message = self.activation_system.process_application(
                application_id=app['id'],
                status=status_var.get(),
                payment_status=payment_var.get(),
                notes=f"Updated: tier={tier_var.get()}, status={status_var.get()}, payment={payment_var.get()}",
                processed_by=1
            )
            
            # Generera license key om approved + paid (EFTER process_application)
            license_key = None
            if success and status_var.get() == "approved" and payment_var.get() == "paid":
                license_key = self._generate_license_key(app['machine_uid'], tier_var.get(), app['id'])
                from core.debug_logger import info
                info("AdminLicenseApps", f"Generated and activated license key: {license_key} for app {app['id']}")
            
            if success:
                # Stäng dialog och ladda om
                dialog._close_dialog()
                self._load_applications()
                
                # Visa success efter reload
                self.after(100, lambda: MessageBox.show_success(
                    self.winfo_toplevel(),
                    "Updated",
                    f"Tier: {tier_var.get().title()}, Status: {status_var.get().title()}"
                ))
            else:
                MessageBox.show_error(
                    self.winfo_toplevel(),
                    "Failed",
                    message
                )
        
        CustomButton(
            btn_row,
            text="💾 Save",
            command=save_changes,
            width=100,
            height=35,
            style="primary"
        ).pack(side="left", padx=5)
        
        CustomButton(
            btn_row,
            text="📧 Email",
            command=send_email,
            width=100,
            height=35,
            style="secondary"
        ).pack(side="left", padx=5)
        
        CustomButton(
            btn_row,
            text="✖ Cancel",
            command=dialog._close_dialog,
            width=100,
            height=35,
            style="secondary"
        ).pack(side="left", padx=5)
    
    def _update_tier_selection(self, tier_var, tier_buttons, selected_tier):
        """Update tier selection and button colors"""
        tier_var.set(selected_tier)
        for tier, btn in tier_buttons.items():
            if tier == selected_tier:
                btn.configure(fg_color=("#1f6aa5", "#144870"))
            else:
                btn.configure(fg_color=("#3a3a3a", "#3a3a3a"))
    
    def _update_status_selection(self, status_var, status_buttons, selected_status):
        """Update status selection and button colors"""
        status_var.set(selected_status)
        for status, btn in status_buttons.items():
            if status == selected_status:
                btn.configure(fg_color=("#1f6aa5", "#144870"))
            else:
                btn.configure(fg_color=("#3a3a3a", "#3a3a3a"))
    
    def _update_payment_selection(self, payment_var, payment_buttons, selected_payment):
        """Update payment selection and button colors"""
        payment_var.set(selected_payment)
        for payment, btn in payment_buttons.items():
            if payment == selected_payment:
                btn.configure(fg_color=("#1f6aa5", "#144870"))
            else:
                btn.configure(fg_color=("#3a3a3a", "#3a3a3a"))
    
    def _generate_license_key(self, machine_uid: str, tier: str, app_id: int = None) -> str:
        """Generate unique license key based on machine UID and tier"""
        import hashlib
        import secrets
        from datetime import datetime
        
        # Skapa unik seed från machine_uid, tier och timestamp
        seed = f"{machine_uid}-{tier}-{datetime.now().isoformat()}-{secrets.token_hex(8)}"
        hash_obj = hashlib.sha256(seed.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Format: TIER-XXXX-XXXX-XXXX-XXXX
        tier_prefix = tier[:3].upper()  # BAS, STA, PRO, ENT, ULT
        key_parts = [
            tier_prefix,
            hash_hex[0:4].upper(),
            hash_hex[4:8].upper(),
            hash_hex[8:12].upper(),
            hash_hex[12:16].upper()
        ]
        
        license_key = "-".join(key_parts)
        
        # Hash license key för säkerhet
        key_hash = hashlib.sha256(license_key.encode()).hexdigest()
        
        # Spara license key och hash i databasen
        try:
            import sqlite3
            conn = sqlite3.connect('data/license_applications.db')
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE license_applications SET license_key = ?, license_key_hash = ? WHERE machine_uid = ?",
                (license_key, key_hash, machine_uid)
            )
            conn.commit()
            
            # Aktivera licensen automatiskt om app_id finns
            if app_id:
                # Hämta app data
                cursor.execute("""
                    SELECT email, company FROM license_applications WHERE id = ?
                """, (app_id,))
                app_data = cursor.fetchone()
                
                if app_data:
                    email, company = app_data
                    # Skapa aktiv license
                    cursor.execute("""
                        INSERT OR REPLACE INTO active_licenses (
                            license_key, license_key_hash, machine_uid,
                            email, company, tier, activated_at,
                            last_validated, application_id, is_active
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                    """, (
                        license_key, key_hash, machine_uid,
                        email, company, tier,
                        datetime.now().isoformat(),
                        datetime.now().isoformat(),
                        app_id
                    ))
                    conn.commit()
                    from core.debug_logger import info
                    info("AdminLicenseApps", f"License activated: {license_key[:8]}...")
            
            conn.close()
        except Exception as e:
            from core.debug_logger import error
            error("AdminLicenseApps", f"Failed to save license key: {e}")
        
        return license_key
    
    def _copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            
            from core.ui_components import MessageBox
            MessageBox.show_success(
                self.winfo_toplevel(),
                "Copied!",
                "Text copied to clipboard"
            )
        except Exception as e:
            from core.ui_components import MessageBox
            MessageBox.show_error(
                self.winfo_toplevel(),
                "Copy Failed",
                f"Failed to copy: {e}"
            )


# Debug logging
debug("AdminLicenseApps", "Admin license applications module loaded")

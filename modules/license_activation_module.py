"""
License Activation Module
UI for trial activation and license application
"""

import customtkinter as ctk
from core.ui_components import CustomFrame, CustomLabel, CustomButton
from core.debug_logger import debug, info
from core.license_activation import LicenseActivation

class LicenseActivationModule(CustomFrame):
    """License activation and application UI"""
    
    def __init__(self, parent, on_success=None):
        super().__init__(parent, transparent=False)
        self.on_success = on_success
        self.activation_system = LicenseActivation()
        
        debug("LicenseActivation", "Initializing license activation module")
        
        self._create_ui()
        
        info("LicenseActivation", "License activation module initialized")
    
    def _create_ui(self):
        """Create UI"""
        # Get machine UID
        machine_uid = self.activation_system.get_machine_uid()
        
        # Main container
        container = CustomFrame(self, transparent=True)
        container.pack(expand=True)
        
        # Logo/Title
        title_frame = CustomFrame(container, transparent=True)
        title_frame.pack(pady=(50, 30))
        
        CustomLabel(
            title_frame,
            text="🔑 MultiTeam License Activation",
            size=28,
            bold=True
        ).pack()
        
        CustomLabel(
            title_frame,
            text="Activate your license to continue",
            size=14,
            color=("#888888", "#888888")
        ).pack(pady=(10, 0))
        
        # Machine UID display
        uid_frame = CustomFrame(container, transparent=False)
        uid_frame.pack(pady=20, padx=50)
        uid_frame.configure(
            border_width=2,
            border_color=("#3a3a3a", "#3a3a3a"),
            corner_radius=10
        )
        
        uid_content = CustomFrame(uid_frame, transparent=True)
        uid_content.pack(padx=20, pady=15)
        
        # Machine ID label
        CustomLabel(
            uid_content,
            text="Machine ID:",
            size=11,
            color=("#888888", "#888888")
        ).pack(anchor="w")
        
        # Machine ID value (read-only entry istället för textbox)
        uid_value = ctk.CTkEntry(
            uid_content,
            width=500,
            height=40,
            fg_color=("#2b2b2b", "#2b2b2b"),
            text_color=("#ffffff", "#ffffff"),
            border_width=1,
            border_color=("#3a3a3a", "#3a3a3a"),
            corner_radius=5,
            font=("Consolas", 11),
            state="readonly"  # Read-only men synlig text
        )
        uid_value.pack(pady=(5, 10))
        uid_value.configure(state="normal")
        uid_value.insert(0, machine_uid)
        uid_value.configure(state="readonly")
        
        # Options container
        options_frame = CustomFrame(container, transparent=True)
        options_frame.pack(pady=30)
        # Trial activation card
        trial_card = self._create_option_card(
            options_frame,
            "🎁 Start 30-Day Trial",
            "Try all features free for 30 days",
            "Start Trial",
            self._activate_trial
        )
        trial_card.pack(side="left", padx=15)
        
        # License application card
        app_card = self._create_option_card(
            options_frame,
            "📝 Apply for License",
            "Submit application for full license",
            "Apply Now",
            self._show_application_form
        )
        app_card.pack(side="left", padx=15)
        
        # Already have license
        license_frame = CustomFrame(container, transparent=True)
        license_frame.pack(pady=20)
        
        CustomLabel(
            license_frame,
            text="Already have a license key?",
            size=11,
            color=("#888888", "#888888")
        ).pack()
        
        enter_key_btn = CustomButton(
            license_frame,
            text="Enter License Key",
            command=self._show_enter_key_dialog,
            width=150,
            height=35,
            style="secondary"
        )
        enter_key_btn.pack(pady=(10, 0))
    
    def _create_option_card(self, parent, title, description, button_text, command):
        """Create an option card"""
        card = CustomFrame(parent, transparent=False)
        card.configure(
            border_width=2,
            border_color=("#3a3a3a", "#3a3a3a"),
            corner_radius=10,
            width=300,
            height=200
        )
        card.pack_propagate(False)
        
        content = CustomFrame(card, transparent=True)
        content.pack(expand=True, padx=20, pady=20)
        
        # Title
        CustomLabel(
            content,
            text=title,
            size=16,
            bold=True
        ).pack(pady=(10, 5))
        
        # Description
        CustomLabel(
            content,
            text=description,
            size=11,
            color=("#888888", "#888888")
        ).pack(pady=(0, 20))
        
        # Button
        btn = CustomButton(
            content,
            text=button_text,
            command=command,
            width=200,
            height=40,
            style="primary"
        )
        btn.pack(pady=(10, 0))
        
        return card
    
    def _activate_trial(self):
        """Activate 30-day trial"""
        from core.ui_components import MessageBox
        
        # Check trial status first
        status = self.activation_system.check_trial_status()
        
        if status['has_trial']:
            MessageBox.show_error(
                self.winfo_toplevel(),
                "Trial Already Used",
                status['message']
            )
            return
        
        # Activate trial
        success, message = self.activation_system.activate_trial()
        
        if success:
            MessageBox.show_success(
                self.winfo_toplevel(),
                "Trial Activated!",
                f"{message}\n\nYou can now use all features for 30 days."
            )
            
            # Call success callback
            if self.on_success:
                self.on_success()
        else:
            MessageBox.show_error(
                self.winfo_toplevel(),
                "Activation Failed",
                message
            )
    
    def _show_application_form(self):
        """Show license application form"""
        # Clear current UI
        for widget in self.winfo_children():
            widget.destroy()
        
        # Create application form
        from modules.license_application_module import LicenseApplicationModule
        
        app_module = LicenseApplicationModule(
            self,
            activation_system=self.activation_system,
            on_back=self._create_ui,
            on_success=self.on_success
        )
        app_module.pack(fill="both", expand=True)
    
    def _show_enter_key_dialog(self):
        """Show dialog to enter license key"""
        # Skapa en enkel toplevel dialog utan grab_set problem
        dialog = ctk.CTkToplevel(self.winfo_toplevel())
        dialog.title("Enter License Key")
        dialog.geometry("500x320")
        dialog.configure(fg_color=("#2b2b2b", "#2b2b2b"))
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 250
        y = (dialog.winfo_screenheight() // 2) - 160
        dialog.geometry(f"500x320+{x}+{y}")
        
        # Make modal
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Content
        content = CustomFrame(dialog, transparent=True)
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Title
        CustomLabel(
            content,
            text="Enter License Key",
            size=18,
            bold=True
        ).pack(pady=(0, 20))
        
        # Key entry
        CustomLabel(
            content,
            text="License Key:",
            size=12
        ).pack(anchor="w")
        
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
        key_entry.pack(pady=10)
        
        # Force focus after dialog is shown
        dialog.after(200, lambda: key_entry.focus_set())
        dialog.after(250, lambda: key_entry.focus_force())
        
        # Buttons
        btn_frame = CustomFrame(content, transparent=True)
        btn_frame.pack(pady=20)
        
        def activate_key(event=None):
            key = key_entry.get().strip().upper()
            if not key:
                from core.ui_components import MessageBox
                MessageBox.show_error(dialog, "Error", "Please enter a license key")
                return
            
            # Get machine UID
            machine_uid = self.activation_system.get_machine_uid()
            
            # Försök aktivera license key direkt (hanterar både nya och befintliga)
            import sqlite3
            import hashlib
            
            try:
                conn = sqlite3.connect('data/license_applications.db')
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Hash license key
                key_hash = hashlib.sha256(key.encode()).hexdigest()
                
                # Kolla om license key finns i applications (godkänd)
                cursor.execute("""
                    SELECT * FROM license_applications
                    WHERE license_key = ? AND status = 'approved' AND payment_status = 'paid'
                """, (key,))
                
                app_data = cursor.fetchone()
                
                if not app_data:
                    conn.close()
                    from core.ui_components import MessageBox
                    MessageBox.show_error(dialog, "Invalid License", 
                                        "License key not found or not approved")
                    return
                
                # Kolla om redan aktiverad på denna maskin
                cursor.execute("""
                    SELECT * FROM active_licenses
                    WHERE license_key_hash = ? AND machine_uid = ?
                """, (key_hash, machine_uid))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Redan aktiverad på denna maskin
                    conn.close()
                    success = True
                    message = f"License already active: {app_data['requested_tier']}"
                    tier = app_data['requested_tier']
                else:
                    # Aktivera för första gången
                    from datetime import datetime
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
                    conn.close()
                    
                    success = True
                    message = f"License activated: {app_data['requested_tier']}"
                    tier = app_data['requested_tier']
                    
            except Exception as e:
                from core.debug_logger import error
                error("LicenseActivation", f"License activation error: {e}")
                from core.ui_components import MessageBox
                MessageBox.show_error(dialog, "Error", f"Activation failed: {e}")
                return
            
            from core.ui_components import MessageBox
            
            if success:
                from core.ui_components import MessageBox
                
                # Stäng input-dialogen först
                dialog.destroy()
                
                # Visa success-meddelande
                success_dialog = MessageBox.show_success(
                    self.winfo_toplevel(),
                    "License Activated!",
                    f"{message}\n\nThe application will restart to apply the new license."
                )
                
                # Vänta lite så användaren ser meddelandet, sedan starta om
                def restart_app():
                    try:
                        import sys
                        import os
                        # Stäng alla dialoger
                        for widget in self.winfo_toplevel().winfo_children():
                            if isinstance(widget, (ctk.CTkToplevel,)):
                                try:
                                    widget.destroy()
                                except:
                                    pass
                        # Starta om appen
                        os.execv(sys.executable, ['python'] + sys.argv)
                    except Exception as e:
                        from core.debug_logger import error
                        error("LicenseActivation", f"Restart error: {e}")
                
                # Vänta 2 sekunder innan restart
                self.after(2000, restart_app)
            else:
                MessageBox.show_error(
                    dialog,
                    "Activation Failed",
                    message
                )
        
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
        
        # Bind Enter key to activate
        key_entry.bind("<Return>", activate_key)
    
    def _copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            self.winfo_toplevel().clipboard_clear()
            self.winfo_toplevel().clipboard_append(text)
            self.winfo_toplevel().update()
            
            from core.ui_components import MessageBox
            MessageBox.show_success(
                self.winfo_toplevel(),
                "Copied!",
                "Machine ID copied to clipboard"
            )
        except Exception as e:
            from core.ui_components import MessageBox
            MessageBox.show_error(
                self.winfo_toplevel(),
                "Copy Failed",
                f"Failed to copy: {e}"
            )


# Debug logging
debug("LicenseActivation", "License activation module loaded")

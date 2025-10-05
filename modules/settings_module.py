"""
Global Settings Module
UI för att hantera globala applikationsinställningar
"""

import customtkinter as ctk
from typing import Callable
from core.debug_logger import debug, info, warning, error
from core.ui_components import (
    CustomButton, CustomLabel, CustomFrame, 
    CustomCheckbox, MessageBox
)
from core.global_settings import settings


class SettingsModule(ctk.CTkFrame):
    """Global settings module"""
    
    def __init__(
        self,
        master,
        on_back: Callable,
        **kwargs
    ):
        """Initialize settings module"""
        debug("SettingsModule", "Initializing settings module")
        
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.on_back = on_back
        self.settings = settings
        
        # Store checkbox references
        self.checkboxes = {}
        
        self._create_ui()
        
        info("SettingsModule", "Settings module initialized")
    
    def _create_ui(self):
        """Create settings UI"""
        debug("SettingsModule", "Creating settings UI")
        
        # Main container - no scrolling
        container = CustomFrame(self, transparent=False)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Content frame - fixed, no scrolling
        content_frame = CustomFrame(container, transparent=True)
        content_frame.pack(fill="both", expand=False, padx=20, pady=(10, 5))
        
        # Title - smaller
        title_label = CustomLabel(
            content_frame,
            text="⚙️ Global Settings",
            size=20,
            bold=True
        )
        title_label.pack(pady=(5, 2))
        
        subtitle_label = CustomLabel(
            content_frame,
            text="Konfigurera applikationsinställningar",
            size=10,
            color=("#999999", "#999999")
        )
        subtitle_label.pack(pady=(0, 10))
        
        # Three column layout
        columns_frame = CustomFrame(content_frame, transparent=True)
        columns_frame.pack(fill="both", expand=True, pady=10)
        
        # Left column
        left_column = CustomFrame(columns_frame, transparent=True)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Middle column
        middle_column = CustomFrame(columns_frame, transparent=True)
        middle_column.pack(side="left", fill="both", expand=True, padx=5)
        
        # Right column
        right_column = CustomFrame(columns_frame, transparent=True)
        right_column.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        # LEFT COLUMN - Authentication Settings
        self._create_section(
            left_column,
            "🔐 Authentication",
            [
                ("email_verification_enabled", "Email Verification", 
                 "Kräv email-verifiering vid registrering"),
                ("2fa_enabled", "Two-Factor Authentication", 
                 "Aktivera 2FA-funktionalitet"),
                ("2fa_required_for_all", "Require 2FA for All", 
                 "Tvinga alla att använda 2FA"),
            ]
        )
        
        # Session Settings
        self._create_section(
            left_column,
            "⏱️ Session",
            [
                ("password_reset_enabled", "Password Reset", 
                 "Tillåt lösenordsåterställning"),
            ]
        )
        
        # MIDDLE COLUMN - System Settings
        self._create_section(
            middle_column,
            "💻 System",
            [
                ("minimize_to_tray", "Minimize to System Tray", 
                 "Minimera till system tray istället för att stänga"),
            ]
        )
        
        # OAuth Settings
        self._create_section(
            middle_column,
            "🌐 OAuth & Social",
            [
                ("google_oauth_enabled", "Google OAuth Login", 
                 "Aktivera Google-inloggning"),
            ]
        )
        
        # Notifications Settings
        self._create_section(
            middle_column,
            "🔔 Notifications",
            [
                ("desktop_notifications_enabled", "Desktop Notifications", 
                 "Visa Windows Toast notifications"),
                ("sound_notifications_enabled", "Sound Notifications", 
                 "Spela ljud vid notifikationer"),
            ]
        )
        
        # RIGHT COLUMN - Appearance & Updates
        appearance_section = CustomFrame(right_column, transparent=False)
        appearance_section.pack(fill="x", pady=(0, 10))
        
        appearance_container = CustomFrame(appearance_section, transparent=True)
        appearance_container.pack(fill="x", padx=15, pady=15)
        
        CustomLabel(
            appearance_container,
            text="🎨 Appearance",
            size=14,
            bold=True
        ).pack(anchor="w", pady=(0, 10))
        
        # Theme selector
        CustomLabel(
            appearance_container,
            text="Theme:",
            size=11
        ).pack(anchor="w", pady=(0, 5))
        
        current_theme = self.settings.get("app_theme", "dark")
        self.theme_var = ctk.StringVar(value=current_theme)
        
        theme_options = ctk.CTkSegmentedButton(
            appearance_container,
            values=["dark", "light"],
            variable=self.theme_var,
            command=self._on_theme_change,
            width=200
        )
        theme_options.pack(anchor="w", pady=(0, 10))
        
        # Auto-Update Section in right column
        update_section = CustomFrame(right_column, transparent=False)
        update_section.pack(fill="x", pady=(0, 10))
        
        update_container = CustomFrame(update_section, transparent=True)
        update_container.pack(fill="x", padx=15, pady=15)
        
        CustomLabel(
            update_container,
            text="🔄 Auto-Update",
            size=14,
            bold=True
        ).pack(anchor="w", pady=(0, 10))
        
        CustomLabel(
            update_container,
            text="Check for updates",
            size=10,
            color=("#999999", "#999999")
        ).pack(anchor="w", pady=(0, 10))
        
        update_btn = CustomButton(
            update_container,
            text="🔍 Check Updates",
            command=self._check_for_updates,
            width=180,
            height=35,
            style="primary"
        )
        update_btn.pack(anchor="w")
        
        # License Management Section (Right column)
        license_container = CustomFrame(right_column, transparent=False)
        license_container.pack(fill="x", pady=(0, 10))
        license_container.configure(
            border_width=1,
            border_color=("#3a3a3a", "#3a3a3a"),
            corner_radius=5
        )
        
        license_content = CustomFrame(license_container, transparent=True)
        license_content.pack(fill="x", padx=15, pady=15)
        
        CustomLabel(
            license_content,
            text="🔑 License Management",
            size=14,
            bold=True
        ).pack(anchor="w", pady=(0, 10))
        
        CustomLabel(
            license_content,
            text="Manage your license keys",
            size=10,
            color=("#999999", "#999999")
        ).pack(anchor="w", pady=(0, 10))
        
        license_btn = CustomButton(
            license_content,
            text="🔑 Manage Licenses",
            command=self._show_license_management,
            width=180,
            height=35,
            style="primary"
        )
        license_btn.pack(anchor="w")
        
        # Action buttons - less padding
        button_frame = CustomFrame(container, transparent=True)
        button_frame.pack(pady=(5, 10))
        
        # Save button
        save_btn = CustomButton(
            button_frame,
            text="💾 Save Settings",
            command=self._save_settings,
            width=200,
            height=45,
            style="success"
        )
        save_btn.pack(side="left", padx=10)
        
        # Reset button
        reset_btn = CustomButton(
            button_frame,
            text="🔄 Reset to Defaults",
            command=self._reset_settings,
            width=200,
            height=45,
            style="secondary"
        )
        reset_btn.pack(side="left", padx=10)
        
        # Back button
        back_btn = CustomButton(
            button_frame,
            text="← Back",
            command=self._handle_back,
            width=150,
            height=45,
            style="transparent"
        )
        back_btn.pack(side="left", padx=10)
        
        debug("SettingsModule", "Settings UI created")
    
    def _create_section(self, parent, title: str, settings_list: list, show_divider: bool = True):
        """Create a settings section"""
        debug("SettingsModule", f"Creating section: {title}")
        
        # Section title
        section_title = CustomLabel(
            parent,
            text=title,
            size=16,
            bold=True
        )
        section_title.pack(anchor="w", padx=40, pady=(20, 15))
        
        # Settings items
        for setting_key, setting_label, setting_desc in settings_list:
            self._create_setting_item(parent, setting_key, setting_label, setting_desc)
        
        # Divider
        if show_divider:
            divider = ctk.CTkFrame(parent, height=1, fg_color=("#3a3a3a", "#2a2a2a"))
            divider.pack(fill="x", padx=40, pady=20)
    
    def _create_setting_item(self, parent, key: str, label: str, description: str):
        """Create a single setting item"""
        debug("SettingsModule", f"Creating setting item: {key}")
        
        item_frame = CustomFrame(parent, transparent=True)
        item_frame.pack(fill="x", padx=40, pady=10)
        
        # Left side - checkbox and labels
        left_frame = CustomFrame(item_frame, transparent=True)
        left_frame.pack(side="left", fill="x", expand=True)
        
        # Get current value
        current_value = self.settings.get(key, False)
        
        # Checkbox
        checkbox = CustomCheckbox(
            left_frame,
            text=label,
        )
        checkbox.pack(anchor="w")
        
        if current_value:
            checkbox.select()
        
        # Store reference
        self.checkboxes[key] = checkbox
        
        # Description
        desc_label = CustomLabel(
            left_frame,
            text=description,
            size=10,
            color=("#666666", "#666666")
        )
        desc_label.pack(anchor="w", padx=(25, 0), pady=(2, 0))
        
        debug("SettingsModule", f"Setting item created: {key} = {current_value}")
    
    def _on_theme_change(self, value):
        """Handle theme change"""
        debug("SettingsModule", f"Theme changed to: {value}")
        info("SettingsModule", f"Theme will be applied: {value}")
        # Theme change will be applied on save
    
    def _save_settings(self):
        """Save all settings"""
        debug("SettingsModule", "Saving settings")
        
        changes = []
        
        # Save checkbox settings
        for key, checkbox in self.checkboxes.items():
            new_value = checkbox.get() == 1
            old_value = self.settings.get(key)
            
            if new_value != old_value:
                self.settings.set(key, new_value)
                changes.append(f"{key}: {old_value} → {new_value}")
                debug("SettingsModule", f"Setting changed: {key} = {new_value}")
        
        # Save theme
        new_theme = self.theme_var.get()
        old_theme = self.settings.get("app_theme")
        if new_theme != old_theme:
            self.settings.set("app_theme", new_theme)
            changes.append(f"theme: {old_theme} → {new_theme}")
            
            # Apply theme
            ctk.set_appearance_mode(new_theme)
            debug("SettingsModule", f"Theme applied: {new_theme}")
        
        if changes:
            info("SettingsModule", f"Settings saved with {len(changes)} changes")
            MessageBox.show_success(
                self.master,
                "Settings Saved",
                f"Settings have been saved successfully.\n\n{len(changes)} change(s) applied."
            )
        else:
            info("SettingsModule", "No changes to save")
            MessageBox.show_info(
                self.master,
                "No Changes",
                "No settings were changed."
            )
    
    def _reset_settings(self):
        """Reset settings to defaults"""
        debug("SettingsModule", "Reset settings requested")
        
        def on_confirm():
            debug("SettingsModule", "Resetting settings to defaults")
            self.settings.reset_to_defaults()
            
            # Reload UI
            for widget in self.winfo_children():
                widget.destroy()
            self._create_ui()
            
            info("SettingsModule", "Settings reset to defaults")
            MessageBox.show_success(
                self.master,
                "Settings Reset",
                "All settings have been reset to default values."
            )
        
        MessageBox.show_confirm(
            self.master,
            "Reset Settings",
            "Are you sure you want to reset all settings to default values?\n\nThis action cannot be undone.",
            on_confirm
        )
    
    def _check_for_updates(self):
        """Check for application updates"""
        debug("SettingsModule", "Checking for updates")
        
        try:
            from core.auto_update import AutoUpdate
            
            auto_update = AutoUpdate()
            
            # Check for updates
            result = auto_update.check_for_updates()
            
            # Handle None result (network error)
            if result is None:
                warning("SettingsModule", "Update check returned None (network error)")
                MessageBox.show_error(
                    self.master,
                    "Update Check Failed",
                    "Failed to check for updates.\n\nPlease check your internet connection."
                )
                return
            
            has_update, latest_version = result
            
            if has_update:
                info("SettingsModule", f"Update available: {latest_version}")
                MessageBox.show_info(
                    self.master,
                    "Update Available",
                    f"A new version is available: {latest_version}\n\nWould you like to download and install it?"
                )
                # TODO: Implement download and install
            else:
                info("SettingsModule", "No updates available")
                MessageBox.show_success(
                    self.master,
                    "Up to Date",
                    "You are running the latest version of MultiTeam!"
                )
        except Exception as e:
            error("SettingsModule", f"Error checking for updates: {e}")
            MessageBox.show_error(
                self.master,
                "Update Check Failed",
                f"Failed to check for updates.\n\nError: {str(e)}"
            )
    
    def _show_license_management(self):
        """Show license management dialog"""
        debug("SettingsModule", "Opening license management")
        
        try:
            import customtkinter as ctk
            from core.license_activation import LicenseActivation
            from core.custom_window import CustomDialog
            from core.ui_components import CustomFrame, CustomLabel, CustomButton
            
            # Skapa activation system
            activation_system = LicenseActivation()
            machine_uid = activation_system.get_machine_uid()
            
            # Skapa dialog för license management
            dialog = CustomDialog(self.winfo_toplevel(), title="🔑 License Management", width=600, height=400)
            
            # Content
            content = CustomFrame(dialog.content_frame, transparent=True)
            content.pack(fill="both", expand=True, padx=30, pady=30)
            
            # Title
            CustomLabel(
                content,
                text="🔑 License Management",
                size=18,
                bold=True
            ).pack(pady=(0, 10))
            
            # Machine ID
            CustomLabel(
                content,
                text=f"Machine ID: {machine_uid}",
                size=11,
                color=("#888888", "#888888")
            ).pack(pady=(0, 20))
            
            # Enter License Key button
            CustomButton(
                content,
                text="🔑 Enter License Key",
                command=lambda: self._show_enter_key_dialog(dialog, activation_system),
                width=300,
                height=45,
                style="primary"
            ).pack(pady=10)
            
            # Apply for License button
            CustomButton(
                content,
                text="📝 Apply for License",
                command=lambda: self._show_application_form(dialog),
                width=300,
                height=45,
                style="secondary"
            ).pack(pady=10)
            
            info("SettingsModule", "License management dialog opened")
            
        except Exception as e:
            error("SettingsModule", f"Error opening license management: {e}")
            import traceback
            traceback.print_exc()
            MessageBox.show_error(
                self.master,
                "License Management Error",
                f"Failed to open license management.\n\nError: {str(e)}"
            )
    
    def _show_enter_key_dialog(self, parent_dialog, activation_system):
        """Show enter license key dialog"""
        from core.ui_components import MessageBox
        
        # Stäng parent dialog
        parent_dialog._close_dialog()
        
        # Skapa input dialog
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
        from core.ui_components import CustomFrame, CustomLabel, CustomButton
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
        
        # Force focus
        dialog.after(200, lambda: key_entry.focus_set())
        dialog.after(250, lambda: key_entry.focus_force())
        
        # Buttons
        btn_frame = CustomFrame(content, transparent=True)
        btn_frame.pack(pady=20)
        
        def activate_key(event=None):
            key = key_entry.get().strip().upper()
            if not key:
                MessageBox.show_error(dialog, "Error", "Please enter a license key")
                return
            
            # Get machine UID
            machine_uid = activation_system.get_machine_uid()
            
            # Activate license (simplified version)
            import sqlite3
            import hashlib
            from datetime import datetime
            
            try:
                conn = sqlite3.connect('data/license_applications.db')
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Hash license key
                key_hash = hashlib.sha256(key.encode()).hexdigest()
                
                # Check if license exists
                cursor.execute("""
                    SELECT * FROM license_applications
                    WHERE license_key = ? AND status = 'approved' AND payment_status = 'paid'
                """, (key,))
                
                app_data = cursor.fetchone()
                
                if not app_data:
                    conn.close()
                    MessageBox.show_error(dialog, "Invalid License", 
                                        "License key not found or not approved")
                    return
                
                # Check if already activated
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
                
                conn.close()
                
                dialog.destroy()
                MessageBox.show_success(
                    self.winfo_toplevel(),
                    "License Activated!",
                    f"License activated: {app_data['requested_tier']}"
                )
                
            except Exception as e:
                from core.debug_logger import error
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
    
    def _show_application_form(self, parent_dialog):
        """Show license application form"""
        from core.ui_components import MessageBox
        MessageBox.show_info(
            self.winfo_toplevel(),
            "Apply for License",
            "License application form will be implemented here."
        )
    
    def _handle_back(self):
        """Handle back button"""
        debug("SettingsModule", "Back button clicked")
        self.on_back()


if __name__ == "__main__":
    # Test settings module
    info("TEST", "Testing SettingsModule...")
    
    from core.custom_window import CustomWindow
    
    def on_back():
        print("Back clicked")
    
    app = CustomWindow(title="Settings Test", width=800, height=700)
    
    settings_module = SettingsModule(
        app.content_frame,
        on_back=on_back
    )
    settings_module.pack(fill="both", expand=True)
    
    info("TEST", "Starting mainloop...")
    app.mainloop()

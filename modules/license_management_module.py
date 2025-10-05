"""
License Management Module
Admin panel för att hantera licenser
"""

import customtkinter as ctk
from core.ui_components import CustomFrame, CustomLabel, CustomButton
from core.debug_logger import debug, info
from datetime import datetime

class LicenseManagementModule(CustomFrame):
    """License management admin panel"""
    
    def __init__(self, parent, license_system, on_back=None, is_superadmin=False):
        super().__init__(parent, transparent=False)
        self.license_system = license_system
        self.on_back = on_back
        self.is_superadmin = is_superadmin
        
        debug("LicenseManagement", "Initializing license management module")
        
        self._create_ui()
        
        info("LicenseManagement", "License management module initialized")
    
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
            text="📜 License Management",
            size=24,
            bold=True
        ).pack(anchor="w")
        
        CustomLabel(
            title_frame,
            text="Manage your license and upgrade options",
            size=12,
            color=("#999999", "#999999")
        ).pack(anchor="w")
        
        # Main content
        content = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=("#2a2a2a", "#2a2a2a"),
            scrollbar_button_hover_color=("#3a3a3a", "#3a3a3a")
        )
        content.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        # Combined License Info & Actions Card
        self._create_combined_info_section(content)
        
        # Upgrade Options Section
        self._create_upgrade_options_section(content)
    
    def _create_combined_info_section(self, parent):
        """Create combined license info, actions, and applications section"""
        section = CustomFrame(parent, transparent=False)
        section.pack(fill="x", pady=10)
        section.configure(border_width=2, border_color=("#3a3a3a", "#3a3a3a"), corner_radius=10)
        
        # Section header
        header = CustomFrame(section, transparent=True)
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        CustomLabel(header, text="📜 License Management", size=18, bold=True).pack(anchor="w")
        
        # Divider
        ctk.CTkFrame(section, height=1, fg_color=("#3a3a3a", "#3a3a3a")).pack(fill="x", padx=20, pady=10)
        
        # Content container with 3 columns
        content_container = CustomFrame(section, transparent=True)
        content_container.pack(fill="x", padx=20, pady=(0, 20))
        
        # Column 1: Current License Info
        col1 = CustomFrame(content_container, transparent=True)
        col1.pack(side="left", fill="both", expand=True, padx=5)
        
        CustomLabel(col1, text="Current License", size=14, bold=True).pack(anchor="w", pady=(0, 10))
        
        license_info = self.license_system.get_license_info()
        
        info_items = [
            ("Tier", license_info['tier'].title()),
            ("Status", license_info['status'].upper()),
            ("Key", license_info['key']),
            ("Expires", license_info.get('expiry_date', 'Never'))
        ]
        
        for label, value in info_items:
            row = CustomFrame(col1, transparent=True)
            row.pack(fill="x", pady=3)
            CustomLabel(row, text=f"{label}:", size=11, bold=True).pack(side="left")
            
            if label == "Key":
                CustomLabel(row, text=value, size=10, color=("#888888", "#888888")).pack(side="left", padx=5)
                copy_btn = CustomButton(
                    row,
                    text="📋",
                    command=lambda: self._copy_to_clipboard(value),
                    width=30,
                    height=20,
                    style="secondary"
                )
                copy_btn.pack(side="left")
            else:
                CustomLabel(row, text=value, size=10, color=("#888888", "#888888")).pack(side="left", padx=5)
        
        # Column 2: License Actions
        col2 = CustomFrame(content_container, transparent=True)
        col2.pack(side="left", fill="both", expand=True, padx=5)
        
        CustomLabel(col2, text="Actions", size=14, bold=True).pack(anchor="w", pady=(0, 10))
        
        actions = [
            ("🔑 Generate New Key", self._generate_new_key),
            ("✓ Validate License", self._validate_license),
            ("🔄 Refresh Info", self._refresh_info)
        ]
        
        for text, command in actions:
            btn = CustomButton(
                col2,
                text=text,
                command=command,
                width=200,
                height=35,
                style="secondary"
            )
            btn.pack(pady=3, anchor="w")
        
        # Column 3: Admin Applications (SuperAdmin only)
        if hasattr(self, 'is_superadmin') and self.is_superadmin:
            col3 = CustomFrame(content_container, transparent=True)
            col3.pack(side="left", fill="both", expand=True, padx=5)
            
            CustomLabel(col3, text="Admin", size=14, bold=True).pack(anchor="w", pady=(0, 10))
            
            CustomLabel(
                col3,
                text="Manage license applications\nand approve/reject requests",
                size=10,
                color=("#888888", "#888888")
            ).pack(anchor="w", pady=(0, 10))
            
            manage_btn = CustomButton(
                col3,
                text="🔧 Manage Applications",
                command=self._show_applications_management,
                width=200,
                height=35,
                style="primary"
            )
            manage_btn.pack(anchor="w")
    
    def _create_current_license_section(self, parent):
        """Create current license info section"""
        section = CustomFrame(parent, transparent=False)
        section.pack(fill="x", pady=10)
        section.configure(border_width=2, border_color=("#3a3a3a", "#3a3a3a"), corner_radius=10)
        
        # Section header
        header = CustomFrame(section, transparent=True)
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        CustomLabel(header, text="📋 Current License", size=18, bold=True).pack(anchor="w")
        
        # Divider
        ctk.CTkFrame(section, height=1, fg_color=("#3a3a3a", "#3a3a3a")).pack(fill="x", padx=20, pady=10)
        
        # License info
        info_frame = CustomFrame(section, transparent=True)
        info_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        license_info = self.license_system.get_license_info()
        tier_info = self.license_system.get_tier_info()
        
        # Tier
        tier_row = CustomFrame(info_frame, transparent=True)
        tier_row.pack(fill="x", pady=5)
        
        CustomLabel(tier_row, text="License Tier:", size=12, bold=True).pack(side="left")
        CustomLabel(tier_row, text=license_info['tier_name'], size=12, 
                   color=("#2d7a2d", "#2d7a2d") if license_info['status'] == 'active' else ("#c42b1c", "#c42b1c")).pack(side="left", padx=10)
        
        # Status
        status_row = CustomFrame(info_frame, transparent=True)
        status_row.pack(fill="x", pady=5)
        
        CustomLabel(status_row, text="Status:", size=12, bold=True).pack(side="left")
        status_color = ("#2d7a2d", "#2d7a2d") if license_info['status'] == 'active' else ("#c42b1c", "#c42b1c")
        CustomLabel(status_row, text=license_info['status'].upper(), size=12, color=status_color).pack(side="left", padx=10)
        
        # Key with copy button
        key_row = CustomFrame(info_frame, transparent=True)
        key_row.pack(fill="x", pady=5)
        
        CustomLabel(key_row, text="License Key:", size=12, bold=True).pack(side="left")
        CustomLabel(key_row, text=license_info['key'], size=11, 
                   color=("#888888", "#888888")).pack(side="left", padx=10)
        
        # Copy button
        copy_btn = CustomButton(
            key_row,
            text="📋 Copy",
            command=lambda: self._copy_to_clipboard(license_info['key']),
            width=80,
            height=25,
            style="secondary"
        )
        copy_btn.pack(side="left", padx=5)
        
        # Expiry
        expiry_row = CustomFrame(info_frame, transparent=True)
        expiry_row.pack(fill="x", pady=5)
        
        CustomLabel(expiry_row, text="Expires:", size=12, bold=True).pack(side="left")
        CustomLabel(expiry_row, text=license_info['expiry'], size=12).pack(side="left", padx=10)
        
        # Limits
        limits_frame = CustomFrame(info_frame, transparent=True)
        limits_frame.pack(fill="x", pady=(15, 5))
        
        CustomLabel(limits_frame, text="📊 License Limits:", size=14, bold=True).pack(anchor="w", pady=(0, 10))
        
        # Modules
        max_modules = tier_info['max_modules']
        modules_text = "Unlimited" if max_modules == -1 else f"{max_modules} modules"
        self._create_limit_row(limits_frame, "Modules:", modules_text)
        
        # Teams
        max_teams = tier_info['max_teams']
        teams_text = "Unlimited" if max_teams == -1 else f"{max_teams} teams"
        self._create_limit_row(limits_frame, "Teams:", teams_text)
        
        # Members
        max_members = tier_info['max_members_per_team']
        members_text = "Unlimited" if max_members == -1 else f"{max_members} members per team"
        self._create_limit_row(limits_frame, "Members:", members_text)
        
        # Team Groups
        groups_text = "✓ Enabled" if tier_info['team_groups'] else "✗ Disabled"
        groups_color = ("#2d7a2d", "#2d7a2d") if tier_info['team_groups'] else ("#888888", "#888888")
        self._create_limit_row(limits_frame, "Team Groups:", groups_text, groups_color)
    
    def _create_limit_row(self, parent, label, value, color=None):
        """Create a limit info row"""
        row = CustomFrame(parent, transparent=True)
        row.pack(fill="x", pady=3)
        
        CustomLabel(row, text=label, size=11, bold=True).pack(side="left", padx=(20, 10))
        CustomLabel(row, text=value, size=11, color=color if color else ("#cccccc", "#cccccc")).pack(side="left")
    
    def _create_upgrade_options_section(self, parent):
        """Create upgrade options section"""
        section = CustomFrame(parent, transparent=False)
        section.pack(fill="x", pady=10)
        section.configure(border_width=2, border_color=("#3a3a3a", "#3a3a3a"), corner_radius=10)
        
        # Section header
        header = CustomFrame(section, transparent=True)
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        CustomLabel(header, text="⬆️ Upgrade Options", size=18, bold=True).pack(anchor="w")
        
        # Divider
        ctk.CTkFrame(section, height=1, fg_color=("#3a3a3a", "#3a3a3a")).pack(fill="x", padx=20, pady=10)
        
        # Tier cards container
        cards_container = CustomFrame(section, transparent=True)
        cards_container.pack(fill="x", padx=20, pady=(0, 20))
        
        # Get all tiers
        tiers = self.license_system.get_all_tiers()
        current_tier = self.license_system.get_license_info()['tier']
        
        # Create grid container for 3 cards per row
        grid_row = None
        for idx, (tier_key, tier_data) in enumerate(tiers.items()):
            # Create new row every 3 cards
            if idx % 3 == 0:
                grid_row = CustomFrame(cards_container, transparent=True)
                grid_row.pack(fill="x", pady=5)
            
            self._create_tier_card(grid_row, tier_key, tier_data, tier_key == current_tier)
    
    def _create_tier_card(self, parent, tier_key, tier_data, is_current):
        """Create a tier upgrade card"""
        card = CustomFrame(parent, transparent=False)
        card.pack(side="left", padx=5, pady=10, fill="both", expand=True)
        
        # Border color based on current tier
        border_color = ("#2d7a2d", "#2d7a2d") if is_current else ("#3a3a3a", "#3a3a3a")
        card.configure(border_width=2, border_color=border_color, corner_radius=8)
        
        # Card content
        content = CustomFrame(card, transparent=True)
        content.pack(fill="x", padx=15, pady=15)
        
        # Header row
        header_row = CustomFrame(content, transparent=True)
        header_row.pack(fill="x")
        
        # Tier name
        tier_label = CustomFrame(header_row, transparent=True)
        tier_label.pack(side="left")
        
        CustomLabel(tier_label, text=tier_data['name'], size=16, bold=True).pack(side="left")
        
        if is_current:
            CustomLabel(tier_label, text="(Current)", size=11, 
                       color=("#2d7a2d", "#2d7a2d")).pack(side="left", padx=10)
        
        # Price
        CustomLabel(header_row, text=tier_data['price'], size=14, bold=True).pack(side="right")
        
        # Features
        features_frame = CustomFrame(content, transparent=True)
        features_frame.pack(fill="x", pady=(10, 0))
        
        # Modules
        max_modules = tier_data['max_modules']
        modules_text = "✓ Unlimited modules" if max_modules == -1 else f"✓ {max_modules} modules"
        CustomLabel(features_frame, text=modules_text, size=10).pack(anchor="w", pady=2)
        
        # Teams
        max_teams = tier_data['max_teams']
        teams_text = "✓ Unlimited teams" if max_teams == -1 else f"✓ {max_teams} teams"
        CustomLabel(features_frame, text=teams_text, size=10).pack(anchor="w", pady=2)
        
        # Members
        max_members = tier_data['max_members_per_team']
        members_text = "✓ Unlimited members" if max_members == -1 else f"✓ {max_members} members per team"
        CustomLabel(features_frame, text=members_text, size=10).pack(anchor="w", pady=2)
        
        # Team Groups
        if tier_data['team_groups']:
            CustomLabel(features_frame, text="✓ Team Groups", size=10).pack(anchor="w", pady=2)
        
        # Upgrade button
        if not is_current:
            upgrade_btn = CustomButton(
                content,
                text=f"Upgrade to {tier_data['name']}",
                command=lambda t=tier_key: self._upgrade_license(t),
                width=200,
                height=35,
                style="primary"
            )
            upgrade_btn.pack(pady=(10, 0))
    
    def _create_actions_section(self, parent):
        """Create license actions section"""
        section = CustomFrame(parent, transparent=False)
        section.pack(fill="x", pady=10)
        section.configure(border_width=2, border_color=("#3a3a3a", "#3a3a3a"), corner_radius=10)
        
        # Section header
        header = CustomFrame(section, transparent=True)
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        CustomLabel(header, text="⚙️ License Actions", size=18, bold=True).pack(anchor="w")
        
        # Divider
        ctk.CTkFrame(section, height=1, fg_color=("#3a3a3a", "#3a3a3a")).pack(fill="x", padx=20, pady=10)
        
        # Actions
        actions_frame = CustomFrame(section, transparent=True)
        actions_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Generate new key button
        gen_btn = CustomButton(
            actions_frame,
            text="🔑 Generate New License Key",
            command=self._generate_new_key,
            width=250,
            height=40,
            style="secondary"
        )
        gen_btn.pack(pady=5)
        
        # Validate license button
        validate_btn = CustomButton(
            actions_frame,
            text="✓ Validate License",
            command=self._validate_license,
            width=250,
            height=40,
            style="secondary"
        )
        validate_btn.pack(pady=5)
        
        # Refresh button
        refresh_btn = CustomButton(
            actions_frame,
            text="🔄 Refresh License Info",
            command=self._refresh_info,
            width=250,
            height=40,
            style="secondary"
        )
        refresh_btn.pack(pady=5)
    
    def _upgrade_license(self, tier):
        """Upgrade license to new tier"""
        from core.ui_components import MessageBox
        
        # Upgrade license (30 days for paid tiers, no expiry for basic)
        duration = None if tier == "basic" else 30
        success = self.license_system.upgrade_license(tier, duration)
        
        if success:
            MessageBox.show_success(
                self.winfo_toplevel(),
                "Upgrade Successful",
                f"License upgraded to {self.license_system.TIERS[tier]['name']}!"
            )
            self._refresh_info()
        else:
            MessageBox.show_error(
                self.winfo_toplevel(),
                "Upgrade Failed",
                "Failed to upgrade license. Please try again."
            )
    
    def _generate_new_key(self):
        """Generate new license key"""
        current_tier = self.license_system.get_license_info()['tier']
        key = self.license_system.generate_license(current_tier)
        
        # Show custom dialog with copy button
        self._show_license_key_dialog(key)
        
        self._refresh_info()
    
    def _show_license_key_dialog(self, key):
        """Show dialog with license key and copy button"""
        import customtkinter as ctk
        from core.ui_components import CustomFrame, CustomLabel, CustomButton
        
        # Create dialog
        dialog = ctk.CTkToplevel(self.winfo_toplevel())
        dialog.title("New License Key Generated")
        dialog.geometry("500x300")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"500x300+{x}+{y}")
        
        # Content
        content = CustomFrame(dialog, transparent=False)
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        CustomLabel(
            content,
            text="🔑 New License Key Generated",
            size=18,
            bold=True
        ).pack(pady=(0, 20))
        
        # Key display
        key_frame = CustomFrame(content, transparent=False)
        key_frame.pack(fill="x", pady=10)
        key_frame.configure(
            border_width=2,
            border_color=("#2d7a2d", "#2d7a2d"),
            corner_radius=8
        )
        
        CustomLabel(
            key_frame,
            text=key,
            size=16,
            bold=True,
            color=("#2d7a2d", "#2d7a2d")
        ).pack(pady=15)
        
        # Info text
        CustomLabel(
            content,
            text="Please save this key securely.\nYou can copy it to clipboard using the button below.",
            size=11,
            color=("#888888", "#888888")
        ).pack(pady=10)
        
        # Buttons
        btn_frame = CustomFrame(content, transparent=True)
        btn_frame.pack(pady=20)
        
        # Copy button
        copy_btn = CustomButton(
            btn_frame,
            text="📋 Copy to Clipboard",
            command=lambda: self._copy_key_and_close(key, dialog),
            width=180,
            height=40,
            style="primary"
        )
        copy_btn.pack(side="left", padx=5)
        
        # Close button
        close_btn = CustomButton(
            btn_frame,
            text="Close",
            command=dialog.destroy,
            width=100,
            height=40,
            style="secondary"
        )
        close_btn.pack(side="left", padx=5)
    
    def _copy_key_and_close(self, key, dialog):
        """Copy key to clipboard and close dialog"""
        try:
            self.winfo_toplevel().clipboard_clear()
            self.winfo_toplevel().clipboard_append(key)
            self.winfo_toplevel().update()
            
            info("LicenseManagement", f"License key copied: {key}")
            dialog.destroy()
            
            # Show brief notification
            from core.ui_components import MessageBox
            MessageBox.show_success(
                self.winfo_toplevel(),
                "Copied!",
                "License key copied to clipboard!"
            )
        except Exception as e:
            from core.ui_components import MessageBox
            MessageBox.show_error(
                self.winfo_toplevel(),
                "Copy Failed",
                f"Failed to copy: {e}"
            )
    
    def _validate_license(self):
        """Validate current license"""
        from core.ui_components import MessageBox
        
        is_valid, reason = self.license_system.validate_license()
        
        if is_valid:
            MessageBox.show_success(
                self.winfo_toplevel(),
                "License Valid",
                f"Your license is valid!\n\n{reason}"
            )
        else:
            MessageBox.show_error(
                self.winfo_toplevel(),
                "License Invalid",
                f"License validation failed:\n\n{reason}"
            )
    
    def _refresh_info(self):
        """Refresh license information"""
        # Clear and recreate UI
        for widget in self.winfo_children():
            widget.destroy()
        
        self._create_ui()
        
        info("LicenseManagement", "License info refreshed")
    
    def _copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        from core.ui_components import MessageBox
        
        try:
            # Copy to clipboard
            self.winfo_toplevel().clipboard_clear()
            self.winfo_toplevel().clipboard_append(text)
            self.winfo_toplevel().update()
            
            # Show notification
            MessageBox.show_success(
                self.winfo_toplevel(),
                "Copied!",
                f"License key copied to clipboard:\n\n{text}"
            )
            
            info("LicenseManagement", f"License key copied to clipboard: {text}")
        except Exception as e:
            MessageBox.show_error(
                self.winfo_toplevel(),
                "Copy Failed",
                f"Failed to copy to clipboard: {e}"
            )
    
    def _create_applications_section(self, parent):
        """Create license applications section (SuperAdmin only)"""
        section = CustomFrame(parent, transparent=False)
        section.pack(fill="x", pady=10)
        section.configure(border_width=2, border_color=("#3a3a3a", "#3a3a3a"), corner_radius=10)
        
        # Section header
        header = CustomFrame(section, transparent=True)
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        CustomLabel(header, text="📋 License Applications (Admin)", size=18, bold=True).pack(anchor="w")
        
        # Divider
        ctk.CTkFrame(section, height=1, fg_color=("#3a3a3a", "#3a3a3a")).pack(fill="x", padx=20, pady=10)
        
        # Button to open applications management
        actions_frame = CustomFrame(section, transparent=True)
        actions_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        manage_btn = CustomButton(
            actions_frame,
            text="🔧 Manage License Applications",
            command=self._show_applications_management,
            width=250,
            height=40,
            style="primary"
        )
        manage_btn.pack(pady=5)
    
    def _show_applications_management(self):
        """Show applications management interface"""
        # Clear current content
        for widget in self.master.winfo_children():
            widget.destroy()
        
        # Show admin applications module
        from modules.admin_license_applications import AdminLicenseApplications
        from core.license_activation import LicenseActivation
        
        activation_system = LicenseActivation()
        
        app_module = AdminLicenseApplications(
            self.master,
            activation_system=activation_system,
            on_back=self._return_to_license_management
        )
        app_module.pack(fill="both", expand=True)
    
    def _return_to_license_management(self):
        """Return to license management"""
        # Clear and recreate
        for widget in self.master.winfo_children():
            widget.destroy()
        
        new_module = LicenseManagementModule(
            self.master,
            license_system=self.license_system,
            on_back=self.on_back,
            is_superadmin=self.is_superadmin
        )
        new_module.pack(fill="both", expand=True)


# Debug logging
debug("LicenseManagement", "License management module loaded")

"""
Permissions Viewer Module
UI för att visa och hantera team permissions
"""

import customtkinter as ctk
from typing import Callable, Optional, List, Dict
from core.debug_logger import debug, info, warning, error
from core.ui_components import (
    CustomButton, CustomLabel, CustomFrame, MessageBox
)
from core.team_permissions import TeamPermissions


class PermissionsViewerModule(ctk.CTkFrame):
    """Permissions viewer module"""
    
    ROLE_NAMES = {
        100: "Owner",
        75: "Admin",
        50: "Member",
        25: "Guest"
    }
    
    ROLE_COLORS = {
        100: "#F44336",  # Red
        75: "#FF9800",   # Orange
        50: "#2196F3",   # Blue
        25: "#9E9E9E"    # Gray
    }
    
    def __init__(
        self,
        master,
        team_id: str,
        team_name: str,
        current_user_role: int,
        on_back: Callable = None,
        **kwargs
    ):
        """
        Initialize permissions viewer
        
        Args:
            master: Parent widget
            team_id: Team ID
            team_name: Team name
            current_user_role: Current user's role level
            on_back: Callback for back button
        """
        debug("PermissionsViewer", f"Initializing permissions viewer for team: {team_name}")
        
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.team_id = team_id
        self.team_name = team_name
        self.current_user_role = current_user_role
        self.on_back = on_back
        
        self.permissions = TeamPermissions(team_id)
        self.members = []
        
        self._create_ui()
        self._load_members()
        
        info("PermissionsViewer", "Permissions viewer initialized")
    
    def _create_ui(self):
        """Create permissions viewer UI"""
        debug("PermissionsViewer", "Creating permissions viewer UI")
        
        # Header
        header = CustomFrame(self, transparent=True)
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        CustomLabel(
            header,
            text=f"🔐 Permissions - {self.team_name}",
            size=20,
            bold=True
        ).pack(side="left")
        
        if self.on_back:
            CustomButton(
                header,
                text="← Back",
                command=self.on_back,
                style="secondary",
                width=100
            ).pack(side="right")
        
        # Role legend
        legend_frame = CustomFrame(self, transparent=False)
        legend_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        legend_container = CustomFrame(legend_frame, transparent=True)
        legend_container.pack(fill="x", padx=15, pady=15)
        
        CustomLabel(
            legend_container,
            text="📊 Role Levels",
            size=14,
            bold=True
        ).pack(anchor="w", pady=(0, 10))
        
        roles_row = CustomFrame(legend_container, transparent=True)
        roles_row.pack(fill="x")
        
        for level, name in sorted(self.ROLE_NAMES.items(), reverse=True):
            role_frame = CustomFrame(roles_row, transparent=True)
            role_frame.pack(side="left", padx=(0, 20))
            
            color = self.ROLE_COLORS[level]
            CustomLabel(
                role_frame,
                text=f"● {name} ({level})",
                size=11,
                bold=True,
                color=(color, color)
            ).pack()
        
        # Permissions info
        info_frame = CustomFrame(self, transparent=False)
        info_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        info_container = CustomFrame(info_frame, transparent=True)
        info_container.pack(fill="x", padx=15, pady=15)
        
        CustomLabel(
            info_container,
            text="ℹ️ Permission System",
            size=14,
            bold=True
        ).pack(anchor="w", pady=(0, 10))
        
        permissions_text = """
        • Owner (100): Full control - Can delete team, manage all members
        • Admin (75): Can manage members, change settings, view audit logs
        • Member (50): Can chat, share files, create tasks/events
        • Guest (25): Read-only access - Can view but not modify
        
        Higher role levels can manage lower levels.
        """
        
        CustomLabel(
            info_container,
            text=permissions_text.strip(),
            size=11,
            color=("#666666", "#999999")
        ).pack(anchor="w")
        
        # Members list
        members_container = CustomFrame(self, transparent=False)
        members_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        CustomLabel(
            members_container,
            text="👥 Team Members & Roles",
            size=14,
            bold=True
        ).pack(padx=15, pady=(15, 10), anchor="w")
        
        # Scrollable frame for members
        self.members_scroll = ctk.CTkScrollableFrame(
            members_container,
            fg_color="transparent"
        )
        self.members_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        debug("PermissionsViewer", "Permissions viewer UI created")
    
    def _load_members(self):
        """Load and display team members"""
        debug("PermissionsViewer", "Loading team members")
        
        # Get all members with their roles
        self.members = self.permissions.get_all_user_roles()
        
        # Clear existing members
        for widget in self.members_scroll.winfo_children():
            widget.destroy()
        
        if not self.members:
            CustomLabel(
                self.members_scroll,
                text="👥 No members found",
                size=12,
                color=("#888888", "#888888")
            ).pack(pady=50)
            return
        
        # Sort by role level (highest first)
        self.members.sort(key=lambda m: m['role_level'], reverse=True)
        
        # Display members
        for member in self.members:
            self._create_member_card(member)
        
        info("PermissionsViewer", f"Loaded {len(self.members)} members")
    
    def _create_member_card(self, member: Dict):
        """Create member card widget"""
        # Member card
        card = CustomFrame(self.members_scroll, transparent=False)
        card.pack(fill="x", pady=5)
        
        content = CustomFrame(card, transparent=True)
        content.pack(fill="x", padx=15, pady=10)
        
        # Header row
        header_row = CustomFrame(content, transparent=True)
        header_row.pack(fill="x", pady=(0, 5))
        
        # Role indicator
        role_level = member['role_level']
        role_name = self.ROLE_NAMES.get(role_level, "Unknown")
        role_color = self.ROLE_COLORS.get(role_level, "#888888")
        
        role_label = CustomLabel(
            header_row,
            text=f"● {role_name}",
            size=12,
            bold=True,
            color=(role_color, role_color)
        )
        role_label.pack(side="left", padx=(0, 10))
        
        # User ID
        user_label = CustomLabel(
            header_row,
            text=f"User ID: {member['user_id']}",
            size=11,
            color=("#666666", "#999999")
        )
        user_label.pack(side="left")
        
        # Permissions list
        perms_frame = CustomFrame(content, transparent=True)
        perms_frame.pack(fill="x", pady=(5, 0))
        
        # Get permissions for this role
        can_do = []
        if role_level >= 100:
            can_do = ["Delete Team", "Manage All", "Full Access"]
        elif role_level >= 75:
            can_do = ["Manage Members", "Change Settings", "View Audit Logs"]
        elif role_level >= 50:
            can_do = ["Chat", "Share Files", "Create Tasks/Events"]
        else:
            can_do = ["Read-Only Access"]
        
        perms_text = "Can: " + ", ".join(can_do)
        CustomLabel(
            perms_frame,
            text=perms_text,
            size=10,
            color=("#666666", "#999999")
        ).pack(anchor="w")
        
        # Actions (only if current user can manage this member)
        if self.current_user_role > role_level:
            actions_row = CustomFrame(content, transparent=True)
            actions_row.pack(fill="x", pady=(10, 0))
            
            # Change role button
            CustomButton(
                actions_row,
                text="Change Role",
                command=lambda m=member: self._change_role(m),
                style="primary",
                width=120,
                height=30
            ).pack(side="left", padx=(0, 5))
            
            # Remove button
            CustomButton(
                actions_row,
                text="Remove",
                command=lambda m=member: self._remove_member(m),
                style="secondary",
                width=100,
                height=30
            ).pack(side="left")
    
    def _change_role(self, member: Dict):
        """Change member's role"""
        debug("PermissionsViewer", f"Changing role for user: {member['user_id']}")
        
        # Create dialog to select new role
        dialog = ctk.CTkToplevel(self)
        dialog.title("Change Role")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        CustomLabel(
            dialog,
            text=f"Select new role for User {member['user_id']}",
            size=14,
            bold=True
        ).pack(pady=20)
        
        # Role buttons
        for level, name in sorted(self.ROLE_NAMES.items(), reverse=True):
            if level < self.current_user_role:  # Can only assign lower roles
                color = self.ROLE_COLORS[level]
                btn = CustomButton(
                    dialog,
                    text=f"{name} ({level})",
                    command=lambda l=level: self._apply_role_change(member, l, dialog),
                    style="primary",
                    width=200,
                    height=40
                )
                btn.pack(pady=5)
        
        CustomButton(
            dialog,
            text="Cancel",
            command=dialog.destroy,
            style="secondary",
            width=200
        ).pack(pady=20)
    
    def _apply_role_change(self, member: Dict, new_level: int, dialog):
        """Apply role change"""
        user_id = member['user_id']
        
        success = self.permissions.set_user_role(user_id, new_level)
        
        if success:
            info("PermissionsViewer", f"Role changed for user {user_id} to {new_level}")
            MessageBox.show_success(self, "Success", f"Role updated to {self.ROLE_NAMES[new_level]}")
            dialog.destroy()
            self._load_members()
        else:
            error("PermissionsViewer", f"Failed to change role for user {user_id}")
            MessageBox.show_error(self, "Error", "Failed to update role")
    
    def _remove_member(self, member: Dict):
        """Remove member from team"""
        debug("PermissionsViewer", f"Removing user: {member['user_id']}")
        
        # Confirm removal
        MessageBox.show_info(
            self,
            "Remove Member",
            f"Remove User {member['user_id']} from team?\n\nThis action cannot be undone."
        )
        
        # Note: Actual removal would need to be implemented in TeamSystem
        warning("PermissionsViewer", "Member removal not yet implemented in TeamSystem")

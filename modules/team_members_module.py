"""
Team Members Module
Hantera team-medlemmar med invite via email, UID, och invite codes
"""

import customtkinter as ctk
from typing import Callable, Optional, List, Dict
import secrets
import string
from datetime import datetime, timedelta
from core.debug_logger import debug, info, warning, error
from core.ui_components import (
    CustomButton, CustomLabel, CustomFrame, MessageBox
)
from core.team_system import TeamSystem


class TeamMembersModule(ctk.CTkFrame):
    """Team members management module"""
    
    def __init__(
        self,
        master,
        team_id: str,
        team_name: str,
        current_user_id: str,
        team_system: TeamSystem,
        notification_system=None,
        sound_system=None,
        **kwargs
    ):
        """
        Initialize team members module
        
        Args:
            master: Parent widget
            team_id: Team ID
            team_name: Team name
            current_user_id: Current user ID
            team_system: Team system instance
            notification_system: Notification system
            sound_system: Sound system
        """
        debug("TeamMembersModule", f"Initializing members for team: {team_name}")
        
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.team_id = team_id
        self.team_name = team_name
        self.current_user_id = current_user_id
        self.team_system = team_system
        self.notification_system = notification_system
        self.sound_system = sound_system
        
        self.members = []
        self.invite_code = None
        
        self._create_ui()
        self._load_members()
        self._generate_invite_code()
        
        info("TeamMembersModule", "Team members module initialized")
    
    def _create_ui(self):
        """Create members UI"""
        debug("TeamMembersModule", "Creating members UI")
        
        # Invite section
        invite_frame = CustomFrame(self, transparent=False)
        invite_frame.pack(fill="x", pady=(0, 10))
        
        invite_container = CustomFrame(invite_frame, transparent=True)
        invite_container.pack(fill="x", padx=15, pady=15)
        
        CustomLabel(
            invite_container,
            text="➕ Invite Members",
            size=14,
            bold=True
        ).pack(anchor="w", pady=(0, 10))
        
        # Invite by Email
        email_row = CustomFrame(invite_container, transparent=True)
        email_row.pack(fill="x", pady=(0, 10))
        
        CustomLabel(
            email_row,
            text="📧 Email:",
            size=11
        ).pack(side="left", padx=(0, 10))
        
        self.email_entry = ctk.CTkEntry(
            email_row,
            placeholder_text="user@example.com",
            height=35,
            width=250
        )
        self.email_entry.pack(side="left", padx=(0, 10))
        
        CustomButton(
            email_row,
            text="Send Invite",
            command=self._invite_by_email,
            style="primary",
            width=120,
            height=35
        ).pack(side="left")
        
        # Invite by UID
        uid_row = CustomFrame(invite_container, transparent=True)
        uid_row.pack(fill="x", pady=(0, 10))
        
        CustomLabel(
            uid_row,
            text="🆔 UID:",
            size=11
        ).pack(side="left", padx=(0, 10))
        
        self.uid_entry = ctk.CTkEntry(
            uid_row,
            placeholder_text="User ID (e.g., 12345)",
            height=35,
            width=250
        )
        self.uid_entry.pack(side="left", padx=(0, 10))
        
        CustomButton(
            uid_row,
            text="Add Member",
            command=self._invite_by_uid,
            style="primary",
            width=120,
            height=35
        ).pack(side="left")
        
        # Invite Code section
        code_row = CustomFrame(invite_container, transparent=True)
        code_row.pack(fill="x", pady=(0, 5))
        
        CustomLabel(
            code_row,
            text="🔗 Invite Code:",
            size=11
        ).pack(side="left", padx=(0, 10))
        
        self.code_label = CustomLabel(
            code_row,
            text="Generating...",
            size=11,
            bold=True,
            color=("#2196F3", "#2196F3")
        )
        self.code_label.pack(side="left", padx=(0, 10))
        
        CustomButton(
            code_row,
            text="📋 Copy",
            command=self._copy_invite_code,
            style="secondary",
            width=80,
            height=30
        ).pack(side="left", padx=(0, 5))
        
        CustomButton(
            code_row,
            text="🔄 New",
            command=self._generate_invite_code,
            style="secondary",
            width=80,
            height=30
        ).pack(side="left")
        
        # Invite Link
        link_row = CustomFrame(invite_container, transparent=True)
        link_row.pack(fill="x")
        
        CustomLabel(
            link_row,
            text="Share this code or link with people you want to invite",
            size=9,
            color=("#666666", "#999999")
        ).pack(anchor="w")
        
        # Members list
        members_frame = CustomFrame(self, transparent=False)
        members_frame.pack(fill="both", expand=True)
        
        CustomLabel(
            members_frame,
            text="👥 Team Members",
            size=14,
            bold=True
        ).pack(padx=15, pady=(15, 10), anchor="w")
        
        # Fixed frame for members (no scrollbar)
        self.members_scroll = CustomFrame(members_frame, transparent=True)
        self.members_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        debug("TeamMembersModule", "Members UI created")
    
    def _load_members(self):
        """Load and display team members"""
        debug("TeamMembersModule", "Loading members")
        
        try:
            self.members = self.team_system.get_team_members(self.team_id)
            
            # Clear existing members
            for widget in self.members_scroll.winfo_children():
                widget.destroy()
            
            if not self.members:
                CustomLabel(
                    self.members_scroll,
                    text="👥 No members yet. Invite people to join!",
                    size=12,
                    color=("#888888", "#888888")
                ).pack(pady=50)
                return
            
            # Display members
            for member in self.members:
                self._create_member_card(member)
            
            info("TeamMembersModule", f"Loaded {len(self.members)} members")
            
        except Exception as e:
            error("TeamMembersModule", f"Error loading members: {e}")
    
    def _create_member_card(self, member: Dict):
        """Create member card widget"""
        # Member card
        card = CustomFrame(self.members_scroll, transparent=False)
        card.pack(fill="x", pady=5)
        
        content = CustomFrame(card, transparent=True)
        content.pack(fill="x", padx=15, pady=10)
        
        # Left side - User info
        left_side = CustomFrame(content, transparent=True)
        left_side.pack(side="left", fill="x", expand=True)
        
        # User name with UID
        user_id = member.get('user_id', 'Unknown')
        name_label = CustomLabel(
            left_side,
            text=f"👤 User {user_id} (UID: {user_id})",
            size=12,
            bold=True
        )
        name_label.pack(anchor="w")
        
        # Role
        role = member.get('role', 50)
        role_name = self._get_role_name(role)
        role_color = self._get_role_color(role)
        
        role_label = CustomLabel(
            left_side,
            text=f"🎭 {role_name}",
            size=10,
            color=(role_color, role_color)
        )
        role_label.pack(anchor="w", pady=(2, 0))
        
        # Joined date
        try:
            joined = datetime.fromisoformat(member.get('joined_at', ''))
            joined_str = joined.strftime("%Y-%m-%d")
        except:
            joined_str = "Unknown"
        
        CustomLabel(
            left_side,
            text=f"📅 Joined: {joined_str}",
            size=9,
            color=("#666666", "#999999")
        ).pack(anchor="w", pady=(2, 0))
        
        # Right side - Actions
        if user_id != self.current_user_id:
            actions = CustomFrame(content, transparent=True)
            actions.pack(side="right")
            
            # Remove button (only for admins/owners)
            CustomButton(
                actions,
                text="🗑️ Remove",
                command=lambda m=member: self._remove_member(m),
                style="secondary",
                width=100,
                height=30
            ).pack()
    
    def _get_role_name(self, role: int) -> str:
        """Get role name from role level"""
        # Convert to int if string
        try:
            role = int(role)
        except (ValueError, TypeError):
            role = 50  # Default to Member
        
        if role >= 100:
            return "Owner"
        elif role >= 75:
            return "Admin"
        elif role >= 50:
            return "Member"
        else:
            return "Guest"
    
    def _get_role_color(self, role: int) -> str:
        """Get role color from role level"""
        # Convert to int if string
        try:
            role = int(role)
        except (ValueError, TypeError):
            role = 50  # Default to Member
        
        if role >= 100:
            return "#F44336"  # Red
        elif role >= 75:
            return "#FF9800"  # Orange
        elif role >= 50:
            return "#2196F3"  # Blue
        else:
            return "#9E9E9E"  # Gray
    
    def _generate_invite_code(self):
        """Generate new invite code"""
        debug("TeamMembersModule", "Generating invite code")
        
        # Generate random 8-character code
        chars = string.ascii_uppercase + string.digits
        self.invite_code = ''.join(secrets.choice(chars) for _ in range(8))
        
        # Format as XXXX-XXXX
        formatted_code = f"{self.invite_code[:4]}-{self.invite_code[4:]}"
        
        self.code_label.configure(text=formatted_code)
        
        info("TeamMembersModule", f"Generated invite code: {formatted_code}")
        
        # Show notification
        if self.notification_system:
            self.notification_system.show_success(
                "New invite code generated!",
                duration=2000
            )
    
    def _copy_invite_code(self):
        """Copy invite code to clipboard"""
        debug("TeamMembersModule", "Copying invite code")
        
        if not self.invite_code:
            return
        
        formatted_code = f"{self.invite_code[:4]}-{self.invite_code[4:]}"
        
        # Copy to clipboard
        self.clipboard_clear()
        self.clipboard_append(formatted_code)
        
        info("TeamMembersModule", "Invite code copied to clipboard")
        
        MessageBox.show_success(
            self,
            "Copied!",
            f"Invite code '{formatted_code}' copied to clipboard!"
        )
        
        if self.sound_system:
            self.sound_system.play_sound('success')
    
    def _invite_by_email(self):
        """Invite member by email"""
        debug("TeamMembersModule", "Inviting by email")
        
        email = self.email_entry.get().strip()
        
        if not email:
            MessageBox.show_error(self, "Error", "Please enter an email address")
            return
        
        # TODO: Implement email sending via mail server
        info("TeamMembersModule", f"Sending invite to: {email}")
        
        MessageBox.show_info(
            self,
            "Invite Sent",
            f"Invitation email will be sent to:\n{email}\n\n(Email server integration pending)"
        )
        
        self.email_entry.delete(0, "end")
        
        if self.notification_system:
            self.notification_system.show_success(
                f"Invite sent to {email}",
                duration=3000
            )
    
    def _invite_by_uid(self):
        """Invite member by UID"""
        debug("TeamMembersModule", "Inviting by UID")
        
        uid = self.uid_entry.get().strip()
        
        if not uid:
            MessageBox.show_error(self, "Error", "Please enter a User ID")
            return
        
        try:
            # Add member to team
            success = self.team_system.add_member(
                self.team_id,
                uid,
                role=50  # Default member role
            )
            
            if success:
                info("TeamMembersModule", f"Added member: {uid}")
                
                MessageBox.show_success(
                    self,
                    "Member Added",
                    f"User {uid} has been added to the team!"
                )
                
                self.uid_entry.delete(0, "end")
                
                if self.notification_system:
                    self.notification_system.show_success(
                        f"User {uid} added to team",
                        duration=3000
                    )
                
                if self.sound_system:
                    self.sound_system.play_sound('success')
                
                # Reload members
                self._load_members()
            else:
                error("TeamMembersModule", "Failed to add member")
                MessageBox.show_error(self, "Error", "Failed to add member")
                
        except Exception as e:
            error("TeamMembersModule", f"Error adding member: {e}")
            MessageBox.show_error(self, "Error", f"Error: {str(e)}")
    
    def _remove_member(self, member: Dict):
        """Remove member from team"""
        debug("TeamMembersModule", f"Removing member: {member.get('user_id')}")
        
        def on_confirm():
            try:
                success = self.team_system.remove_member(
                    self.team_id,
                    member.get('user_id')
                )
                
                if success:
                    info("TeamMembersModule", f"Removed member: {member.get('user_id')}")
                    
                    MessageBox.show_success(
                        self,
                        "Member Removed",
                        f"User {member.get('user_id')} has been removed from the team"
                    )
                    
                    if self.notification_system:
                        self.notification_system.show_info(
                            f"User {member.get('user_id')} removed",
                            duration=3000
                        )
                    
                    # Reload members
                    self._load_members()
                else:
                    error("TeamMembersModule", "Failed to remove member")
                    MessageBox.show_error(self, "Error", "Failed to remove member")
                    
            except Exception as e:
                error("TeamMembersModule", f"Error removing member: {e}")
                MessageBox.show_error(self, "Error", f"Error: {str(e)}")
        
        MessageBox.show_confirm(
            self,
            "Remove Member",
            f"Are you sure you want to remove User {member.get('user_id')} from the team?",
            on_confirm
        )

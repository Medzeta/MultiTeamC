"""
Teams Module
Hantera teams, skapa nya, bjud in medlemmar och visa team-data
"""

import customtkinter as ctk
from typing import Callable, Optional, List, Dict
from core.debug_logger import debug, info, warning, error
from core.ui_components import (
    CustomButton, CustomLabel, CustomFrame, CustomEntry, MessageBox
)
from modules.team_chat_module import TeamChatModule


class TeamsModule(ctk.CTkFrame):
    """Teams management module"""
    
    def __init__(
        self,
        master,
        team_system,
        p2p_system,
        file_transfer,
        user_info: dict,
        on_back: Callable = None,
        on_open_team: Callable = None,
        **kwargs
    ):
        """
        Initialize teams module
        
        Args:
            master: Parent widget
            team_system: TeamSystem instance
            p2p_system: P2PSystem instance
            file_transfer: FileTransfer instance
            user_info: Current user information
            on_back: Callback for back button
            on_open_team: Callback for opening team details
        """
        debug("TeamsModule", "Initializing teams module")
        
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.team_system = team_system
        self.p2p_system = p2p_system
        self.file_transfer = file_transfer
        self.user_info = user_info
        self.on_back = on_back
        self.on_open_team = on_open_team
        self.current_team = None
        
        self._create_ui()
        self._refresh_teams()
        
        info("TeamsModule", "Teams module initialized")
    
    def _create_ui(self):
        """Create teams UI"""
        debug("TeamsModule", "Creating teams UI")
        
        # Main container with two columns
        main_container = CustomFrame(self, transparent=True)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left column - Teams list
        left_column = CustomFrame(main_container, transparent=False)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Header
        header_frame = CustomFrame(left_column, transparent=True)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Back button (if callback provided)
        if self.on_back:
            CustomButton(
                header_frame,
                text="← Back",
                command=self.on_back,
                width=100,
                height=35,
                style="secondary"
            ).pack(side="left", padx=(0, 15))
        
        CustomLabel(
            header_frame,
            text="👥 My Teams",
            size=18,
            bold=True
        ).pack(side="left")
        
        CustomButton(
            header_frame,
            text="+ Create Team",
            command=self._show_create_team_dialog,
            width=140,
            height=35,
            style="success"
        ).pack(side="right")
        
        # Teams list
        self.teams_container = ctk.CTkScrollableFrame(
            left_column,
            fg_color="transparent",
            scrollbar_fg_color=("#2b2b2b", "#2b2b2b"),
            scrollbar_button_color=("#3b3b3b", "#3b3b3b"),
            scrollbar_button_hover_color=("#4b4b4b", "#4b4b4b")
        )
        self.teams_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Right column - Team details
        self.right_column = CustomFrame(main_container, transparent=False)
        self.right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Placeholder
        self.details_container = CustomFrame(self.right_column, transparent=True)
        self.details_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        CustomLabel(
            self.details_container,
            text="Select a team to view details",
            size=14,
            color=("#999999", "#999999")
        ).pack(expand=True)
        
        debug("TeamsModule", "Teams UI created")
    
    def _refresh_teams(self):
        """Refresh teams list"""
        debug("TeamsModule", "Refreshing teams list")
        
        # Clear existing
        for widget in self.teams_container.winfo_children():
            widget.destroy()
        
        # Get teams
        teams = self.team_system.get_my_teams()
        
        if not teams:
            # No teams
            no_teams_frame = CustomFrame(self.teams_container, transparent=False)
            no_teams_frame.pack(fill="x", pady=10)
            
            CustomLabel(
                no_teams_frame,
                text="No teams yet",
                size=12,
                color=("#999999", "#999999")
            ).pack(pady=20)
            
            CustomLabel(
                no_teams_frame,
                text="Create your first team to get started!",
                size=10,
                color=("#666666", "#666666")
            ).pack(pady=(0, 20))
            
            return
        
        # Show teams
        for team in teams:
            self._create_team_widget(team)
        
        info("TeamsModule", f"Displayed {len(teams)} teams")
    
    def _create_team_widget(self, team: dict):
        """Create widget for a team"""
        team_frame = CustomFrame(self.teams_container, transparent=False)
        team_frame.pack(fill="x", pady=5)
        
        # Make clickable
        team_frame.bind("<Button-1>", lambda e: self._show_team_details(team))
        
        content = CustomFrame(team_frame, transparent=True)
        content.pack(fill="x", padx=15, pady=12)
        content.bind("<Button-1>", lambda e: self._show_team_details(team))
        
        # Team name
        name_label = CustomLabel(
            content,
            text=team['name'],
            size=14,
            bold=True
        )
        name_label.pack(anchor="w")
        name_label.bind("<Button-1>", lambda e: self._show_team_details(team))
        
        # Role badge
        role_color = {
            'owner': ("#107c10", "#0d5e0d"),
            'admin': ("#1f6aa5", "#144870"),
            'member': ("#999999", "#666666")
        }.get(team['role'], ("#999999", "#666666"))
        
        role_label = CustomLabel(
            content,
            text=f"🏷️ {team['role'].title()}",
            size=10,
            color=role_color
        )
        role_label.pack(anchor="w", pady=(3, 0))
        role_label.bind("<Button-1>", lambda e: self._show_team_details(team))
    
    def _show_team_details(self, team: dict):
        """Show team details in right column"""
        info("TeamsModule", f"Showing details for team: {team['name']}")
        
        self.current_team = team
        
        # Clear details container
        for widget in self.details_container.winfo_children():
            widget.destroy()
        
        # Team header
        header = CustomFrame(self.details_container, transparent=True)
        header.pack(fill="x", pady=(0, 15))
        
        CustomLabel(
            header,
            text=team['name'],
            size=18,
            bold=True
        ).pack(anchor="w")
        
        if team.get('description'):
            CustomLabel(
                header,
                text=team['description'],
                size=11,
                color=("#999999", "#999999")
            ).pack(anchor="w", pady=(5, 0))
        
        # Divider
        ctk.CTkFrame(
            self.details_container,
            height=1,
            fg_color=("#3a3a3a", "#3a3a3a")
        ).pack(fill="x", pady=15)
        
        # Members section
        members_header = CustomFrame(self.details_container, transparent=True)
        members_header.pack(fill="x", pady=(0, 10))
        
        CustomLabel(
            members_header,
            text="👤 Members",
            size=14,
            bold=True
        ).pack(side="left")
        
        # Open Team button (integrated view)
        CustomButton(
            members_header,
            text="📂 Open Team",
            command=lambda: self._open_team_details(team),
            width=130,
            height=30,
            style="primary"
        ).pack(side="right", padx=(0, 5))
        
        # Open Chat button
        CustomButton(
            members_header,
            text="💬 Chat",
            command=lambda: self._open_team_chat(team),
            width=100,
            height=30,
            style="secondary"
        ).pack(side="right", padx=(0, 10))
        
        # Invite button (only for owner/admin)
        if team['role'] in ['owner', 'admin']:
            CustomButton(
                members_header,
                text="+ Invite",
                command=lambda: self._show_invite_dialog(team),
                width=100,
                height=30,
                style="success"
            ).pack(side="right")
        
        # Members list
        members = self.team_system.get_team_members(team['team_id'])
        
        members_container = ctk.CTkScrollableFrame(
            self.details_container,
            fg_color="transparent",
            height=200,
            scrollbar_fg_color=("#2b2b2b", "#2b2b2b"),
            scrollbar_button_color=("#3b3b3b", "#3b3b3b"),
            scrollbar_button_hover_color=("#4b4b4b", "#4b4b4b")
        )
        members_container.pack(fill="both", expand=True, pady=(0, 15))
        
        for member in members:
            self._create_member_widget(members_container, member)
        
        # Actions
        actions_frame = CustomFrame(self.details_container, transparent=True)
        actions_frame.pack(fill="x", pady=(10, 0))
        
        # Leave team button (not for owners)
        if team['role'] != 'owner':
            CustomButton(
                actions_frame,
                text="Leave Team",
                command=lambda: self._leave_team(team),
                width=120,
                height=35,
                style="secondary"
            ).pack(side="left")
    
    def _create_member_widget(self, container, member: dict):
        """Create widget for a team member"""
        member_frame = CustomFrame(container, transparent=False)
        member_frame.pack(fill="x", pady=3)
        
        content = CustomFrame(member_frame, transparent=True)
        content.pack(fill="x", padx=12, pady=8)
        
        # User ID (would be name in real app)
        CustomLabel(
            content,
            text=f"User #{member['user_id']}",
            size=11
        ).pack(side="left")
        
        # Role
        role_color = {
            'owner': ("#107c10", "#0d5e0d"),
            'admin': ("#1f6aa5", "#144870"),
            'member': ("#999999", "#666666")
        }.get(member['role'], ("#999999", "#666666"))
        
        CustomLabel(
            content,
            text=member['role'].title(),
            size=10,
            color=role_color
        ).pack(side="right")
    
    def _show_create_team_dialog(self):
        """Show create team dialog"""
        debug("TeamsModule", "Showing create team dialog")
        
        # Create dialog with dark theme
        dialog = ctk.CTkToplevel(self)
        dialog.title("Create Team")
        dialog.geometry("500x350")
        dialog.transient(self.master)
        dialog.grab_set()
        
        # Set dark theme colors
        dialog.configure(fg_color=("#2b2b2b", "#2b2b2b"))
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (350 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Content
        content = CustomFrame(dialog, transparent=True)
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        CustomLabel(
            content,
            text="Create New Team",
            size=18,
            bold=True
        ).pack(pady=(0, 20))
        
        # Team name
        CustomLabel(content, text="Team Name", size=12).pack(anchor="w", pady=(0, 5))
        name_entry = CustomEntry(content, placeholder="Enter team name")
        name_entry.pack(fill="x", pady=(0, 15))
        name_entry.focus()
        
        # Description
        CustomLabel(content, text="Description (optional)", size=12).pack(anchor="w", pady=(0, 5))
        desc_entry = CustomEntry(content, placeholder="Enter description")
        desc_entry.pack(fill="x", pady=(0, 25))
        
        # Buttons
        button_frame = CustomFrame(content, transparent=True)
        button_frame.pack(fill="x")
        
        def create():
            name = name_entry.get().strip()
            if not name:
                MessageBox.show_error(dialog, "Error", "Please enter a team name")
                return
            
            desc = desc_entry.get().strip()
            team_id = self.team_system.create_team(name, desc)
            
            if team_id:
                dialog.destroy()  # Stäng dialogen först
                self._refresh_teams()  # Sedan uppdatera listan
                MessageBox.show_success(self.master, "Success", f"Team '{name}' created!")
            else:
                MessageBox.show_error(dialog, "Error", "Failed to create team")
        
        CustomButton(
            button_frame,
            text="Create",
            command=create,
            width=150,
            height=40,
            style="success"
        ).pack(side="left", padx=(0, 10))
        
        CustomButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            width=150,
            height=40,
            style="secondary"
        ).pack(side="left")
        
        # Enter key binding
        name_entry.bind("<Return>", lambda e: create())
        desc_entry.bind("<Return>", lambda e: create())
    
    def _show_invite_dialog(self, team: dict):
        """Show invite peer dialog"""
        debug("TeamsModule", f"Showing invite dialog for team: {team['name']}")
        
        # Get connected peers
        peers = self.p2p_system.get_connected_peers()
        
        if not peers:
            MessageBox.show_info(
                self.master,
                "No Peers",
                "No connected peers available.\n\nConnect to peers first in the Network Peers section."
            )
            return
        
        # Create dialog with dark theme
        dialog = ctk.CTkToplevel(self)
        dialog.title("Invite to Team")
        dialog.geometry("500x400")
        dialog.transient(self.master)
        dialog.grab_set()
        
        # Set dark theme colors
        dialog.configure(fg_color=("#2b2b2b", "#2b2b2b"))
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Content
        content = CustomFrame(dialog, transparent=True)
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        CustomLabel(
            content,
            text=f"Invite to '{team['name']}'",
            size=16,
            bold=True
        ).pack(pady=(0, 20))
        
        CustomLabel(
            content,
            text="Select a peer to invite:",
            size=12
        ).pack(anchor="w", pady=(0, 10))
        
        # Peers list
        peers_container = ctk.CTkScrollableFrame(
            content,
            fg_color="transparent",
            scrollbar_fg_color=("#2b2b2b", "#2b2b2b"),
            scrollbar_button_color=("#3b3b3b", "#3b3b3b"),
            scrollbar_button_hover_color=("#4b4b4b", "#4b4b4b")
        )
        peers_container.pack(fill="both", expand=True, pady=(0, 20))
        
        selected_peer = {"peer_id": None}
        
        for peer in peers:
            peer_frame = CustomFrame(peers_container, transparent=False)
            peer_frame.pack(fill="x", pady=3)
            
            def select_peer(p=peer):
                selected_peer["peer_id"] = p['id']
                # Update selection visual (simplified)
                for child in peers_container.winfo_children():
                    child.configure(border_width=0)
                peer_frame.configure(border_width=2, border_color=("#1f6aa5", "#144870"))
            
            peer_frame.bind("<Button-1>", lambda e, p=peer: select_peer(p))
            
            peer_content = CustomFrame(peer_frame, transparent=True)
            peer_content.pack(fill="x", padx=12, pady=10)
            peer_content.bind("<Button-1>", lambda e, p=peer: select_peer(p))
            
            peer_label = CustomLabel(
                peer_content,
                text=f"🖥️ {peer['id'][:16]}...",
                size=11
            )
            peer_label.pack(side="left")
            peer_label.bind("<Button-1>", lambda e, p=peer: select_peer(p))
            
            ip_label = CustomLabel(
                peer_content,
                text=f"{peer['ip']}",
                size=10,
                color=("#999999", "#999999")
            )
            ip_label.pack(side="right")
            ip_label.bind("<Button-1>", lambda e, p=peer: select_peer(p))
        
        # Buttons
        button_frame = CustomFrame(content, transparent=True)
        button_frame.pack(fill="x")
        
        def invite():
            if not selected_peer["peer_id"]:
                MessageBox.show_error(dialog, "Error", "Please select a peer")
                return
            
            success = self.team_system.invite_peer_to_team(team['team_id'], selected_peer["peer_id"])
            
            if success:
                MessageBox.show_success(dialog, "Success", "Invitation sent!")
                dialog.destroy()
            else:
                MessageBox.show_error(dialog, "Error", "Failed to send invitation")
        
        CustomButton(
            button_frame,
            text="Send Invitation",
            command=invite,
            width=150,
            height=40,
            style="success"
        ).pack(side="left", padx=(0, 10))
        
        CustomButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            width=150,
            height=40,
            style="secondary"
        ).pack(side="left")
    
    def _open_team_details(self, team: dict):
        """Open integrated team details view"""
        info("TeamsModule", f"Opening team details for: {team['name']}")
        
        if self.on_open_team:
            self.on_open_team(team)
    
    def _open_team_chat(self, team: dict):
        """Open team chat"""
        info("TeamsModule", f"Opening chat for team: {team['name']}")
        
        # Clear main container
        for widget in self.winfo_children():
            widget.destroy()
        
        # Create chat module
        chat_module = TeamChatModule(
            self,
            team_system=self.team_system,
            p2p_system=self.p2p_system,
            file_transfer=self.file_transfer,
            team_info=team,
            user_info=self.user_info,
            on_back=self._close_chat
        )
        chat_module.pack(fill="both", expand=True)
        
        self.current_chat = chat_module
        debug("TeamsModule", "Chat opened")
    
    def _close_chat(self):
        """Close chat and return to teams view"""
        info("TeamsModule", "Closing chat")
        
        if hasattr(self, 'current_chat'):
            self.current_chat.cleanup()
            delattr(self, 'current_chat')
        
        # Recreate teams UI
        for widget in self.winfo_children():
            widget.destroy()
        
        self._create_ui()
        self._refresh_teams()
        
        debug("TeamsModule", "Returned to teams view")
    
    def _leave_team(self, team: dict):
        """Leave a team"""
        info("TeamsModule", f"Leaving team: {team['name']}")
        
        # Confirm
        result = MessageBox.show_question(
            self.master,
            "Leave Team",
            f"Are you sure you want to leave '{team['name']}'?"
        )
        
        if result:
            success = self.team_system.leave_team(team['team_id'])
            
            if success:
                MessageBox.show_success(self.master, "Success", "Left team successfully")
                self.current_team = None
                self._refresh_teams()
                
                # Clear details
                for widget in self.details_container.winfo_children():
                    widget.destroy()
                
                CustomLabel(
                    self.details_container,
                    text="Select a team to view details",
                    size=14,
                    color=("#999999", "#999999")
                ).pack(expand=True)
            else:
                MessageBox.show_error(self.master, "Error", "Failed to leave team")


if __name__ == "__main__":
    # Test teams module
    info("TEST", "Testing TeamsModule...")
    
    from core.custom_window import CustomWindow
    from core.p2p_system import P2PSystem
    from core.team_system import TeamSystem
    
    # Create window
    app = CustomWindow(title="Teams Test", width=1000, height=700)
    
    # Create systems
    p2p = P2PSystem()
    team_sys = TeamSystem(user_id=1, p2p_system=p2p)
    
    # Create teams module
    user_info = {
        'id': 1,
        'name': 'Test User',
        'email': 'test@example.com'
    }
    
    teams_module = TeamsModule(
        app.content_frame,
        team_system=team_sys,
        p2p_system=p2p,
        user_info=user_info
    )
    teams_module.pack(fill="both", expand=True)
    
    info("TEST", "Starting mainloop...")
    app.mainloop()

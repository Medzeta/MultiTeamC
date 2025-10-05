"""
Team Details Module
Integrerad vy för team med Tasks, Calendar, Files och Members
"""

import customtkinter as ctk
from typing import Callable, Optional, Dict
from core.debug_logger import debug, info, warning, error
from core.ui_components import (
    CustomButton, CustomLabel, CustomFrame, MessageBox
)
from core.team_system import TeamSystem


class TeamDetailsModule(ctk.CTkFrame):
    """Team details module med integrerade features"""
    
    def __init__(
        self,
        master,
        team_id: str,
        team_name: str,
        current_user_id: str,
        team_system: TeamSystem,
        notification_system=None,
        sound_system=None,
        on_back: Callable = None,
        **kwargs
    ):
        """
        Initialize team details module
        
        Args:
            master: Parent widget
            team_id: Team ID
            team_name: Team name
            current_user_id: Current user ID
            team_system: Team system instance
            notification_system: Notification system
            sound_system: Sound system
            on_back: Callback for back button
        """
        debug("TeamDetailsModule", f"Initializing team details for: {team_name}")
        
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.team_id = team_id
        self.team_name = team_name
        self.current_user_id = current_user_id
        self.team_system = team_system
        self.notification_system = notification_system
        self.sound_system = sound_system
        self.on_back = on_back
        
        self.current_tab = "members"
        self.current_module = None
        
        self._create_ui()
        
        info("TeamDetailsModule", "Team details module initialized")
    
    def _create_ui(self):
        """Create team details UI"""
        debug("TeamDetailsModule", "Creating team details UI")
        
        # Header
        header = CustomFrame(self, transparent=True)
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        CustomLabel(
            header,
            text=f"👥 {self.team_name}",
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
        
        # Tab buttons
        tabs_frame = CustomFrame(self, transparent=False)
        tabs_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        tabs_container = CustomFrame(tabs_frame, transparent=True)
        tabs_container.pack(fill="x", padx=15, pady=15)
        
        # Members tab
        self.members_btn = CustomButton(
            tabs_container,
            text="👥 Members",
            command=lambda: self._switch_tab("members"),
            width=150,
            height=40,
            style="primary"
        )
        self.members_btn.pack(side="left", padx=(0, 5))
        
        # Tasks tab
        self.tasks_btn = CustomButton(
            tabs_container,
            text="✅ Tasks",
            command=lambda: self._switch_tab("tasks"),
            width=150,
            height=40,
            style="secondary"
        )
        self.tasks_btn.pack(side="left", padx=(0, 5))
        
        # Calendar tab
        self.calendar_btn = CustomButton(
            tabs_container,
            text="📅 Calendar",
            command=lambda: self._switch_tab("calendar"),
            width=150,
            height=40,
            style="secondary"
        )
        self.calendar_btn.pack(side="left", padx=(0, 5))
        
        # Files tab
        self.files_btn = CustomButton(
            tabs_container,
            text="📁 Files",
            command=lambda: self._switch_tab("files"),
            width=150,
            height=40,
            style="secondary"
        )
        self.files_btn.pack(side="left", padx=(0, 5))
        
        # Content area
        self.content_frame = CustomFrame(self, transparent=True)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Show members by default
        self._switch_tab("members")
        
        debug("TeamDetailsModule", "Team details UI created")
    
    def _switch_tab(self, tab_name: str):
        """Switch to different tab"""
        debug("TeamDetailsModule", f"Switching to tab: {tab_name}")
        
        # Update button colors to show active tab
        primary_color = ("#1f6aa5", "#1f6aa5")
        secondary_color = ("#3b3b3b", "#3b3b3b")
        
        self.members_btn.configure(fg_color=primary_color if tab_name == "members" else secondary_color)
        self.tasks_btn.configure(fg_color=primary_color if tab_name == "tasks" else secondary_color)
        self.calendar_btn.configure(fg_color=primary_color if tab_name == "calendar" else secondary_color)
        self.files_btn.configure(fg_color=primary_color if tab_name == "files" else secondary_color)
        
        # Clear current content
        if self.current_module:
            self.current_module.destroy()
            self.current_module = None
        
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.current_tab = tab_name
        
        # Load appropriate module
        if tab_name == "members":
            self._show_members()
        elif tab_name == "tasks":
            self._show_tasks()
        elif tab_name == "calendar":
            self._show_calendar()
        elif tab_name == "files":
            self._show_files()
    
    def _show_members(self):
        """Show members management"""
        debug("TeamDetailsModule", "Showing members")
        
        from modules.team_members_module import TeamMembersModule
        
        self.current_module = TeamMembersModule(
            self.content_frame,
            team_id=self.team_id,
            team_name=self.team_name,
            current_user_id=self.current_user_id,
            team_system=self.team_system,
            notification_system=self.notification_system,
            sound_system=self.sound_system
        )
        self.current_module.pack(fill="both", expand=True)
    
    def _show_tasks(self):
        """Show task manager"""
        debug("TeamDetailsModule", "Showing tasks")
        
        from modules.task_manager_module import TaskManagerModule
        
        self.current_module = TaskManagerModule(
            self.content_frame,
            team_id=self.team_id,
            team_name=self.team_name,
            current_user_id=self.current_user_id,
            on_back=None  # No back button in tab view
        )
        self.current_module.pack(fill="both", expand=True)
    
    def _show_calendar(self):
        """Show calendar"""
        debug("TeamDetailsModule", "Showing calendar")
        
        from modules.calendar_module import CalendarModule
        
        self.current_module = CalendarModule(
            self.content_frame,
            team_id=self.team_id,
            team_name=self.team_name,
            current_user_id=self.current_user_id,
            on_back=None  # No back button in tab view
        )
        self.current_module.pack(fill="both", expand=True)
    
    def _show_files(self):
        """Show file server"""
        debug("TeamDetailsModule", "Showing files")
        
        from modules.fileserver_module import FileServerModule
        
        self.current_module = FileServerModule(
            self.content_frame,
            team_id=self.team_id,
            team_name=self.team_name,
            current_user_id=self.current_user_id,
            notification_system=self.notification_system,
            sound_system=self.sound_system,
            on_back=None  # No back button in tab view
        )
        self.current_module.pack(fill="both", expand=True)

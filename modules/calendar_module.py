"""
Calendar Module
UI för team kalender med events
"""

import customtkinter as ctk
from typing import Callable, Optional, List, Dict
from datetime import datetime, timedelta
from core.debug_logger import debug, info, warning, error
from core.ui_components import (
    CustomButton, CustomLabel, CustomFrame, CustomEntry, MessageBox
)
from core.team_calendar import TeamCalendar


class CalendarModule(ctk.CTkFrame):
    """Calendar module för teams"""
    
    def __init__(
        self,
        master,
        team_id: str,
        team_name: str,
        current_user_id: str,
        on_back: Callable = None,
        **kwargs
    ):
        """
        Initialize calendar module
        
        Args:
            master: Parent widget
            team_id: Team ID
            team_name: Team name
            current_user_id: Current user ID
            on_back: Callback for back button
        """
        debug("CalendarModule", f"Initializing calendar for team: {team_name}")
        
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.team_id = team_id
        self.team_name = team_name
        self.current_user_id = current_user_id
        self.on_back = on_back
        
        self.calendar = TeamCalendar(team_id)
        self.current_date = datetime.now()
        self.events = []
        
        self._create_ui()
        
        # Load events after UI is ready
        self.after(100, self._load_events)
        
        info("CalendarModule", "Calendar module initialized")
    
    def _create_ui(self):
        """Create calendar UI"""
        debug("CalendarModule", "Creating calendar UI")
        
        # Header
        header = CustomFrame(self, transparent=True)
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        CustomLabel(
            header,
            text=f"📅 Calendar - {self.team_name}",
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
        
        # Month navigation
        nav_frame = CustomFrame(self, transparent=True)
        nav_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        CustomButton(
            nav_frame,
            text="◀",
            command=self._previous_month,
            style="secondary",
            width=50
        ).pack(side="left", padx=(0, 10))
        
        self.month_label = CustomLabel(
            nav_frame,
            text=self.current_date.strftime("%B %Y"),
            size=16,
            bold=True
        )
        self.month_label.pack(side="left", expand=True)
        
        CustomButton(
            nav_frame,
            text="▶",
            command=self._next_month,
            style="secondary",
            width=50
        ).pack(side="left", padx=(10, 0))
        
        CustomButton(
            nav_frame,
            text="Today",
            command=self._go_to_today,
            style="primary",
            width=80
        ).pack(side="right", padx=(10, 0))
        
        # Add event section
        add_frame = CustomFrame(self, transparent=False)
        add_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        add_container = CustomFrame(add_frame, transparent=True)
        add_container.pack(fill="x", padx=15, pady=15)
        
        CustomLabel(
            add_container,
            text="➕ New Event",
            size=14,
            bold=True
        ).pack(anchor="w", pady=(0, 10))
        
        # Event input
        input_row1 = CustomFrame(add_container, transparent=True)
        input_row1.pack(fill="x", pady=(0, 5))
        
        self.event_title_entry = ctk.CTkEntry(
            input_row1,
            placeholder_text="Event title...",
            height=35
        )
        self.event_title_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Set focus after a short delay
        self.after(100, lambda: self.event_title_entry.focus())
        
        # Event type dropdown
        self.event_type_var = ctk.StringVar(value="meeting")
        type_menu = ctk.CTkOptionMenu(
            input_row1,
            values=["meeting", "deadline", "reminder", "other"],
            variable=self.event_type_var,
            width=120
        )
        type_menu.pack(side="left")
        
        # Date/time row
        input_row2 = CustomFrame(add_container, transparent=True)
        input_row2.pack(fill="x", pady=(0, 10))
        
        CustomLabel(
            input_row2,
            text="Date:",
            size=11
        ).pack(side="left", padx=(0, 5))
        
        self.event_date_entry = ctk.CTkEntry(
            input_row2,
            placeholder_text="YYYY-MM-DD",
            width=120,
            height=35
        )
        self.event_date_entry.pack(side="left", padx=(0, 10))
        self.event_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        CustomLabel(
            input_row2,
            text="Time:",
            size=11
        ).pack(side="left", padx=(0, 5))
        
        self.event_time_entry = ctk.CTkEntry(
            input_row2,
            placeholder_text="HH:MM",
            width=80,
            height=35
        )
        self.event_time_entry.pack(side="left", padx=(0, 10))
        self.event_time_entry.insert(0, "10:00")
        
        CustomButton(
            input_row2,
            text="Add Event",
            command=self._add_event,
            style="primary",
            width=100
        ).pack(side="left")
        
        # Events list
        events_container = CustomFrame(self, transparent=False)
        events_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Fixed frame for events (no scrollbar)
        self.events_scroll = CustomFrame(events_container, transparent=True)
        self.events_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        debug("CalendarModule", "Calendar UI created")
    
    def _add_event(self):
        """Add new event"""
        title = self.event_title_entry.get().strip()
        date_str = self.event_date_entry.get().strip()
        time_str = self.event_time_entry.get().strip()
        
        if not title:
            MessageBox.show_error(self, "Error", "Please enter an event title")
            return
        
        try:
            # Parse date and time
            start_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            end_datetime = start_datetime + timedelta(hours=1)
            
            event_type = self.event_type_var.get()
            
            debug("CalendarModule", f"Adding event: {title} at {start_datetime}")
            
            event_id = self.calendar.create_event(
                title=title,
                start_time=start_datetime.isoformat(),
                end_time=end_datetime.isoformat(),
                event_type=event_type,
                created_by=self.current_user_id
            )
            
            if event_id:
                info("CalendarModule", f"Event created: {event_id}")
                MessageBox.show_success(self, "Success", f"Event '{title}' created!")
                self.event_title_entry.delete(0, "end")
                self._load_events()
            else:
                error("CalendarModule", "Failed to create event")
                MessageBox.show_error(self, "Error", "Failed to create event")
                
        except ValueError as e:
            error("CalendarModule", f"Invalid date/time format: {e}")
            MessageBox.show_error(self, "Error", "Invalid date or time format.\nUse YYYY-MM-DD and HH:MM")
    
    def _load_events(self):
        """Load and display events for current month"""
        try:
            debug("CalendarModule", f"Loading events for {self.current_date.year}-{self.current_date.month:02d}")
            
            # Get events for current month
            self.events = self.calendar.get_events_for_month(
                self.current_date.year,
                self.current_date.month
            )
            
            debug("CalendarModule", f"Found {len(self.events)} events for display")
        except Exception as e:
            error("CalendarModule", f"Error loading events: {e}")
            self.events = []
        
        # Clear existing events
        for widget in self.events_scroll.winfo_children():
            widget.destroy()
        
        if not self.events:
            CustomLabel(
                self.events_scroll,
                text="📅 No events this month. Create your first event above!",
                size=12,
                color=("#888888", "#888888")
            ).pack(pady=50)
            return
        
        # Sort events by date
        self.events.sort(key=lambda e: e['start_time'])
        
        # Display events
        for event in self.events:
            self._create_event_card(event)
        
        info("CalendarModule", f"Loaded {len(self.events)} events")
    
    def _create_event_card(self, event: Dict):
        """Create event card widget"""
        # Event card
        card = CustomFrame(self.events_scroll, transparent=False)
        card.pack(fill="x", pady=5)
        
        content = CustomFrame(card, transparent=True)
        content.pack(fill="x", padx=15, pady=10)
        
        # Parse datetime
        start_time = datetime.fromisoformat(event['start_time'])
        
        # Header row
        header_row = CustomFrame(content, transparent=True)
        header_row.pack(fill="x", pady=(0, 5))
        
        # Event type indicator
        type_colors = {
            "meeting": "#2196F3",
            "deadline": "#F44336",
            "reminder": "#FF9800",
            "other": "#9C27B0"
        }
        type_color = type_colors.get(event['event_type'], "#888888")
        
        type_label = CustomLabel(
            header_row,
            text=f"● {event['event_type'].upper()}",
            size=10,
            bold=True,
            color=(type_color, type_color)
        )
        type_label.pack(side="left", padx=(0, 10))
        
        # Date/time
        date_label = CustomLabel(
            header_row,
            text=start_time.strftime("%b %d, %Y at %H:%M"),
            size=11,
            color=("#666666", "#999999")
        )
        date_label.pack(side="left")
        
        # Event title
        title_label = CustomLabel(
            content,
            text=event['title'],
            size=14,
            bold=True
        )
        title_label.pack(anchor="w", pady=(0, 5))
        
        # Description if exists
        if event.get('description'):
            desc_label = CustomLabel(
                content,
                text=event['description'],
                size=11,
                color=("#666666", "#999999")
            )
            desc_label.pack(anchor="w", pady=(0, 5))
        
        # Location if exists
        if event.get('location'):
            loc_label = CustomLabel(
                content,
                text=f"📍 {event['location']}",
                size=11,
                color=("#666666", "#999999")
            )
            loc_label.pack(anchor="w", pady=(0, 5))
        
        # Actions row
        actions_row = CustomFrame(content, transparent=True)
        actions_row.pack(fill="x", pady=(5, 0))
        
        # Delete button
        CustomButton(
            actions_row,
            text="🗑️ Delete",
            command=lambda e=event: self._delete_event(e['id']),
            style="secondary",
            width=100,
            height=30
        ).pack(side="right")
    
    def _delete_event(self, event_id: int):
        """Delete event"""
        debug("CalendarModule", f"Deleting event: {event_id}")
        
        success = self.calendar.delete_event(event_id)
        
        if success:
            info("CalendarModule", f"Event {event_id} deleted")
            self._load_events()
        else:
            error("CalendarModule", f"Failed to delete event {event_id}")
    
    def _previous_month(self):
        """Go to previous month"""
        self.current_date = self.current_date.replace(day=1) - timedelta(days=1)
        self.month_label.configure(text=self.current_date.strftime("%B %Y"))
        self._load_events()
    
    def _next_month(self):
        """Go to next month"""
        next_month = self.current_date.month + 1
        next_year = self.current_date.year
        
        if next_month > 12:
            next_month = 1
            next_year += 1
        
        self.current_date = self.current_date.replace(month=next_month, year=next_year)
        self.month_label.configure(text=self.current_date.strftime("%B %Y"))
        self._load_events()
    
    def _go_to_today(self):
        """Go to current month"""
        self.current_date = datetime.now()
        self.month_label.configure(text=self.current_date.strftime("%B %Y"))
        self._load_events()

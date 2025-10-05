"""
Team Calendar System
Delad kalender för teams
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from core.debug_logger import debug, info, warning, error, exception


class TeamCalendar:
    """System för team calendar"""
    
    def __init__(self, team_id: str):
        """
        Initialize team calendar
        
        Args:
            team_id: Team ID
        """
        debug("TeamCalendar", f"Initializing team calendar for team: {team_id}")
        
        self.team_id = team_id
        self.db_path = Path(f"data/calendar_{team_id}.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._setup_database()
        
        info("TeamCalendar", "Team calendar initialized")
    
    def _setup_database(self):
        """Setup database for calendar events"""
        debug("TeamCalendar", "Setting up calendar database")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    location TEXT,
                    event_type TEXT DEFAULT 'meeting',
                    created_by TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    all_day BOOLEAN DEFAULT 0,
                    recurring TEXT,
                    attendees TEXT,
                    reminder_minutes INTEGER DEFAULT 15
                )
            """)
            
            # Index for date queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_start_time 
                ON events(start_time)
            """)
            
            conn.commit()
            conn.close()
            
            debug("TeamCalendar", "Database setup completed")
            
        except Exception as e:
            exception("TeamCalendar", f"Error setting up database: {e}")
    
    def create_event(
        self,
        title: str,
        start_time: str,
        end_time: str,
        description: str = "",
        location: str = "",
        event_type: str = "meeting",
        created_by: str = "",
        all_day: bool = False,
        recurring: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        reminder_minutes: int = 15
    ) -> Optional[int]:
        """
        Create calendar event
        
        Args:
            title: Event title
            start_time: Start time (ISO format)
            end_time: End time (ISO format)
            description: Event description
            location: Event location
            event_type: Type (meeting, deadline, reminder, etc.)
            created_by: Creator user ID
            all_day: All-day event
            recurring: Recurrence pattern (daily, weekly, monthly)
            attendees: List of attendee user IDs
            reminder_minutes: Minutes before event to remind
            
        Returns:
            Event ID if successful
        """
        debug("TeamCalendar", f"Creating event: {title}")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            attendees_str = ",".join(attendees) if attendees else ""
            
            cursor.execute("""
                INSERT INTO events 
                (title, description, start_time, end_time, location, event_type, 
                 created_by, created_at, all_day, recurring, attendees, reminder_minutes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                title,
                description,
                start_time,
                end_time,
                location,
                event_type,
                created_by,
                datetime.now().isoformat(),
                all_day,
                recurring,
                attendees_str,
                reminder_minutes
            ))
            
            event_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            info("TeamCalendar", f"Event created: {event_id}")
            return event_id
            
        except Exception as e:
            exception("TeamCalendar", f"Error creating event: {e}")
            return None
    
    def get_events(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        event_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Get events within date range
        
        Args:
            start_date: Start date filter (ISO format)
            end_date: End date filter (ISO format)
            event_type: Filter by event type
            
        Returns:
            List of event dicts
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM events WHERE 1=1"
            params = []
            
            if start_date:
                query += " AND start_time >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND start_time <= ?"
                params.append(end_date)
            
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)
            
            query += " ORDER BY start_time ASC"
            
            cursor.execute(query, params)
            
            columns = [desc[0] for desc in cursor.description]
            events = []
            
            for row in cursor.fetchall():
                event = dict(zip(columns, row))
                # Parse attendees
                if event['attendees']:
                    event['attendees'] = event['attendees'].split(',')
                else:
                    event['attendees'] = []
                events.append(event)
            
            conn.close()
            
            return events
            
        except Exception as e:
            exception("TeamCalendar", f"Error getting events: {e}")
            return []
    
    def get_events_for_day(self, date: str) -> List[Dict]:
        """
        Get all events for a specific day
        
        Args:
            date: Date in YYYY-MM-DD format
            
        Returns:
            List of events
        """
        start = f"{date}T00:00:00"
        end = f"{date}T23:59:59"
        return self.get_events(start_date=start, end_date=end)
    
    def get_events_for_week(self, start_date: str) -> List[Dict]:
        """
        Get events for a week
        
        Args:
            start_date: Week start date (YYYY-MM-DD)
            
        Returns:
            List of events
        """
        start = datetime.fromisoformat(start_date)
        end = start + timedelta(days=7)
        
        return self.get_events(
            start_date=start.isoformat(),
            end_date=end.isoformat()
        )
    
    def get_events_for_month(self, year: int, month: int) -> List[Dict]:
        """
        Get events for a month
        
        Args:
            year: Year
            month: Month (1-12)
            
        Returns:
            List of events
        """
        start = datetime(year, month, 1)
        
        # Get last day of month
        if month == 12:
            end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end = datetime(year, month + 1, 1) - timedelta(days=1)
        
        return self.get_events(
            start_date=start.isoformat(),
            end_date=end.isoformat()
        )
    
    def update_event(
        self,
        event_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        location: Optional[str] = None,
        event_type: Optional[str] = None
    ) -> bool:
        """
        Update event
        
        Args:
            event_id: Event ID
            title: New title
            description: New description
            start_time: New start time
            end_time: New end time
            location: New location
            event_type: New event type
            
        Returns:
            True if successful
        """
        debug("TeamCalendar", f"Updating event: {event_id}")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if title is not None:
                updates.append("title = ?")
                params.append(title)
            
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            
            if start_time is not None:
                updates.append("start_time = ?")
                params.append(start_time)
            
            if end_time is not None:
                updates.append("end_time = ?")
                params.append(end_time)
            
            if location is not None:
                updates.append("location = ?")
                params.append(location)
            
            if event_type is not None:
                updates.append("event_type = ?")
                params.append(event_type)
            
            if not updates:
                warning("TeamCalendar", "No updates provided")
                conn.close()
                return False
            
            params.append(event_id)
            
            query = f"UPDATE events SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            
            conn.commit()
            conn.close()
            
            info("TeamCalendar", f"Event updated: {event_id}")
            return True
            
        except Exception as e:
            exception("TeamCalendar", f"Error updating event: {e}")
            return False
    
    def delete_event(self, event_id: int) -> bool:
        """
        Delete event
        
        Args:
            event_id: Event ID
            
        Returns:
            True if successful
        """
        debug("TeamCalendar", f"Deleting event: {event_id}")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
            
            conn.commit()
            conn.close()
            
            info("TeamCalendar", f"Event deleted: {event_id}")
            return True
            
        except Exception as e:
            exception("TeamCalendar", f"Error deleting event: {e}")
            return False
    
    def get_upcoming_events(self, days: int = 7) -> List[Dict]:
        """
        Get upcoming events
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of upcoming events
        """
        now = datetime.now()
        end = now + timedelta(days=days)
        
        return self.get_events(
            start_date=now.isoformat(),
            end_date=end.isoformat()
        )

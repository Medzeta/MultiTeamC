"""
Team Groups System - Ultimate Tier Feature
Allows organizing multiple teams into groups
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from .debug_logger import debug, info, warning, error

class TeamGroupsSystem:
    """
    Team Groups management system
    Only available for Ultimate tier license holders
    """
    
    def __init__(self, user_id: int, license_system):
        """Initialize team groups system"""
        self.user_id = user_id
        self.license_system = license_system
        self.db_path = Path("data") / f"team_groups_{user_id}.db"
        self.db_path.parent.mkdir(exist_ok=True)
        
        self._setup_database()
        
        info("TeamGroups", f"Team groups system initialized for user {user_id}")
    
    def _setup_database(self):
        """Setup database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Groups table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    color TEXT DEFAULT '#3a3a3a',
                    created_at TEXT NOT NULL,
                    created_by INTEGER NOT NULL
                )
            """)
            
            # Group members (teams in group)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS group_teams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    team_id INTEGER NOT NULL,
                    added_at TEXT NOT NULL,
                    added_by INTEGER NOT NULL,
                    FOREIGN KEY (group_id) REFERENCES groups(id),
                    UNIQUE(group_id, team_id)
                )
            """)
            
            # Group settings
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS group_settings (
                    group_id INTEGER PRIMARY KEY,
                    settings TEXT NOT NULL,
                    FOREIGN KEY (group_id) REFERENCES groups(id)
                )
            """)
            
            conn.commit()
            conn.close()
            
            debug("TeamGroups", "Database setup completed")
        except Exception as e:
            error("TeamGroups", f"Database setup error: {e}")
    
    def has_access(self) -> bool:
        """Check if user has access to team groups (Ultimate tier)"""
        return self.license_system.has_team_groups()
    
    def create_group(self, name: str, description: str = "", color: str = "#3a3a3a") -> Optional[int]:
        """
        Create a new team group
        
        Args:
            name: Group name
            description: Group description
            color: Group color (hex)
            
        Returns:
            int: Group ID or None if failed
        """
        if not self.has_access():
            warning("TeamGroups", "User does not have access to team groups")
            return None
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO groups (name, description, color, created_at, created_by)
                VALUES (?, ?, ?, ?, ?)
            """, (name, description, color, datetime.now().isoformat(), self.user_id))
            
            group_id = cursor.lastrowid
            
            # Create default settings
            default_settings = {
                "auto_sync": True,
                "notifications": True,
                "shared_files": True
            }
            
            cursor.execute("""
                INSERT INTO group_settings (group_id, settings)
                VALUES (?, ?)
            """, (group_id, json.dumps(default_settings)))
            
            conn.commit()
            conn.close()
            
            info("TeamGroups", f"Group created: {name} (ID: {group_id})")
            return group_id
        except Exception as e:
            error("TeamGroups", f"Error creating group: {e}")
            return None
    
    def add_team_to_group(self, group_id: int, team_id: int) -> bool:
        """
        Add a team to a group
        
        Args:
            group_id: Group ID
            team_id: Team ID
            
        Returns:
            bool: Success
        """
        if not self.has_access():
            warning("TeamGroups", "User does not have access to team groups")
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR IGNORE INTO group_teams (group_id, team_id, added_at, added_by)
                VALUES (?, ?, ?, ?)
            """, (group_id, team_id, datetime.now().isoformat(), self.user_id))
            
            conn.commit()
            conn.close()
            
            info("TeamGroups", f"Team {team_id} added to group {group_id}")
            return True
        except Exception as e:
            error("TeamGroups", f"Error adding team to group: {e}")
            return False
    
    def remove_team_from_group(self, group_id: int, team_id: int) -> bool:
        """Remove a team from a group"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM group_teams
                WHERE group_id = ? AND team_id = ?
            """, (group_id, team_id))
            
            conn.commit()
            conn.close()
            
            info("TeamGroups", f"Team {team_id} removed from group {group_id}")
            return True
        except Exception as e:
            error("TeamGroups", f"Error removing team from group: {e}")
            return False
    
    def get_all_groups(self) -> List[Dict]:
        """Get all groups for user"""
        if not self.has_access():
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, description, color, created_at
                FROM groups
                ORDER BY created_at DESC
            """)
            
            groups = []
            for row in cursor.fetchall():
                groups.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "color": row[3],
                    "created_at": row[4]
                })
            
            conn.close()
            
            debug("TeamGroups", f"Retrieved {len(groups)} groups")
            return groups
        except Exception as e:
            error("TeamGroups", f"Error getting groups: {e}")
            return []
    
    def get_group_teams(self, group_id: int) -> List[int]:
        """Get all teams in a group"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT team_id FROM group_teams
                WHERE group_id = ?
                ORDER BY added_at DESC
            """, (group_id,))
            
            team_ids = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            debug("TeamGroups", f"Group {group_id} has {len(team_ids)} teams")
            return team_ids
        except Exception as e:
            error("TeamGroups", f"Error getting group teams: {e}")
            return []
    
    def delete_group(self, group_id: int) -> bool:
        """Delete a group (teams remain, just removed from group)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete group teams
            cursor.execute("DELETE FROM group_teams WHERE group_id = ?", (group_id,))
            
            # Delete group settings
            cursor.execute("DELETE FROM group_settings WHERE group_id = ?", (group_id,))
            
            # Delete group
            cursor.execute("DELETE FROM groups WHERE id = ?", (group_id,))
            
            conn.commit()
            conn.close()
            
            info("TeamGroups", f"Group {group_id} deleted")
            return True
        except Exception as e:
            error("TeamGroups", f"Error deleting group: {e}")
            return False
    
    def update_group(self, group_id: int, name: str = None, description: str = None, color: str = None) -> bool:
        """Update group information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if name:
                updates.append("name = ?")
                params.append(name)
            
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            
            if color:
                updates.append("color = ?")
                params.append(color)
            
            if not updates:
                return False
            
            params.append(group_id)
            
            cursor.execute(f"""
                UPDATE groups
                SET {', '.join(updates)}
                WHERE id = ?
            """, params)
            
            conn.commit()
            conn.close()
            
            info("TeamGroups", f"Group {group_id} updated")
            return True
        except Exception as e:
            error("TeamGroups", f"Error updating group: {e}")
            return False
    
    def get_group_info(self, group_id: int) -> Optional[Dict]:
        """Get detailed group information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, description, color, created_at
                FROM groups
                WHERE id = ?
            """, (group_id,))
            
            row = cursor.fetchone()
            
            if not row:
                conn.close()
                return None
            
            group_info = {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "color": row[3],
                "created_at": row[4],
                "teams": self.get_group_teams(group_id)
            }
            
            conn.close()
            
            return group_info
        except Exception as e:
            error("TeamGroups", f"Error getting group info: {e}")
            return None


# Debug logging
debug("TeamGroups", "Team groups system module loaded")

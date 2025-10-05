"""
Team System
Hantera teams, medlemmar och delad data mellan peers
"""

import sqlite3
import json
import uuid
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
from core.debug_logger import debug, info, warning, error, exception


class TeamSystem:
    """Team management system"""
    
    def __init__(self, user_id: int, p2p_system, license_system=None):
        """
        Initialize team system
        
        Args:
            user_id: Current user's ID
            p2p_system: P2PSystem instance for communication
            license_system: LicenseSystem instance for enforcement (optional)
        """
        debug("TeamSystem", f"Initializing team system for user {user_id}")
        
        self.user_id = user_id
        self.p2p_system = p2p_system
        self.license_system = license_system
        self.db_path = Path("data/teams.db")
        self.team_sync = None  # Will be set externally
        
        # Initialize database
        self._init_database()
        
        info("TeamSystem", "Team system initialized")
    
    def _init_database(self):
        """Initialize teams database"""
        debug("TeamSystem", "Initializing teams database")
        
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Teams table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teams (
                    team_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_by INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Team members table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS team_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_id TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    peer_id TEXT,
                    role TEXT NOT NULL DEFAULT 'member',
                    joined_at TEXT NOT NULL,
                    FOREIGN KEY (team_id) REFERENCES teams(team_id),
                    UNIQUE(team_id, user_id)
                )
            """)
            
            # Team invitations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS team_invitations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_id TEXT NOT NULL,
                    from_user_id INTEGER NOT NULL,
                    to_peer_id TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    responded_at TEXT,
                    FOREIGN KEY (team_id) REFERENCES teams(team_id)
                )
            """)
            
            # Team data table (för delad data)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS team_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_id TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    data_key TEXT NOT NULL,
                    data_value TEXT,
                    created_by INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1,
                    FOREIGN KEY (team_id) REFERENCES teams(team_id),
                    UNIQUE(team_id, data_type, data_key)
                )
            """)
            
            # Sync log table (för att spåra synkronisering)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sync_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    data_id INTEGER,
                    synced_at TEXT NOT NULL,
                    synced_with_peer TEXT,
                    FOREIGN KEY (team_id) REFERENCES teams(team_id)
                )
            """)
            
            conn.commit()
            conn.close()
            
            info("TeamSystem", "Teams database initialized successfully")
            
        except Exception as e:
            exception("TeamSystem", f"Error initializing database: {e}")
    
    def create_team(self, name: str, description: str = "") -> Optional[str]:
        """
        Create a new team
        
        Args:
            name: Team name
            description: Team description
        
        Returns:
            Team ID if successful, None otherwise
        """
        info("TeamSystem", f"Creating team: {name}")
        
        # Check license limits
        if self.license_system:
            current_teams = len(self.get_user_teams(self.user_id))
            can_create, reason = self.license_system.can_create_team(current_teams)
            
            if not can_create:
                warning("TeamSystem", f"Cannot create team: {reason}")
                return None
        
        try:
            team_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create team
            cursor.execute("""
                INSERT INTO teams (team_id, name, description, created_by, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (team_id, name, description, self.user_id, now, now))
            
            # Add creator as owner
            cursor.execute("""
                INSERT INTO team_members (team_id, user_id, role, joined_at)
                VALUES (?, ?, 'owner', ?)
            """, (team_id, self.user_id, now))
            
            conn.commit()
            conn.close()
            
            info("TeamSystem", f"Team created successfully: {team_id}")
            return team_id
            
        except Exception as e:
            exception("TeamSystem", f"Error creating team: {e}")
            return None
    
    def get_my_teams(self) -> List[Dict]:
        """Get all teams current user is member of"""
        debug("TeamSystem", f"Getting teams for user {self.user_id}")
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT t.*, tm.role, tm.joined_at
                FROM teams t
                JOIN team_members tm ON t.team_id = tm.team_id
                WHERE tm.user_id = ?
                ORDER BY t.created_at DESC
            """, (self.user_id,))
            
            teams = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            debug("TeamSystem", f"Found {len(teams)} teams")
            return teams
            
        except Exception as e:
            exception("TeamSystem", f"Error getting teams: {e}")
            return []
    
    def get_user_teams(self, user_id: int) -> List[Dict]:
        """
        Get all teams for a specific user (alias for get_my_teams)
        
        Args:
            user_id: User ID (ignored, uses self.user_id)
            
        Returns:
            List of team dicts
        """
        return self.get_my_teams()
    
    def get_team_members(self, team_id: str) -> List[Dict]:
        """Get all members of a team"""
        debug("TeamSystem", f"Getting members for team {team_id}")
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM team_members
                WHERE team_id = ?
                ORDER BY joined_at ASC
            """, (team_id,))
            
            members = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            debug("TeamSystem", f"Found {len(members)} members")
            return members
            
        except Exception as e:
            exception("TeamSystem", f"Error getting team members: {e}")
            return []
    
    def invite_peer_to_team(self, team_id: str, peer_id: str) -> bool:
        """
        Invite a peer to join team
        
        Args:
            team_id: Team ID
            peer_id: Peer's client ID
        
        Returns:
            True if invitation sent successfully
        """
        info("TeamSystem", f"Inviting peer {peer_id[:8]}... to team {team_id[:8]}...")
        
        try:
            # Check if user is owner/admin
            if not self._can_invite(team_id):
                warning("TeamSystem", "User does not have permission to invite")
                return False
            
            # Check license limits for members
            if self.license_system:
                current_members = len(self.get_team_members(team_id))
                can_add, reason = self.license_system.can_add_member(team_id, current_members)
                
                if not can_add:
                    warning("TeamSystem", f"Cannot add member: {reason}")
                    return False
            
            # Check if peer is connected
            if not self.p2p_system.is_connected(peer_id):
                warning("TeamSystem", f"Peer {peer_id[:8]}... is not connected")
                return False
            
            # Create invitation in database
            now = datetime.now().isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO team_invitations (team_id, from_user_id, to_peer_id, created_at)
                VALUES (?, ?, ?, ?)
            """, (team_id, self.user_id, peer_id, now))
            
            invitation_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Send invitation via P2P
            team_info = self._get_team_info(team_id)
            
            message = {
                'type': 'team_invitation',
                'invitation_id': invitation_id,
                'team_id': team_id,
                'team_name': team_info['name'],
                'team_description': team_info['description'],
                'from_user_id': self.user_id
            }
            
            success = self.p2p_system.send_message(peer_id, message)
            
            if success:
                info("TeamSystem", f"Invitation sent to peer {peer_id[:8]}...")
            else:
                warning("TeamSystem", f"Failed to send invitation to peer {peer_id[:8]}...")
            
            return success
            
        except Exception as e:
            exception("TeamSystem", f"Error inviting peer: {e}")
            return False
    
    def accept_invitation(self, invitation_id: int, team_id: str) -> bool:
        """Accept team invitation"""
        info("TeamSystem", f"Accepting invitation {invitation_id}")
        
        try:
            now = datetime.now().isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update invitation status
            cursor.execute("""
                UPDATE team_invitations
                SET status = 'accepted', responded_at = ?
                WHERE id = ?
            """, (now, invitation_id))
            
            # Add user to team
            cursor.execute("""
                INSERT INTO team_members (team_id, user_id, role, joined_at)
                VALUES (?, ?, 'member', ?)
            """, (team_id, self.user_id, now))
            
            conn.commit()
            conn.close()
            
            info("TeamSystem", f"Invitation accepted, joined team {team_id[:8]}...")
            return True
            
        except Exception as e:
            exception("TeamSystem", f"Error accepting invitation: {e}")
            return False
    
    def leave_team(self, team_id: str) -> bool:
        """Leave a team"""
        info("TeamSystem", f"Leaving team {team_id[:8]}...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user is owner
            cursor.execute("""
                SELECT role FROM team_members
                WHERE team_id = ? AND user_id = ?
            """, (team_id, self.user_id))
            
            result = cursor.fetchone()
            if result and result[0] == 'owner':
                warning("TeamSystem", "Owner cannot leave team, must transfer ownership first")
                conn.close()
                return False
            
            # Remove user from team
            cursor.execute("""
                DELETE FROM team_members
                WHERE team_id = ? AND user_id = ?
            """, (team_id, self.user_id))
            
            conn.commit()
            conn.close()
            
            info("TeamSystem", f"Left team {team_id[:8]}...")
            return True
            
        except Exception as e:
            exception("TeamSystem", f"Error leaving team: {e}")
            return False
    
    def _can_invite(self, team_id: str) -> bool:
        """Check if user can invite members to team"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT role FROM team_members
                WHERE team_id = ? AND user_id = ?
            """, (team_id, self.user_id))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                role = result[0]
                return role in ['owner', 'admin']
            
            return False
            
        except Exception as e:
            exception("TeamSystem", f"Error checking permissions: {e}")
            return False
    
    def _get_team_info(self, team_id: str) -> Optional[Dict]:
        """Get team information"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM teams WHERE team_id = ?
            """, (team_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return dict(result)
            
            return None
            
        except Exception as e:
            exception("TeamSystem", f"Error getting team info: {e}")
            return None
    
    def set_team_data(self, team_id: str, data_type: str, data_key: str, data_value: any) -> bool:
        """
        Set team data (will be synced with other members)
        
        Args:
            team_id: Team ID
            data_type: Type of data (e.g., 'chat', 'file', 'note')
            data_key: Unique key for this data
            data_value: Data value (will be JSON serialized)
        
        Returns:
            True if successful
        """
        debug("TeamSystem", f"Setting team data: {data_type}/{data_key}")
        
        try:
            now = datetime.now().isoformat()
            value_json = json.dumps(data_value)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert or update
            cursor.execute("""
                INSERT INTO team_data (team_id, data_type, data_key, data_value, created_by, created_at, updated_at, version)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                ON CONFLICT(team_id, data_type, data_key) DO UPDATE SET
                    data_value = excluded.data_value,
                    updated_at = excluded.updated_at,
                    version = version + 1
            """, (team_id, data_type, data_key, value_json, self.user_id, now, now))
            
            conn.commit()
            conn.close()
            
            # Queue for sync if team_sync is available
            if self.team_sync:
                self.team_sync.queue_sync(team_id, data_type, data_key, data_value)
            
            info("TeamSystem", f"Team data set: {data_type}/{data_key}")
            return True
            
        except Exception as e:
            exception("TeamSystem", f"Error setting team data: {e}")
            return False
    
    def get_team_data(self, team_id: str, data_type: str = None) -> List[Dict]:
        """Get team data, optionally filtered by type"""
        debug("TeamSystem", f"Getting team data for {team_id[:8]}...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if data_type:
                cursor.execute("""
                    SELECT * FROM team_data
                    WHERE team_id = ? AND data_type = ?
                    ORDER BY updated_at DESC
                """, (team_id, data_type))
            else:
                cursor.execute("""
                    SELECT * FROM team_data
                    WHERE team_id = ?
                    ORDER BY updated_at DESC
                """, (team_id,))
            
            data = []
            for row in cursor.fetchall():
                item = dict(row)
                # Parse JSON value
                try:
                    item['data_value'] = json.loads(item['data_value'])
                except:
                    pass
                data.append(item)
            
            conn.close()
            
            debug("TeamSystem", f"Found {len(data)} data items")
            return data
            
        except Exception as e:
            exception("TeamSystem", f"Error getting team data: {e}")
            return []


if __name__ == "__main__":
    # Test team system
    info("TEST", "Testing TeamSystem...")
    
    from core.p2p_system import P2PSystem
    
    # Create P2P system
    p2p = P2PSystem()
    
    # Create team system
    team_sys = TeamSystem(user_id=1, p2p_system=p2p)
    
    # Create a test team
    team_id = team_sys.create_team("Test Team", "A test team for development")
    print(f"Created team: {team_id}")
    
    # Get my teams
    teams = team_sys.get_my_teams()
    print(f"My teams: {len(teams)}")
    for team in teams:
        print(f"  - {team['name']} ({team['role']})")
    
    # Set some team data
    team_sys.set_team_data(team_id, "note", "welcome", {"text": "Welcome to the team!"})
    
    # Get team data
    data = team_sys.get_team_data(team_id)
    print(f"Team data: {len(data)} items")
    for item in data:
        print(f"  - {item['data_type']}/{item['data_key']}: {item['data_value']}")
    
    print("\n✅ Team system working!")

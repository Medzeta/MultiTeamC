"""
Team Permissions System
Roller och behörigheter för team members
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from core.debug_logger import debug, info, warning, error, exception


class TeamPermissions:
    """System för team permissions och roller"""
    
    # Role definitions
    ROLES = {
        'owner': {
            'name': 'Owner',
            'level': 100,
            'permissions': [
                'delete_team',
                'manage_roles',
                'invite_members',
                'remove_members',
                'manage_settings',
                'send_messages',
                'upload_files',
                'create_channels',
                'delete_channels',
                'view_audit_log'
            ]
        },
        'admin': {
            'name': 'Admin',
            'level': 75,
            'permissions': [
                'invite_members',
                'remove_members',
                'manage_settings',
                'send_messages',
                'upload_files',
                'create_channels',
                'delete_channels',
                'view_audit_log'
            ]
        },
        'member': {
            'name': 'Member',
            'level': 50,
            'permissions': [
                'send_messages',
                'upload_files',
                'create_channels'
            ]
        },
        'guest': {
            'name': 'Guest',
            'level': 25,
            'permissions': [
                'send_messages'
            ]
        }
    }
    
    def __init__(self, user_id: str):
        """
        Initialize team permissions system
        
        Args:
            user_id: Current user ID
        """
        debug("TeamPermissions", f"Initializing team permissions for user: {user_id}")
        
        self.user_id = user_id
        self.db_path = Path(f"data/team_permissions_{user_id}.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._setup_database()
        
        info("TeamPermissions", "Team permissions system initialized")
    
    def _setup_database(self):
        """Setup database for permissions"""
        debug("TeamPermissions", "Setting up permissions database")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Team member roles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS member_roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    assigned_by TEXT,
                    assigned_at TEXT NOT NULL,
                    UNIQUE(team_id, user_id)
                )
            """)
            
            # Custom permissions table (overrides)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS custom_permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    permission TEXT NOT NULL,
                    granted BOOLEAN NOT NULL,
                    granted_by TEXT,
                    granted_at TEXT NOT NULL,
                    UNIQUE(team_id, user_id, permission)
                )
            """)
            
            # Indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_member_roles_team 
                ON member_roles(team_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_member_roles_user 
                ON member_roles(team_id, user_id)
            """)
            
            conn.commit()
            conn.close()
            
            debug("TeamPermissions", "Database setup completed")
            
        except Exception as e:
            exception("TeamPermissions", f"Error setting up database: {e}")
    
    def set_role(
        self,
        team_id: str,
        user_id: str,
        role: str,
        assigned_by: Optional[str] = None
    ) -> bool:
        """
        Set role for team member
        
        Args:
            team_id: Team ID
            user_id: User ID
            role: Role name (owner, admin, member, guest)
            assigned_by: User ID who assigned the role
            
        Returns:
            True if successful
        """
        if role not in self.ROLES:
            error("TeamPermissions", f"Invalid role: {role}")
            return False
        
        debug("TeamPermissions", f"Setting role {role} for user {user_id[:8]}... in team {team_id[:8]}...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO member_roles 
                (team_id, user_id, role, assigned_by, assigned_at)
                VALUES (?, ?, ?, ?, ?)
            """, (team_id, user_id, role, assigned_by, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            info("TeamPermissions", f"Role {role} set for user {user_id[:8]}...")
            return True
            
        except Exception as e:
            exception("TeamPermissions", f"Error setting role: {e}")
            return False
    
    def get_role(self, team_id: str, user_id: str) -> Optional[str]:
        """
        Get role for team member
        
        Args:
            team_id: Team ID
            user_id: User ID
            
        Returns:
            Role name or None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT role FROM member_roles
                WHERE team_id = ? AND user_id = ?
            """, (team_id, user_id))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0]
            return None
            
        except Exception as e:
            exception("TeamPermissions", f"Error getting role: {e}")
            return None
    
    def has_permission(
        self,
        team_id: str,
        user_id: str,
        permission: str
    ) -> bool:
        """
        Check if user has permission in team
        
        Args:
            team_id: Team ID
            user_id: User ID
            permission: Permission name
            
        Returns:
            True if user has permission
        """
        debug("TeamPermissions", f"Checking permission {permission} for user {user_id[:8]}...")
        
        # Check custom permissions first
        custom = self._get_custom_permission(team_id, user_id, permission)
        if custom is not None:
            return custom
        
        # Get role
        role = self.get_role(team_id, user_id)
        if not role:
            debug("TeamPermissions", f"User has no role in team")
            return False
        
        # Check role permissions
        role_data = self.ROLES.get(role, {})
        permissions = role_data.get('permissions', [])
        
        has_perm = permission in permissions
        debug("TeamPermissions", f"User has permission: {has_perm}")
        
        return has_perm
    
    def _get_custom_permission(
        self,
        team_id: str,
        user_id: str,
        permission: str
    ) -> Optional[bool]:
        """Get custom permission override"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT granted FROM custom_permissions
                WHERE team_id = ? AND user_id = ? AND permission = ?
            """, (team_id, user_id, permission))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return bool(result[0])
            return None
            
        except Exception as e:
            exception("TeamPermissions", f"Error getting custom permission: {e}")
            return None
    
    def grant_permission(
        self,
        team_id: str,
        user_id: str,
        permission: str,
        granted_by: Optional[str] = None
    ) -> bool:
        """Grant custom permission to user"""
        debug("TeamPermissions", f"Granting permission {permission} to user {user_id[:8]}...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO custom_permissions 
                (team_id, user_id, permission, granted, granted_by, granted_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (team_id, user_id, permission, True, granted_by, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            info("TeamPermissions", f"Permission {permission} granted")
            return True
            
        except Exception as e:
            exception("TeamPermissions", f"Error granting permission: {e}")
            return False
    
    def revoke_permission(
        self,
        team_id: str,
        user_id: str,
        permission: str,
        granted_by: Optional[str] = None
    ) -> bool:
        """Revoke custom permission from user"""
        debug("TeamPermissions", f"Revoking permission {permission} from user {user_id[:8]}...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO custom_permissions 
                (team_id, user_id, permission, granted, granted_by, granted_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (team_id, user_id, permission, False, granted_by, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            info("TeamPermissions", f"Permission {permission} revoked")
            return True
            
        except Exception as e:
            exception("TeamPermissions", f"Error revoking permission: {e}")
            return False
    
    def get_team_members_by_role(self, team_id: str, role: str) -> List[str]:
        """Get all members with specific role"""
        debug("TeamPermissions", f"Getting members with role {role} in team {team_id[:8]}...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id FROM member_roles
                WHERE team_id = ? AND role = ?
            """, (team_id, role))
            
            members = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            debug("TeamPermissions", f"Found {len(members)} members with role {role}")
            return members
            
        except Exception as e:
            exception("TeamPermissions", f"Error getting members by role: {e}")
            return []
    
    def get_role_info(self, role: str) -> Optional[Dict]:
        """Get role information"""
        return self.ROLES.get(role)
    
    def get_all_roles(self) -> Dict:
        """Get all available roles"""
        return self.ROLES.copy()
    
    def is_owner(self, team_id: str, user_id: str) -> bool:
        """Check if user is team owner"""
        role = self.get_role(team_id, user_id)
        return role == 'owner'
    
    def is_admin_or_higher(self, team_id: str, user_id: str) -> bool:
        """Check if user is admin or owner"""
        role = self.get_role(team_id, user_id)
        if not role:
            return False
        
        role_level = self.ROLES.get(role, {}).get('level', 0)
        return role_level >= 75  # Admin level
    
    def can_manage_member(
        self,
        team_id: str,
        manager_id: str,
        target_id: str
    ) -> bool:
        """Check if manager can manage target member"""
        manager_role = self.get_role(team_id, manager_id)
        target_role = self.get_role(team_id, target_id)
        
        if not manager_role or not target_role:
            return False
        
        manager_level = self.ROLES.get(manager_role, {}).get('level', 0)
        target_level = self.ROLES.get(target_role, {}).get('level', 0)
        
        # Can only manage members with lower role level
        return manager_level > target_level

"""
Audit Log System
Logging av alla team-aktiviteter för säkerhet och spårbarhet
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from core.debug_logger import debug, info, warning, error, exception


class AuditLog:
    """System för audit logging av team-aktiviteter"""
    
    # Action types
    ACTIONS = {
        # Member actions
        'member_joined': 'Member joined team',
        'member_left': 'Member left team',
        'member_removed': 'Member was removed',
        'member_invited': 'Member was invited',
        
        # Role actions
        'role_changed': 'Member role changed',
        'permission_granted': 'Permission granted',
        'permission_revoked': 'Permission revoked',
        
        # Team actions
        'team_created': 'Team created',
        'team_deleted': 'Team deleted',
        'team_settings_changed': 'Team settings changed',
        'team_renamed': 'Team renamed',
        
        # Channel actions
        'channel_created': 'Channel created',
        'channel_deleted': 'Channel deleted',
        'channel_renamed': 'Channel renamed',
        
        # Message actions
        'message_sent': 'Message sent',
        'message_deleted': 'Message deleted',
        'message_edited': 'Message edited',
        
        # File actions
        'file_uploaded': 'File uploaded',
        'file_downloaded': 'File downloaded',
        'file_deleted': 'File deleted',
        
        # Security actions
        'login_attempt': 'Login attempt',
        'permission_denied': 'Permission denied',
        'suspicious_activity': 'Suspicious activity detected'
    }
    
    def __init__(self, user_id: str):
        """
        Initialize audit log system
        
        Args:
            user_id: Current user ID
        """
        debug("AuditLog", f"Initializing audit log for user: {user_id}")
        
        self.user_id = user_id
        self.db_path = Path(f"data/audit_log_{user_id}.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._setup_database()
        
        info("AuditLog", "Audit log system initialized")
    
    def _setup_database(self):
        """Setup database for audit log"""
        debug("AuditLog", "Setting up audit log database")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Audit log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    actor_id TEXT NOT NULL,
                    actor_name TEXT,
                    target_id TEXT,
                    target_name TEXT,
                    details TEXT,
                    ip_address TEXT,
                    timestamp TEXT NOT NULL,
                    severity TEXT DEFAULT 'info'
                )
            """)
            
            # Indexes for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_team 
                ON audit_log(team_id, timestamp DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_actor 
                ON audit_log(actor_id, timestamp DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_action 
                ON audit_log(action_type, timestamp DESC)
            """)
            
            conn.commit()
            conn.close()
            
            debug("AuditLog", "Database setup completed")
            
        except Exception as e:
            exception("AuditLog", f"Error setting up database: {e}")
    
    def log(
        self,
        team_id: str,
        action_type: str,
        actor_id: str,
        actor_name: Optional[str] = None,
        target_id: Optional[str] = None,
        target_name: Optional[str] = None,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
        severity: str = 'info'
    ) -> bool:
        """
        Log an audit event
        
        Args:
            team_id: Team ID
            action_type: Type of action
            actor_id: User who performed action
            actor_name: Name of actor
            target_id: Target of action (optional)
            target_name: Name of target (optional)
            details: Additional details (optional)
            ip_address: IP address (optional)
            severity: Severity level (info, warning, error)
            
        Returns:
            True if successful
        """
        debug("AuditLog", f"Logging action: {action_type} by {actor_id[:8]}... in team {team_id[:8]}...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO audit_log 
                (team_id, action_type, actor_id, actor_name, target_id, target_name, 
                 details, ip_address, timestamp, severity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                team_id,
                action_type,
                actor_id,
                actor_name,
                target_id,
                target_name,
                details,
                ip_address,
                datetime.now().isoformat(),
                severity
            ))
            
            conn.commit()
            conn.close()
            
            info("AuditLog", f"Action logged: {action_type}")
            return True
            
        except Exception as e:
            exception("AuditLog", f"Error logging action: {e}")
            return False
    
    def get_team_logs(
        self,
        team_id: str,
        limit: int = 100,
        offset: int = 0,
        action_type: Optional[str] = None,
        actor_id: Optional[str] = None,
        severity: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get audit logs for team
        
        Args:
            team_id: Team ID
            limit: Max number of logs to return
            offset: Offset for pagination
            action_type: Filter by action type
            actor_id: Filter by actor
            severity: Filter by severity
            since: Filter by date (get logs since this date)
            
        Returns:
            List of log entries
        """
        debug("AuditLog", f"Getting logs for team {team_id[:8]}... (limit={limit}, offset={offset})")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build query
            query = "SELECT * FROM audit_log WHERE team_id = ?"
            params = [team_id]
            
            if action_type:
                query += " AND action_type = ?"
                params.append(action_type)
            
            if actor_id:
                query += " AND actor_id = ?"
                params.append(actor_id)
            
            if severity:
                query += " AND severity = ?"
                params.append(severity)
            
            if since:
                query += " AND timestamp >= ?"
                params.append(since.isoformat())
            
            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            
            logs = []
            for row in cursor.fetchall():
                logs.append({
                    'id': row[0],
                    'team_id': row[1],
                    'action_type': row[2],
                    'actor_id': row[3],
                    'actor_name': row[4],
                    'target_id': row[5],
                    'target_name': row[6],
                    'details': row[7],
                    'ip_address': row[8],
                    'timestamp': row[9],
                    'severity': row[10]
                })
            
            conn.close()
            
            debug("AuditLog", f"Found {len(logs)} log entries")
            return logs
            
        except Exception as e:
            exception("AuditLog", f"Error getting logs: {e}")
            return []
    
    def get_user_activity(
        self,
        actor_id: str,
        limit: int = 50,
        team_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Get activity logs for specific user
        
        Args:
            actor_id: User ID
            limit: Max number of logs
            team_id: Filter by team (optional)
            
        Returns:
            List of log entries
        """
        debug("AuditLog", f"Getting activity for user {actor_id[:8]}...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if team_id:
                cursor.execute("""
                    SELECT * FROM audit_log
                    WHERE actor_id = ? AND team_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (actor_id, team_id, limit))
            else:
                cursor.execute("""
                    SELECT * FROM audit_log
                    WHERE actor_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (actor_id, limit))
            
            logs = []
            for row in cursor.fetchall():
                logs.append({
                    'id': row[0],
                    'team_id': row[1],
                    'action_type': row[2],
                    'actor_id': row[3],
                    'actor_name': row[4],
                    'target_id': row[5],
                    'target_name': row[6],
                    'details': row[7],
                    'ip_address': row[8],
                    'timestamp': row[9],
                    'severity': row[10]
                })
            
            conn.close()
            
            debug("AuditLog", f"Found {len(logs)} activity entries")
            return logs
            
        except Exception as e:
            exception("AuditLog", f"Error getting user activity: {e}")
            return []
    
    def get_security_events(
        self,
        team_id: str,
        days: int = 7
    ) -> List[Dict]:
        """
        Get security-related events
        
        Args:
            team_id: Team ID
            days: Number of days to look back
            
        Returns:
            List of security events
        """
        debug("AuditLog", f"Getting security events for last {days} days")
        
        since = datetime.now() - timedelta(days=days)
        
        security_actions = [
            'permission_denied',
            'suspicious_activity',
            'member_removed',
            'role_changed'
        ]
        
        logs = []
        for action in security_actions:
            logs.extend(self.get_team_logs(
                team_id=team_id,
                action_type=action,
                since=since,
                limit=100
            ))
        
        # Sort by timestamp
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        info("AuditLog", f"Found {len(logs)} security events")
        return logs
    
    def cleanup_old_logs(self, days: int = 90) -> int:
        """
        Clean up logs older than specified days
        
        Args:
            days: Keep logs from last N days
            
        Returns:
            Number of logs deleted
        """
        debug("AuditLog", f"Cleaning up logs older than {days} days")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor.execute("""
                DELETE FROM audit_log
                WHERE timestamp < ?
            """, (cutoff,))
            
            deleted = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            info("AuditLog", f"Deleted {deleted} old log entries")
            return deleted
            
        except Exception as e:
            exception("AuditLog", f"Error cleaning up logs: {e}")
            return 0
    
    def get_action_description(self, action_type: str) -> str:
        """Get human-readable description of action"""
        return self.ACTIONS.get(action_type, action_type)
    
    def export_logs(
        self,
        team_id: str,
        output_file: str,
        since: Optional[datetime] = None
    ) -> bool:
        """
        Export logs to CSV file
        
        Args:
            team_id: Team ID
            output_file: Output file path
            since: Export logs since this date
            
        Returns:
            True if successful
        """
        debug("AuditLog", f"Exporting logs to {output_file}")
        
        try:
            import csv
            
            logs = self.get_team_logs(
                team_id=team_id,
                limit=10000,
                since=since
            )
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'timestamp', 'action_type', 'actor_name', 'target_name',
                    'details', 'severity'
                ])
                writer.writeheader()
                
                for log in logs:
                    writer.writerow({
                        'timestamp': log['timestamp'],
                        'action_type': self.get_action_description(log['action_type']),
                        'actor_name': log['actor_name'] or log['actor_id'],
                        'target_name': log['target_name'] or log.get('target_id', ''),
                        'details': log.get('details', ''),
                        'severity': log['severity']
                    })
            
            info("AuditLog", f"Exported {len(logs)} logs to {output_file}")
            return True
            
        except Exception as e:
            exception("AuditLog", f"Error exporting logs: {e}")
            return False

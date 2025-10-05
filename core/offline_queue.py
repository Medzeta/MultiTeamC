"""
Offline Message Queue
Sparar meddelanden när offline och skickar när online igen
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from core.debug_logger import debug, info, warning, error, exception


class OfflineQueue:
    """Queue för offline meddelanden"""
    
    def __init__(self, user_id: str):
        """
        Initialize offline queue
        
        Args:
            user_id: User ID för att separera queues
        """
        debug("OfflineQueue", f"Initializing offline queue for user: {user_id}")
        
        self.user_id = user_id
        self.db_path = Path(f"data/offline_queue_{user_id}.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._setup_database()
        
        info("OfflineQueue", "Offline queue initialized")
    
    def _setup_database(self):
        """Setup database for offline queue"""
        debug("OfflineQueue", "Setting up offline queue database")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS offline_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_type TEXT NOT NULL,
                    recipient_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    retry_count INTEGER DEFAULT 0,
                    last_retry TEXT,
                    status TEXT DEFAULT 'pending'
                )
            """)
            
            # File transfers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS offline_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipient_id TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    retry_count INTEGER DEFAULT 0,
                    last_retry TEXT,
                    status TEXT DEFAULT 'pending'
                )
            """)
            
            # Team actions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS offline_team_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    action_data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    retry_count INTEGER DEFAULT 0,
                    last_retry TEXT,
                    status TEXT DEFAULT 'pending'
                )
            """)
            
            conn.commit()
            conn.close()
            
            debug("OfflineQueue", "Database setup completed")
            
        except Exception as e:
            exception("OfflineQueue", f"Error setting up database: {e}")
    
    def add_message(
        self,
        message_type: str,
        recipient_id: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Add message to offline queue
        
        Args:
            message_type: Type of message (chat, team_chat, direct)
            recipient_id: Recipient ID (peer_id or team_id)
            content: Message content
            metadata: Optional metadata
            
        Returns:
            True if added successfully
        """
        debug("OfflineQueue", f"Adding message to queue: {message_type} -> {recipient_id[:8]}...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO offline_messages 
                (message_type, recipient_id, content, metadata, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                message_type,
                recipient_id,
                content,
                json.dumps(metadata) if metadata else None,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            info("OfflineQueue", f"Message added to queue: {message_type}")
            return True
            
        except Exception as e:
            exception("OfflineQueue", f"Error adding message to queue: {e}")
            return False
    
    def add_file(
        self,
        recipient_id: str,
        file_path: str,
        file_name: str,
        file_size: int
    ) -> bool:
        """
        Add file transfer to offline queue
        
        Args:
            recipient_id: Recipient ID
            file_path: Path to file
            file_name: File name
            file_size: File size in bytes
            
        Returns:
            True if added successfully
        """
        debug("OfflineQueue", f"Adding file to queue: {file_name} -> {recipient_id[:8]}...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO offline_files 
                (recipient_id, file_path, file_name, file_size, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                recipient_id,
                file_path,
                file_name,
                file_size,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            info("OfflineQueue", f"File added to queue: {file_name}")
            return True
            
        except Exception as e:
            exception("OfflineQueue", f"Error adding file to queue: {e}")
            return False
    
    def add_team_action(
        self,
        team_id: str,
        action_type: str,
        action_data: Dict
    ) -> bool:
        """
        Add team action to offline queue
        
        Args:
            team_id: Team ID
            action_type: Type of action (create, update, delete, invite, etc.)
            action_data: Action data
            
        Returns:
            True if added successfully
        """
        debug("OfflineQueue", f"Adding team action to queue: {action_type} for {team_id[:8]}...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO offline_team_actions 
                (team_id, action_type, action_data, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                team_id,
                action_type,
                json.dumps(action_data),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            info("OfflineQueue", f"Team action added to queue: {action_type}")
            return True
            
        except Exception as e:
            exception("OfflineQueue", f"Error adding team action to queue: {e}")
            return False
    
    def get_pending_messages(self) -> List[Dict]:
        """Get all pending messages"""
        debug("OfflineQueue", "Getting pending messages")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, message_type, recipient_id, content, metadata, created_at, retry_count
                FROM offline_messages
                WHERE status = 'pending'
                ORDER BY created_at ASC
            """)
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'id': row[0],
                    'message_type': row[1],
                    'recipient_id': row[2],
                    'content': row[3],
                    'metadata': json.loads(row[4]) if row[4] else None,
                    'created_at': row[5],
                    'retry_count': row[6]
                })
            
            conn.close()
            
            debug("OfflineQueue", f"Found {len(messages)} pending messages")
            return messages
            
        except Exception as e:
            exception("OfflineQueue", f"Error getting pending messages: {e}")
            return []
    
    def get_pending_files(self) -> List[Dict]:
        """Get all pending files"""
        debug("OfflineQueue", "Getting pending files")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, recipient_id, file_path, file_name, file_size, created_at, retry_count
                FROM offline_files
                WHERE status = 'pending'
                ORDER BY created_at ASC
            """)
            
            files = []
            for row in cursor.fetchall():
                files.append({
                    'id': row[0],
                    'recipient_id': row[1],
                    'file_path': row[2],
                    'file_name': row[3],
                    'file_size': row[4],
                    'created_at': row[5],
                    'retry_count': row[6]
                })
            
            conn.close()
            
            debug("OfflineQueue", f"Found {len(files)} pending files")
            return files
            
        except Exception as e:
            exception("OfflineQueue", f"Error getting pending files: {e}")
            return []
    
    def get_pending_team_actions(self) -> List[Dict]:
        """Get all pending team actions"""
        debug("OfflineQueue", "Getting pending team actions")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, team_id, action_type, action_data, created_at, retry_count
                FROM offline_team_actions
                WHERE status = 'pending'
                ORDER BY created_at ASC
            """)
            
            actions = []
            for row in cursor.fetchall():
                actions.append({
                    'id': row[0],
                    'team_id': row[1],
                    'action_type': row[2],
                    'action_data': json.loads(row[3]),
                    'created_at': row[4],
                    'retry_count': row[5]
                })
            
            conn.close()
            
            debug("OfflineQueue", f"Found {len(actions)} pending team actions")
            return actions
            
        except Exception as e:
            exception("OfflineQueue", f"Error getting pending team actions: {e}")
            return []
    
    def mark_message_sent(self, message_id: int) -> bool:
        """Mark message as sent"""
        debug("OfflineQueue", f"Marking message {message_id} as sent")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE offline_messages
                SET status = 'sent'
                WHERE id = ?
            """, (message_id,))
            
            conn.commit()
            conn.close()
            
            info("OfflineQueue", f"Message {message_id} marked as sent")
            return True
            
        except Exception as e:
            exception("OfflineQueue", f"Error marking message as sent: {e}")
            return False
    
    def mark_file_sent(self, file_id: int) -> bool:
        """Mark file as sent"""
        debug("OfflineQueue", f"Marking file {file_id} as sent")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE offline_files
                SET status = 'sent'
                WHERE id = ?
            """, (file_id,))
            
            conn.commit()
            conn.close()
            
            info("OfflineQueue", f"File {file_id} marked as sent")
            return True
            
        except Exception as e:
            exception("OfflineQueue", f"Error marking file as sent: {e}")
            return False
    
    def mark_team_action_sent(self, action_id: int) -> bool:
        """Mark team action as sent"""
        debug("OfflineQueue", f"Marking team action {action_id} as sent")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE offline_team_actions
                SET status = 'sent'
                WHERE id = ?
            """, (action_id,))
            
            conn.commit()
            conn.close()
            
            info("OfflineQueue", f"Team action {action_id} marked as sent")
            return True
            
        except Exception as e:
            exception("OfflineQueue", f"Error marking team action as sent: {e}")
            return False
    
    def increment_retry(self, table: str, item_id: int) -> bool:
        """Increment retry count"""
        debug("OfflineQueue", f"Incrementing retry count for {table} {item_id}")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(f"""
                UPDATE {table}
                SET retry_count = retry_count + 1,
                    last_retry = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), item_id))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            exception("OfflineQueue", f"Error incrementing retry count: {e}")
            return False
    
    def get_queue_stats(self) -> Dict:
        """Get queue statistics"""
        debug("OfflineQueue", "Getting queue statistics")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count pending messages
            cursor.execute("SELECT COUNT(*) FROM offline_messages WHERE status = 'pending'")
            pending_messages = cursor.fetchone()[0]
            
            # Count pending files
            cursor.execute("SELECT COUNT(*) FROM offline_files WHERE status = 'pending'")
            pending_files = cursor.fetchone()[0]
            
            # Count pending team actions
            cursor.execute("SELECT COUNT(*) FROM offline_team_actions WHERE status = 'pending'")
            pending_actions = cursor.fetchone()[0]
            
            conn.close()
            
            stats = {
                'pending_messages': pending_messages,
                'pending_files': pending_files,
                'pending_team_actions': pending_actions,
                'total_pending': pending_messages + pending_files + pending_actions
            }
            
            debug("OfflineQueue", f"Queue stats: {stats}")
            return stats
            
        except Exception as e:
            exception("OfflineQueue", f"Error getting queue stats: {e}")
            return {
                'pending_messages': 0,
                'pending_files': 0,
                'pending_team_actions': 0,
                'total_pending': 0
            }
    
    def clear_sent_items(self, older_than_days: int = 7) -> bool:
        """Clear sent items older than specified days"""
        info("OfflineQueue", f"Clearing sent items older than {older_than_days} days")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - older_than_days)
            
            # Delete old sent messages
            cursor.execute("""
                DELETE FROM offline_messages
                WHERE status = 'sent' AND created_at < ?
            """, (cutoff_date.isoformat(),))
            
            # Delete old sent files
            cursor.execute("""
                DELETE FROM offline_files
                WHERE status = 'sent' AND created_at < ?
            """, (cutoff_date.isoformat(),))
            
            # Delete old sent team actions
            cursor.execute("""
                DELETE FROM offline_team_actions
                WHERE status = 'sent' AND created_at < ?
            """, (cutoff_date.isoformat(),))
            
            conn.commit()
            conn.close()
            
            info("OfflineQueue", "Sent items cleared")
            return True
            
        except Exception as e:
            exception("OfflineQueue", f"Error clearing sent items: {e}")
            return False

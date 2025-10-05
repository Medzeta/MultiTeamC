"""
Read Receipts System
Tracking av lästa meddelanden i team chat
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from core.debug_logger import debug, info, warning, error, exception


class ReadReceipts:
    """System för read receipts"""
    
    def __init__(self, user_id: str):
        """
        Initialize read receipts system
        
        Args:
            user_id: Current user ID
        """
        debug("ReadReceipts", f"Initializing read receipts system for user: {user_id}")
        
        self.user_id = user_id
        self.db_path = Path(f"data/read_receipts_{user_id}.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._setup_database()
        
        info("ReadReceipts", "Read receipts system initialized")
    
    def _setup_database(self):
        """Setup database for read receipts"""
        debug("ReadReceipts", "Setting up read receipts database")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Read receipts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS read_receipts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_id TEXT NOT NULL,
                    message_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    read_at TEXT NOT NULL,
                    UNIQUE(team_id, message_id, user_id)
                )
            """)
            
            # Index for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_team_message 
                ON read_receipts(team_id, message_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_team_user 
                ON read_receipts(team_id, user_id)
            """)
            
            conn.commit()
            conn.close()
            
            debug("ReadReceipts", "Database setup completed")
            
        except Exception as e:
            exception("ReadReceipts", f"Error setting up database: {e}")
    
    def mark_as_read(self, team_id: str, message_id: str, user_id: Optional[str] = None) -> bool:
        """
        Mark message as read
        
        Args:
            team_id: Team ID
            message_id: Message ID
            user_id: User ID (defaults to current user)
            
        Returns:
            True if successful
        """
        if user_id is None:
            user_id = self.user_id
        
        debug("ReadReceipts", f"Marking message {message_id[:8]}... as read by {user_id[:8]}...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO read_receipts 
                (team_id, message_id, user_id, read_at)
                VALUES (?, ?, ?, ?)
            """, (team_id, message_id, user_id, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            info("ReadReceipts", f"Message {message_id[:8]}... marked as read")
            return True
            
        except Exception as e:
            exception("ReadReceipts", f"Error marking message as read: {e}")
            return False
    
    def get_read_count(self, team_id: str, message_id: str) -> int:
        """
        Get count of users who read the message
        
        Args:
            team_id: Team ID
            message_id: Message ID
            
        Returns:
            Number of users who read the message
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM read_receipts
                WHERE team_id = ? AND message_id = ?
            """, (team_id, message_id))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
            
        except Exception as e:
            exception("ReadReceipts", f"Error getting read count: {e}")
            return 0

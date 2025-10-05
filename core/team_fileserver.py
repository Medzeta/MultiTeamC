"""
Team File Server
Gemensam filserver för teams med full debug och notifikationer
"""

import sqlite3
import os
import shutil
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
from core.debug_logger import debug, info, warning, error, exception


class TeamFileServer:
    """Team file server system"""
    
    def __init__(self, team_id: str):
        """
        Initialize team file server
        
        Args:
            team_id: Team ID
        """
        debug("TeamFileServer", f"Initializing file server for team: {team_id}")
        
        self.team_id = team_id
        self.db_path = Path("data/fileserver.db")
        self.storage_path = Path(f"data/fileserver/{team_id}")
        
        # Create storage directory
        self.storage_path.mkdir(parents=True, exist_ok=True)
        debug("TeamFileServer", f"Storage path: {self.storage_path}")
        
        self._setup_database()
        
        info("TeamFileServer", f"File server initialized for team {team_id}")
    
    def _setup_database(self):
        """Setup file server database"""
        debug("TeamFileServer", "Setting up file server database")
        
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Files table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS team_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_id TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    file_type TEXT,
                    uploaded_by TEXT NOT NULL,
                    uploaded_at TEXT NOT NULL,
                    description TEXT,
                    downloads INTEGER DEFAULT 0,
                    UNIQUE(team_id, file_name)
                )
            """)
            
            # File versions table (for version control)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER NOT NULL,
                    version INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    uploaded_by TEXT NOT NULL,
                    uploaded_at TEXT NOT NULL,
                    FOREIGN KEY (file_id) REFERENCES team_files(id)
                )
            """)
            
            # File access log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_access_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER NOT NULL,
                    user_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (file_id) REFERENCES team_files(id)
                )
            """)
            
            conn.commit()
            conn.close()
            
            debug("TeamFileServer", "File server database setup complete")
            
        except Exception as e:
            exception("TeamFileServer", f"Database setup error: {e}")
            raise
    
    def upload_file(
        self,
        file_path: str,
        uploaded_by: str,
        description: str = ""
    ) -> Optional[int]:
        """
        Upload file to team file server
        
        Args:
            file_path: Path to file to upload
            uploaded_by: User ID who uploaded
            description: File description
            
        Returns:
            File ID if successful, None otherwise
        """
        debug("TeamFileServer", f"Uploading file: {file_path}")
        
        try:
            source_path = Path(file_path)
            
            if not source_path.exists():
                error("TeamFileServer", f"File not found: {file_path}")
                return None
            
            file_name = source_path.name
            file_size = source_path.stat().st_size
            file_type = source_path.suffix[1:] if source_path.suffix else "unknown"
            
            debug("TeamFileServer", f"File: {file_name}, Size: {file_size}, Type: {file_type}")
            
            # Copy file to storage
            dest_path = self.storage_path / file_name
            
            # Handle duplicate names
            counter = 1
            while dest_path.exists():
                stem = source_path.stem
                dest_path = self.storage_path / f"{stem}_{counter}{source_path.suffix}"
                counter += 1
            
            shutil.copy2(source_path, dest_path)
            debug("TeamFileServer", f"File copied to: {dest_path}")
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO team_files (
                    team_id, file_name, file_path, file_size, file_type,
                    uploaded_by, uploaded_at, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.team_id,
                dest_path.name,
                str(dest_path),
                file_size,
                file_type,
                uploaded_by,
                datetime.now().isoformat(),
                description
            ))
            
            file_id = cursor.lastrowid
            
            # Log access
            cursor.execute("""
                INSERT INTO file_access_log (file_id, user_id, action, timestamp)
                VALUES (?, ?, ?, ?)
            """, (file_id, uploaded_by, "upload", datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            info("TeamFileServer", f"File uploaded successfully: {file_name} (ID: {file_id})")
            return file_id
            
        except Exception as e:
            exception("TeamFileServer", f"Upload error: {e}")
            return None
    
    def get_files(self) -> List[Dict]:
        """
        Get all files for team
        
        Returns:
            List of file dicts
        """
        debug("TeamFileServer", f"Getting files for team: {self.team_id}")
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM team_files
                WHERE team_id = ?
                ORDER BY uploaded_at DESC
            """, (self.team_id,))
            
            files = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            debug("TeamFileServer", f"Found {len(files)} files")
            return files
            
        except Exception as e:
            exception("TeamFileServer", f"Error getting files: {e}")
            return []
    
    def download_file(self, file_id: int, user_id: str, dest_path: str) -> bool:
        """
        Download file from server
        
        Args:
            file_id: File ID
            user_id: User downloading
            dest_path: Destination path
            
        Returns:
            True if successful
        """
        debug("TeamFileServer", f"Downloading file ID: {file_id}")
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM team_files WHERE id = ?", (file_id,))
            file_row = cursor.fetchone()
            
            if not file_row:
                error("TeamFileServer", f"File not found: {file_id}")
                conn.close()
                return False
            
            file_dict = dict(file_row)
            source_path = Path(file_dict['file_path'])
            
            if not source_path.exists():
                error("TeamFileServer", f"File missing from storage: {source_path}")
                conn.close()
                return False
            
            # Copy file
            shutil.copy2(source_path, dest_path)
            debug("TeamFileServer", f"File copied to: {dest_path}")
            
            # Update download count
            cursor.execute("""
                UPDATE team_files SET downloads = downloads + 1
                WHERE id = ?
            """, (file_id,))
            
            # Log access
            cursor.execute("""
                INSERT INTO file_access_log (file_id, user_id, action, timestamp)
                VALUES (?, ?, ?, ?)
            """, (file_id, user_id, "download", datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            info("TeamFileServer", f"File downloaded: {file_dict['file_name']}")
            return True
            
        except Exception as e:
            exception("TeamFileServer", f"Download error: {e}")
            return False
    
    def delete_file(self, file_id: int, user_id: str) -> bool:
        """
        Delete file from server
        
        Args:
            file_id: File ID
            user_id: User deleting
            
        Returns:
            True if successful
        """
        debug("TeamFileServer", f"Deleting file ID: {file_id}")
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM team_files WHERE id = ?", (file_id,))
            file_row = cursor.fetchone()
            
            if not file_row:
                error("TeamFileServer", f"File not found: {file_id}")
                conn.close()
                return False
            
            file_dict = dict(file_row)
            file_path = Path(file_dict['file_path'])
            
            # Delete physical file
            if file_path.exists():
                file_path.unlink()
                debug("TeamFileServer", f"Physical file deleted: {file_path}")
            
            # Log access
            cursor.execute("""
                INSERT INTO file_access_log (file_id, user_id, action, timestamp)
                VALUES (?, ?, ?, ?)
            """, (file_id, user_id, "delete", datetime.now().isoformat()))
            
            # Delete from database
            cursor.execute("DELETE FROM team_files WHERE id = ?", (file_id,))
            
            conn.commit()
            conn.close()
            
            info("TeamFileServer", f"File deleted: {file_dict['file_name']}")
            return True
            
        except Exception as e:
            exception("TeamFileServer", f"Delete error: {e}")
            return False
    
    def get_file_info(self, file_id: int) -> Optional[Dict]:
        """
        Get file information
        
        Args:
            file_id: File ID
            
        Returns:
            File dict or None
        """
        debug("TeamFileServer", f"Getting file info: {file_id}")
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM team_files WHERE id = ?", (file_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            exception("TeamFileServer", f"Error getting file info: {e}")
            return None
    
    def get_storage_stats(self) -> Dict:
        """
        Get storage statistics
        
        Returns:
            Dict with stats
        """
        debug("TeamFileServer", "Getting storage stats")
        
        try:
            files = self.get_files()
            
            total_size = sum(f['file_size'] for f in files)
            total_downloads = sum(f['downloads'] for f in files)
            
            # Count by type
            by_type = {}
            for f in files:
                file_type = f['file_type']
                by_type[file_type] = by_type.get(file_type, 0) + 1
            
            stats = {
                'total_files': len(files),
                'total_size': total_size,
                'total_downloads': total_downloads,
                'by_type': by_type
            }
            
            debug("TeamFileServer", f"Stats: {stats}")
            return stats
            
        except Exception as e:
            exception("TeamFileServer", f"Error getting stats: {e}")
            return {
                'total_files': 0,
                'total_size': 0,
                'total_downloads': 0,
                'by_type': {}
            }


if __name__ == "__main__":
    # Test file server
    info("TEST", "Testing TeamFileServer...")
    
    test_team_id = "test_team_123"
    fs = TeamFileServer(test_team_id)
    
    print(f"\n✅ File server initialized for team: {test_team_id}")
    
    # Get stats
    stats = fs.get_storage_stats()
    print(f"\nStorage stats: {stats}")
    
    print("\n✅ Team file server working!")

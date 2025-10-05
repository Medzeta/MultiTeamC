"""
Task Manager System
Delad uppgiftslista för teams
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from core.debug_logger import debug, info, warning, error, exception


class TaskManager:
    """System för task management"""
    
    def __init__(self, team_id: str):
        """
        Initialize task manager
        
        Args:
            team_id: Team ID
        """
        debug("TaskManager", f"Initializing task manager for team: {team_id}")
        
        self.team_id = team_id
        self.db_path = Path(f"data/tasks_{team_id}.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._setup_database()
        
        info("TaskManager", "Task manager initialized")
    
    def _setup_database(self):
        """Setup database for tasks"""
        debug("TaskManager", "Setting up tasks database")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    priority TEXT DEFAULT 'medium',
                    assigned_to TEXT,
                    created_by TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    due_date TEXT,
                    completed_at TEXT,
                    tags TEXT
                )
            """)
            
            # Index for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status 
                ON tasks(status)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_assigned 
                ON tasks(assigned_to)
            """)
            
            conn.commit()
            conn.close()
            
            debug("TaskManager", "Database setup completed")
            
        except Exception as e:
            exception("TaskManager", f"Error setting up database: {e}")
    
    def create_task(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        assigned_to: Optional[str] = None,
        created_by: str = "",
        due_date: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[int]:
        """
        Create new task
        
        Args:
            title: Task title
            description: Task description
            priority: Priority (low, medium, high, urgent)
            assigned_to: User ID assigned to
            created_by: Creator user ID
            due_date: Due date (ISO format)
            tags: List of tags
            
        Returns:
            Task ID if successful
        """
        debug("TaskManager", f"Creating task: {title}")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            tags_str = ",".join(tags) if tags else ""
            
            cursor.execute("""
                INSERT INTO tasks 
                (title, description, priority, assigned_to, created_by, created_at, due_date, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                title,
                description,
                priority,
                assigned_to,
                created_by,
                datetime.now().isoformat(),
                due_date,
                tags_str
            ))
            
            task_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            info("TaskManager", f"Task created: {task_id}")
            return task_id
            
        except Exception as e:
            exception("TaskManager", f"Error creating task: {e}")
            return None
    
    def get_tasks(
        self,
        status: Optional[str] = None,
        assigned_to: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[Dict]:
        """
        Get tasks with optional filters
        
        Args:
            status: Filter by status
            assigned_to: Filter by assigned user
            priority: Filter by priority
            
        Returns:
            List of task dicts
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM tasks WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            if assigned_to:
                query += " AND assigned_to = ?"
                params.append(assigned_to)
            
            if priority:
                query += " AND priority = ?"
                params.append(priority)
            
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            
            columns = [desc[0] for desc in cursor.description]
            tasks = []
            
            for row in cursor.fetchall():
                task = dict(zip(columns, row))
                # Parse tags
                if task['tags']:
                    task['tags'] = task['tags'].split(',')
                else:
                    task['tags'] = []
                tasks.append(task)
            
            conn.close()
            
            return tasks
            
        except Exception as e:
            exception("TaskManager", f"Error getting tasks: {e}")
            return []
    
    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        due_date: Optional[str] = None
    ) -> bool:
        """
        Update task
        
        Args:
            task_id: Task ID
            title: New title
            description: New description
            status: New status
            priority: New priority
            assigned_to: New assigned user
            due_date: New due date
            
        Returns:
            True if successful
        """
        debug("TaskManager", f"Updating task: {task_id}")
        
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
            
            if status is not None:
                updates.append("status = ?")
                params.append(status)
                
                # If marking as completed, set completed_at
                if status == "completed":
                    updates.append("completed_at = ?")
                    params.append(datetime.now().isoformat())
            
            if priority is not None:
                updates.append("priority = ?")
                params.append(priority)
            
            if assigned_to is not None:
                updates.append("assigned_to = ?")
                params.append(assigned_to)
            
            if due_date is not None:
                updates.append("due_date = ?")
                params.append(due_date)
            
            if not updates:
                warning("TaskManager", "No updates provided")
                conn.close()
                return False
            
            params.append(task_id)
            
            query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            
            conn.commit()
            conn.close()
            
            info("TaskManager", f"Task updated: {task_id}")
            return True
            
        except Exception as e:
            exception("TaskManager", f"Error updating task: {e}")
            return False
    
    def delete_task(self, task_id: int) -> bool:
        """
        Delete task
        
        Args:
            task_id: Task ID
            
        Returns:
            True if successful
        """
        debug("TaskManager", f"Deleting task: {task_id}")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            
            conn.commit()
            conn.close()
            
            info("TaskManager", f"Task deleted: {task_id}")
            return True
            
        except Exception as e:
            exception("TaskManager", f"Error deleting task: {e}")
            return False
    
    def get_task_stats(self) -> Dict:
        """
        Get task statistics
        
        Returns:
            Dict with stats
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total tasks
            cursor.execute("SELECT COUNT(*) FROM tasks")
            total = cursor.fetchone()[0]
            
            # By status
            cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
            by_status = dict(cursor.fetchall())
            
            # By priority
            cursor.execute("SELECT priority, COUNT(*) FROM tasks GROUP BY priority")
            by_priority = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'total': total,
                'by_status': by_status,
                'by_priority': by_priority
            }
            
        except Exception as e:
            exception("TaskManager", f"Error getting stats: {e}")
            return {'total': 0, 'by_status': {}, 'by_priority': {}}

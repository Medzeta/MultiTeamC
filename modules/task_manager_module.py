"""
Task Manager Module
UI för delad uppgiftslista i teams
"""

import customtkinter as ctk
from typing import Callable, Optional, List, Dict
from datetime import datetime
from core.debug_logger import debug, info, warning, error
from core.ui_components import (
    CustomButton, CustomLabel, CustomFrame, CustomEntry, MessageBox
)
from core.task_manager import TaskManager


class TaskManagerModule(ctk.CTkFrame):
    """Task manager module för teams"""
    
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
        Initialize task manager module
        
        Args:
            master: Parent widget
            team_id: Team ID
            team_name: Team name
            current_user_id: Current user ID
            on_back: Callback for back button
        """
        debug("TaskManagerModule", f"Initializing task manager for team: {team_name}")
        
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.team_id = team_id
        self.team_name = team_name
        self.current_user_id = current_user_id
        self.on_back = on_back
        
        self.task_manager = TaskManager(team_id)
        self.tasks = []
        
        self._create_ui()
        self._load_tasks()
        
        info("TaskManagerModule", "Task manager module initialized")
    
    def _create_ui(self):
        """Create task manager UI"""
        debug("TaskManagerModule", "Creating task manager UI")
        
        # Header
        header = CustomFrame(self, transparent=True)
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        CustomLabel(
            header,
            text=f"📋 Tasks - {self.team_name}",
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
        
        # Add task section
        add_frame = CustomFrame(self, transparent=False)
        add_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        add_container = CustomFrame(add_frame, transparent=True)
        add_container.pack(fill="x", padx=15, pady=15)
        
        CustomLabel(
            add_container,
            text="➕ New Task",
            size=14,
            bold=True
        ).pack(anchor="w", pady=(0, 10))
        
        # Task input row
        input_row = CustomFrame(add_container, transparent=True)
        input_row.pack(fill="x", pady=(0, 10))
        
        self.task_title_entry = ctk.CTkEntry(
            input_row,
            placeholder_text="Task title...",
            height=35
        )
        self.task_title_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Set focus after a short delay
        self.after(100, lambda: self.task_title_entry.focus())
        
        # Priority dropdown
        self.priority_var = ctk.StringVar(value="medium")
        priority_menu = ctk.CTkOptionMenu(
            input_row,
            values=["low", "medium", "high", "urgent"],
            variable=self.priority_var,
            width=120
        )
        priority_menu.pack(side="left", padx=(0, 10))
        
        CustomButton(
            input_row,
            text="Add Task",
            command=self._add_task,
            style="primary",
            width=100
        ).pack(side="left")
        
        # Filter section
        filter_frame = CustomFrame(self, transparent=True)
        filter_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        CustomLabel(
            filter_frame,
            text="Filter:",
            size=12
        ).pack(side="left", padx=(0, 10))
        
        self.filter_var = ctk.StringVar(value="all")
        
        for filter_name, filter_value in [("All", "all"), ("Pending", "pending"), 
                                          ("In Progress", "in_progress"), ("Completed", "completed")]:
            ctk.CTkRadioButton(
                filter_frame,
                text=filter_name,
                variable=self.filter_var,
                value=filter_value,
                command=self._load_tasks
            ).pack(side="left", padx=5)
        
        # Tasks list
        tasks_container = CustomFrame(self, transparent=False)
        tasks_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Fixed frame for tasks (no scrollbar)
        self.tasks_scroll = CustomFrame(tasks_container, transparent=True)
        self.tasks_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        debug("TaskManagerModule", "Task manager UI created")
    
    def _add_task(self):
        """Add new task"""
        title = self.task_title_entry.get().strip()
        
        if not title:
            MessageBox.show_error(self, "Error", "Please enter a task title")
            return
        
        priority = self.priority_var.get()
        
        debug("TaskManagerModule", f"Adding task: {title} (priority: {priority})")
        
        task_id = self.task_manager.create_task(
            title=title,
            priority=priority,
            created_by=self.current_user_id
        )
        
        if task_id:
            info("TaskManagerModule", f"Task created: {task_id}")
            self.task_title_entry.delete(0, "end")
            self._load_tasks()
        else:
            error("TaskManagerModule", "Failed to create task")
            MessageBox.show_error(self, "Error", "Failed to create task")
    
    def _load_tasks(self):
        """Load and display tasks"""
        debug("TaskManagerModule", "Loading tasks")
        
        # Get filter
        filter_status = self.filter_var.get()
        status_filter = None if filter_status == "all" else filter_status
        
        # Load tasks
        self.tasks = self.task_manager.get_tasks(status=status_filter)
        
        # Clear existing tasks
        for widget in self.tasks_scroll.winfo_children():
            widget.destroy()
        
        if not self.tasks:
            CustomLabel(
                self.tasks_scroll,
                text="📝 No tasks yet. Create your first task above!",
                size=12,
                color=("#888888", "#888888")
            ).pack(pady=50)
            return
        
        # Display tasks
        for task in self.tasks:
            self._create_task_card(task)
        
        info("TaskManagerModule", f"Loaded {len(self.tasks)} tasks")
    
    def _create_task_card(self, task: Dict):
        """Create task card widget"""
        # Task card
        card = CustomFrame(self.tasks_scroll, transparent=False)
        card.pack(fill="x", pady=5)
        
        content = CustomFrame(card, transparent=True)
        content.pack(fill="x", padx=15, pady=10)
        
        # Header row
        header_row = CustomFrame(content, transparent=True)
        header_row.pack(fill="x", pady=(0, 5))
        
        # Priority indicator
        priority_colors = {
            "low": "#4CAF50",
            "medium": "#2196F3",
            "high": "#FF9800",
            "urgent": "#F44336"
        }
        priority_color = priority_colors.get(task['priority'], "#888888")
        
        priority_label = CustomLabel(
            header_row,
            text=f"● {task['priority'].upper()}",
            size=10,
            bold=True,
            color=(priority_color, priority_color)
        )
        priority_label.pack(side="left", padx=(0, 10))
        
        # Status
        status_label = CustomLabel(
            header_row,
            text=f"[{task['status'].replace('_', ' ').title()}]",
            size=10,
            color=("#666666", "#999999")
        )
        status_label.pack(side="left")
        
        # Task title
        title_label = CustomLabel(
            content,
            text=task['title'],
            size=13,
            bold=True
        )
        title_label.pack(anchor="w", pady=(0, 5))
        
        # Description if exists
        if task.get('description'):
            desc_label = CustomLabel(
                content,
                text=task['description'],
                size=11,
                color=("#666666", "#999999")
            )
            desc_label.pack(anchor="w", pady=(0, 5))
        
        # Actions row
        actions_row = CustomFrame(content, transparent=True)
        actions_row.pack(fill="x", pady=(5, 0))
        
        # Status buttons
        if task['status'] == 'pending':
            CustomButton(
                actions_row,
                text="Start",
                command=lambda t=task: self._update_task_status(t['id'], 'in_progress'),
                style="primary",
                width=80,
                height=30
            ).pack(side="left", padx=(0, 5))
        
        if task['status'] == 'in_progress':
            CustomButton(
                actions_row,
                text="Complete",
                command=lambda t=task: self._update_task_status(t['id'], 'completed'),
                style="success",
                width=100,
                height=30
            ).pack(side="left", padx=(0, 5))
        
        if task['status'] == 'completed':
            CustomLabel(
                actions_row,
                text="✓ Completed",
                size=11,
                color=("#4CAF50", "#4CAF50"),
                bold=True
            ).pack(side="left", padx=(0, 10))
        
        # Delete button
        CustomButton(
            actions_row,
            text="🗑️",
            command=lambda t=task: self._delete_task(t['id']),
            style="secondary",
            width=40,
            height=30
        ).pack(side="right")
    
    def _update_task_status(self, task_id: int, new_status: str):
        """Update task status"""
        debug("TaskManagerModule", f"Updating task {task_id} to {new_status}")
        
        success = self.task_manager.update_task(task_id, status=new_status)
        
        if success:
            info("TaskManagerModule", f"Task {task_id} updated")
            self._load_tasks()
        else:
            error("TaskManagerModule", f"Failed to update task {task_id}")
    
    def _delete_task(self, task_id: int):
        """Delete task"""
        debug("TaskManagerModule", f"Deleting task: {task_id}")
        
        success = self.task_manager.delete_task(task_id)
        
        if success:
            info("TaskManagerModule", f"Task {task_id} deleted")
            self._load_tasks()
        else:
            error("TaskManagerModule", f"Failed to delete task {task_id}")

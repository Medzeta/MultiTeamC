"""
Audit Log Viewer Module
UI för att visa och exportera audit logs
"""

import customtkinter as ctk
from typing import Callable, Optional, List, Dict
from datetime import datetime, timedelta
from core.debug_logger import debug, info, warning, error
from core.ui_components import (
    CustomButton, CustomLabel, CustomFrame, CustomEntry, MessageBox
)
from core.audit_log import AuditLog


class AuditLogViewerModule(ctk.CTkFrame):
    """Audit log viewer module"""
    
    ACTION_COLORS = {
        'team_created': "#4CAF50",
        'member_added': "#2196F3",
        'member_removed': "#F44336",
        'role_changed': "#FF9800",
        'message_sent': "#9C27B0",
        'file_shared': "#00BCD4",
        'settings_changed': "#FFC107"
    }
    
    SEVERITY_COLORS = {
        'info': "#2196F3",
        'warning': "#FF9800",
        'error': "#F44336",
        'critical': "#D32F2F"
    }
    
    def __init__(
        self,
        master,
        team_id: str,
        team_name: str,
        on_back: Callable = None,
        **kwargs
    ):
        """
        Initialize audit log viewer
        
        Args:
            master: Parent widget
            team_id: Team ID
            team_name: Team name
            on_back: Callback for back button
        """
        debug("AuditLogViewer", f"Initializing audit log viewer for team: {team_name}")
        
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.team_id = team_id
        self.team_name = team_name
        self.on_back = on_back
        
        self.audit_log = AuditLog(team_id)
        self.logs = []
        
        self._create_ui()
        self._load_logs()
        
        info("AuditLogViewer", "Audit log viewer initialized")
    
    def _create_ui(self):
        """Create audit log viewer UI"""
        debug("AuditLogViewer", "Creating audit log viewer UI")
        
        # Header
        header = CustomFrame(self, transparent=True)
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        CustomLabel(
            header,
            text=f"📋 Audit Log - {self.team_name}",
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
        
        # Filter section
        filter_frame = CustomFrame(self, transparent=False)
        filter_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        filter_container = CustomFrame(filter_frame, transparent=True)
        filter_container.pack(fill="x", padx=15, pady=15)
        
        CustomLabel(
            filter_container,
            text="🔍 Filters",
            size=14,
            bold=True
        ).pack(anchor="w", pady=(0, 10))
        
        # Filter row
        filter_row = CustomFrame(filter_container, transparent=True)
        filter_row.pack(fill="x")
        
        # Time filter
        CustomLabel(
            filter_row,
            text="Time:",
            size=11
        ).pack(side="left", padx=(0, 5))
        
        self.time_filter_var = ctk.StringVar(value="all")
        time_filter = ctk.CTkOptionMenu(
            filter_row,
            values=["All Time", "Last Hour", "Last 24 Hours", "Last 7 Days", "Last 30 Days"],
            variable=self.time_filter_var,
            command=lambda _: self._load_logs(),
            width=150
        )
        time_filter.pack(side="left", padx=(0, 20))
        
        # Action filter
        CustomLabel(
            filter_row,
            text="Action:",
            size=11
        ).pack(side="left", padx=(0, 5))
        
        self.action_filter_var = ctk.StringVar(value="all")
        action_filter = ctk.CTkOptionMenu(
            filter_row,
            values=["All Actions", "Team", "Members", "Messages", "Files", "Settings"],
            variable=self.action_filter_var,
            command=lambda _: self._load_logs(),
            width=150
        )
        action_filter.pack(side="left", padx=(0, 20))
        
        # Export button
        CustomButton(
            filter_row,
            text="📥 Export CSV",
            command=self._export_logs,
            style="success",
            width=120
        ).pack(side="right")
        
        # Stats
        stats_frame = CustomFrame(self, transparent=False)
        stats_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        stats_container = CustomFrame(stats_frame, transparent=True)
        stats_container.pack(fill="x", padx=15, pady=10)
        
        self.stats_label = CustomLabel(
            stats_container,
            text="📊 Loading statistics...",
            size=11,
            color=("#666666", "#999999")
        )
        self.stats_label.pack(anchor="w")
        
        # Logs list
        logs_container = CustomFrame(self, transparent=False)
        logs_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Scrollable frame for logs
        self.logs_scroll = ctk.CTkScrollableFrame(
            logs_container,
            fg_color="transparent"
        )
        self.logs_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        debug("AuditLogViewer", "Audit log viewer UI created")
    
    def _load_logs(self):
        """Load and display audit logs"""
        debug("AuditLogViewer", "Loading audit logs")
        
        # Get time filter
        time_filter = self.time_filter_var.get()
        start_time = None
        
        if time_filter == "Last Hour":
            start_time = (datetime.now() - timedelta(hours=1)).isoformat()
        elif time_filter == "Last 24 Hours":
            start_time = (datetime.now() - timedelta(days=1)).isoformat()
        elif time_filter == "Last 7 Days":
            start_time = (datetime.now() - timedelta(days=7)).isoformat()
        elif time_filter == "Last 30 Days":
            start_time = (datetime.now() - timedelta(days=30)).isoformat()
        
        # Get action filter
        action_filter = self.action_filter_var.get()
        action_type = None
        
        if action_filter == "Team":
            action_type = "team_"
        elif action_filter == "Members":
            action_type = "member_"
        elif action_filter == "Messages":
            action_type = "message_"
        elif action_filter == "Files":
            action_type = "file_"
        elif action_filter == "Settings":
            action_type = "settings_"
        
        # Load logs
        self.logs = self.audit_log.query_logs(
            start_time=start_time,
            action_type=action_type
        )
        
        # Update stats
        stats = self.audit_log.get_stats()
        total = stats.get('total', 0)
        by_action = stats.get('by_action', {})
        
        stats_text = f"📊 Total: {total} events"
        if by_action:
            top_actions = sorted(by_action.items(), key=lambda x: x[1], reverse=True)[:3]
            stats_text += " | Top: " + ", ".join([f"{a}: {c}" for a, c in top_actions])
        
        self.stats_label.configure(text=stats_text)
        
        # Clear existing logs
        for widget in self.logs_scroll.winfo_children():
            widget.destroy()
        
        if not self.logs:
            CustomLabel(
                self.logs_scroll,
                text="📋 No audit logs found for selected filters",
                size=12,
                color=("#888888", "#888888")
            ).pack(pady=50)
            return
        
        # Display logs (newest first)
        for log in reversed(self.logs):
            self._create_log_card(log)
        
        info("AuditLogViewer", f"Loaded {len(self.logs)} audit logs")
    
    def _create_log_card(self, log: Dict):
        """Create log entry card widget"""
        # Log card
        card = CustomFrame(self.logs_scroll, transparent=False)
        card.pack(fill="x", pady=3)
        
        content = CustomFrame(card, transparent=True)
        content.pack(fill="x", padx=15, pady=8)
        
        # Header row
        header_row = CustomFrame(content, transparent=True)
        header_row.pack(fill="x")
        
        # Severity indicator
        severity = log.get('severity', 'info')
        severity_color = self.SEVERITY_COLORS.get(severity, "#888888")
        
        severity_label = CustomLabel(
            header_row,
            text=f"● {severity.upper()}",
            size=9,
            bold=True,
            color=(severity_color, severity_color)
        )
        severity_label.pack(side="left", padx=(0, 10))
        
        # Timestamp
        timestamp = log.get('timestamp', '')
        try:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            time_str = timestamp
        
        time_label = CustomLabel(
            header_row,
            text=time_str,
            size=10,
            color=("#666666", "#999999")
        )
        time_label.pack(side="left", padx=(0, 10))
        
        # Action type
        action = log.get('action', 'unknown')
        action_color = self.ACTION_COLORS.get(action, "#888888")
        
        action_label = CustomLabel(
            header_row,
            text=action.replace('_', ' ').title(),
            size=10,
            bold=True,
            color=(action_color, action_color)
        )
        action_label.pack(side="left")
        
        # User ID
        user_id = log.get('user_id', 'unknown')
        user_label = CustomLabel(
            header_row,
            text=f"User: {user_id}",
            size=9,
            color=("#666666", "#999999")
        )
        user_label.pack(side="right")
        
        # Details
        details = log.get('details', '')
        if details:
            details_label = CustomLabel(
                content,
                text=details,
                size=10,
                color=("#444444", "#AAAAAA")
            )
            details_label.pack(anchor="w", pady=(5, 0))
    
    def _export_logs(self):
        """Export logs to CSV"""
        debug("AuditLogViewer", "Exporting logs to CSV")
        
        filename = f"audit_log_{self.team_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        success = self.audit_log.export_to_csv(filename)
        
        if success:
            info("AuditLogViewer", f"Logs exported to: {filename}")
            MessageBox.show_success(
                self,
                "Export Successful",
                f"Audit logs exported to:\n{filename}"
            )
        else:
            error("AuditLogViewer", "Failed to export logs")
            MessageBox.show_error(self, "Export Failed", "Failed to export audit logs")

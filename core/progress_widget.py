"""
Progress Widget
UI widget för att visa file transfer progress
"""

import customtkinter as ctk
from typing import Callable, Optional
from core.debug_logger import debug, info
from core.ui_components import CustomFrame, CustomLabel, CustomButton


class ProgressWidget(ctk.CTkFrame):
    """Progress bar widget för file transfers"""
    
    def __init__(
        self,
        master,
        transfer_id: str,
        file_name: str,
        file_size: int,
        direction: str = 'upload',
        on_cancel: Optional[Callable] = None,
        **kwargs
    ):
        """
        Initialize progress widget
        
        Args:
            master: Parent widget
            transfer_id: Transfer ID
            file_name: File name
            file_size: File size in bytes
            direction: 'upload' or 'download'
            on_cancel: Callback for cancel button
        """
        debug("ProgressWidget", f"Creating progress widget: {file_name}")
        
        super().__init__(
            master,
            fg_color=("#3b3b3b", "#2b2b2b"),
            corner_radius=8,
            **kwargs
        )
        
        self.transfer_id = transfer_id
        self.file_name = file_name
        self.file_size = file_size
        self.direction = direction
        self.on_cancel_callback = on_cancel
        
        self._create_ui()
        
        info("ProgressWidget", f"Progress widget created: {transfer_id[:8]}...")
    
    def _create_ui(self):
        """Create progress UI"""
        debug("ProgressWidget", "Creating progress UI")
        
        # Main container
        container = CustomFrame(self, transparent=True)
        container.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Top row: File name and cancel button
        top_row = CustomFrame(container, transparent=True)
        top_row.pack(fill="x", pady=(0, 5))
        
        # Direction icon
        icon = "⬆️" if self.direction == 'upload' else "⬇️"
        CustomLabel(
            top_row,
            text=icon,
            size=14
        ).pack(side="left", padx=(0, 5))
        
        # File name
        self.name_label = CustomLabel(
            top_row,
            text=self.file_name,
            size=11,
            bold=True
        )
        self.name_label.pack(side="left", fill="x", expand=True)
        
        # Cancel button
        if self.on_cancel_callback:
            cancel_btn = CustomButton(
                top_row,
                text="✕",
                command=self._on_cancel,
                width=25,
                height=25,
                style="secondary"
            )
            cancel_btn.pack(side="right")
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            container,
            height=8,
            corner_radius=4,
            fg_color=("#2b2b2b", "#1a1a1a"),
            progress_color=("#1f6aa5", "#4da6ff")
        )
        self.progress_bar.pack(fill="x", pady=(0, 5))
        self.progress_bar.set(0)
        
        # Bottom row: Stats
        stats_row = CustomFrame(container, transparent=True)
        stats_row.pack(fill="x")
        
        # Progress text
        self.progress_label = CustomLabel(
            stats_row,
            text="0%",
            size=9,
            color=("#888888", "#888888")
        )
        self.progress_label.pack(side="left")
        
        # Speed
        self.speed_label = CustomLabel(
            stats_row,
            text="",
            size=9,
            color=("#888888", "#888888")
        )
        self.speed_label.pack(side="left", padx=(10, 0))
        
        # ETA
        self.eta_label = CustomLabel(
            stats_row,
            text="",
            size=9,
            color=("#888888", "#888888")
        )
        self.eta_label.pack(side="right")
        
        debug("ProgressWidget", "Progress UI created")
    
    def update_progress(self, progress_data: dict):
        """
        Update progress display
        
        Args:
            progress_data: Progress data dict
        """
        debug("ProgressWidget", f"Updating progress: {progress_data.get('progress_percent', 0):.1f}%")
        
        # Update progress bar
        progress = progress_data.get('progress_percent', 0) / 100
        self.progress_bar.set(progress)
        
        # Update progress text
        self.progress_label.configure(
            text=f"{progress_data.get('progress_percent', 0):.1f}%"
        )
        
        # Update speed
        speed_bps = progress_data.get('speed_bps', 0)
        if speed_bps > 0:
            speed_text = self._format_speed(speed_bps)
            self.speed_label.configure(text=speed_text)
        
        # Update ETA
        eta_seconds = progress_data.get('eta_seconds', 0)
        if eta_seconds > 0:
            eta_text = f"ETA: {self._format_time(eta_seconds)}"
            self.eta_label.configure(text=eta_text)
    
    def mark_complete(self):
        """Mark transfer as complete"""
        debug("ProgressWidget", "Marking as complete")
        
        self.progress_bar.set(1.0)
        self.progress_label.configure(text="100% - Complete!")
        self.speed_label.configure(text="")
        self.eta_label.configure(text="✓ Done")
        
        # Change color to green
        self.progress_bar.configure(progress_color=("#107c10", "#0d5e0d"))
        
        info("ProgressWidget", "Marked as complete")
    
    def mark_failed(self, error_message: str = ""):
        """Mark transfer as failed"""
        debug("ProgressWidget", f"Marking as failed: {error_message}")
        
        self.progress_label.configure(text="Failed")
        self.speed_label.configure(text="")
        self.eta_label.configure(text="✗ Error")
        
        # Change color to red
        self.progress_bar.configure(progress_color=("#c42b1c", "#a52318"))
        
        info("ProgressWidget", "Marked as failed")
    
    def _on_cancel(self):
        """Handle cancel button"""
        debug("ProgressWidget", "Cancel button clicked")
        
        if self.on_cancel_callback:
            self.on_cancel_callback(self.transfer_id)
    
    def _format_size(self, bytes_size: int) -> str:
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"
    
    def _format_speed(self, bps: float) -> str:
        """Format speed"""
        return f"{self._format_size(int(bps))}/s"
    
    def _format_time(self, seconds: float) -> str:
        """Format time"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"


class ProgressContainer(ctk.CTkFrame):
    """Container för multiple progress widgets"""
    
    def __init__(self, master, **kwargs):
        """Initialize progress container"""
        debug("ProgressContainer", "Creating progress container")
        
        super().__init__(
            master,
            fg_color="transparent",
            **kwargs
        )
        
        self.widgets = {}  # transfer_id -> widget
        
        # Scrollable frame for progress widgets
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_fg_color=("#2b2b2b", "#2b2b2b"),
            scrollbar_button_color=("#3b3b3b", "#3b3b3b"),
            height=200
        )
        self.scroll_frame.pack(fill="both", expand=True)
        
        info("ProgressContainer", "Progress container created")
    
    def add_transfer(
        self,
        transfer_id: str,
        file_name: str,
        file_size: int,
        direction: str = 'upload',
        on_cancel: Optional[Callable] = None
    ):
        """Add a transfer to container"""
        debug("ProgressContainer", f"Adding transfer: {file_name}")
        
        widget = ProgressWidget(
            self.scroll_frame,
            transfer_id=transfer_id,
            file_name=file_name,
            file_size=file_size,
            direction=direction,
            on_cancel=on_cancel
        )
        widget.pack(fill="x", pady=5)
        
        self.widgets[transfer_id] = widget
        
        info("ProgressContainer", f"Transfer added: {transfer_id[:8]}...")
    
    def update_transfer(self, transfer_id: str, progress_data: dict):
        """Update transfer progress"""
        if transfer_id in self.widgets:
            self.widgets[transfer_id].update_progress(progress_data)
    
    def complete_transfer(self, transfer_id: str):
        """Mark transfer as complete"""
        if transfer_id in self.widgets:
            self.widgets[transfer_id].mark_complete()
    
    def fail_transfer(self, transfer_id: str, error_message: str = ""):
        """Mark transfer as failed"""
        if transfer_id in self.widgets:
            self.widgets[transfer_id].mark_failed(error_message)
    
    def remove_transfer(self, transfer_id: str):
        """Remove transfer from container"""
        debug("ProgressContainer", f"Removing transfer: {transfer_id[:8]}...")
        
        if transfer_id in self.widgets:
            self.widgets[transfer_id].destroy()
            del self.widgets[transfer_id]
            
            info("ProgressContainer", f"Transfer removed: {transfer_id[:8]}...")

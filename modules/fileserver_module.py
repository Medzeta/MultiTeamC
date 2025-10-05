"""
File Server Module
UI för team filserver med live notifikationer
"""

import customtkinter as ctk
from typing import Callable, Optional, List, Dict
from pathlib import Path
from datetime import datetime
from tkinter import filedialog
from core.debug_logger import debug, info, warning, error
from core.ui_components import (
    CustomButton, CustomLabel, CustomFrame, MessageBox
)
from core.team_fileserver import TeamFileServer


class FileServerModule(ctk.CTkFrame):
    """File server module för teams"""
    
    FILE_TYPE_ICONS = {
        'pdf': '📄',
        'doc': '📝', 'docx': '📝',
        'xls': '📊', 'xlsx': '📊',
        'ppt': '📊', 'pptx': '📊',
        'txt': '📃',
        'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️',
        'mp4': '🎬', 'avi': '🎬', 'mov': '🎬',
        'mp3': '🎵', 'wav': '🎵',
        'zip': '📦', 'rar': '📦', '7z': '📦',
        'py': '🐍', 'js': '📜', 'html': '🌐',
        'unknown': '📁'
    }
    
    def __init__(
        self,
        master,
        team_id: str,
        team_name: str,
        current_user_id: str,
        notification_system=None,
        sound_system=None,
        on_back: Callable = None,
        **kwargs
    ):
        """
        Initialize file server module
        
        Args:
            master: Parent widget
            team_id: Team ID
            team_name: Team name
            current_user_id: Current user ID
            notification_system: Notification system for desktop notifications
            sound_system: Sound system for audio notifications
            on_back: Callback for back button
        """
        debug("FileServerModule", f"Initializing file server for team: {team_name}")
        
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.team_id = team_id
        self.team_name = team_name
        self.current_user_id = current_user_id
        self.notification_system = notification_system
        self.sound_system = sound_system
        self.on_back = on_back
        
        self.fileserver = TeamFileServer(team_id)
        self.files = []
        
        self._create_ui()
        self._load_files()
        
        info("FileServerModule", "File server module initialized")
    
    def _create_ui(self):
        """Create file server UI"""
        debug("FileServerModule", "Creating file server UI")
        
        # Header
        header = CustomFrame(self, transparent=True)
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        CustomLabel(
            header,
            text=f"📁 File Server - {self.team_name}",
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
        
        # Stats section
        stats_frame = CustomFrame(self, transparent=False)
        stats_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        stats_container = CustomFrame(stats_frame, transparent=True)
        stats_container.pack(fill="x", padx=15, pady=15)
        
        self.stats_label = CustomLabel(
            stats_container,
            text="📊 Loading statistics...",
            size=11,
            color=("#666666", "#999999")
        )
        self.stats_label.pack(anchor="w")
        
        # Upload section
        upload_frame = CustomFrame(self, transparent=False)
        upload_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        upload_container = CustomFrame(upload_frame, transparent=True)
        upload_container.pack(fill="x", padx=15, pady=15)
        
        CustomLabel(
            upload_container,
            text="⬆️ Upload File",
            size=14,
            bold=True
        ).pack(anchor="w", pady=(0, 10))
        
        upload_row = CustomFrame(upload_container, transparent=True)
        upload_row.pack(fill="x")
        
        CustomButton(
            upload_row,
            text="📂 Select File",
            command=self._select_and_upload,
            style="primary",
            width=150,
            height=40
        ).pack(side="left", padx=(0, 10))
        
        CustomLabel(
            upload_row,
            text="Upload files to share with your team",
            size=10,
            color=("#666666", "#999999")
        ).pack(side="left")
        
        # Files list
        files_container = CustomFrame(self, transparent=False)
        files_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        CustomLabel(
            files_container,
            text="📂 Team Files",
            size=14,
            bold=True
        ).pack(padx=15, pady=(15, 10), anchor="w")
        
        # Fixed frame for files (no scrollbar)
        self.files_scroll = CustomFrame(files_container, transparent=True)
        self.files_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        debug("FileServerModule", "File server UI created")
    
    def _load_files(self):
        """Load and display files"""
        debug("FileServerModule", "Loading files")
        
        try:
            self.files = self.fileserver.get_files()
            stats = self.fileserver.get_storage_stats()
            
            # Update stats
            total_size_mb = stats['total_size'] / (1024 * 1024)
            stats_text = f"📊 {stats['total_files']} files | {total_size_mb:.2f} MB | {stats['total_downloads']} downloads"
            self.stats_label.configure(text=stats_text)
            
            # Clear existing files
            for widget in self.files_scroll.winfo_children():
                widget.destroy()
            
            if not self.files:
                CustomLabel(
                    self.files_scroll,
                    text="📁 No files yet. Upload your first file above!",
                    size=12,
                    color=("#888888", "#888888")
                ).pack(pady=50)
                return
            
            # Display files
            for file in self.files:
                self._create_file_card(file)
            
            info("FileServerModule", f"Loaded {len(self.files)} files")
            
        except Exception as e:
            error("FileServerModule", f"Error loading files: {e}")
    
    def _create_file_card(self, file: Dict):
        """Create file card widget"""
        # File card
        card = CustomFrame(self.files_scroll, transparent=False)
        card.pack(fill="x", pady=5)
        
        content = CustomFrame(card, transparent=True)
        content.pack(fill="x", padx=15, pady=10)
        
        # Header row
        header_row = CustomFrame(content, transparent=True)
        header_row.pack(fill="x", pady=(0, 5))
        
        # File icon and name
        file_type = file['file_type']
        icon = self.FILE_TYPE_ICONS.get(file_type, self.FILE_TYPE_ICONS['unknown'])
        
        name_label = CustomLabel(
            header_row,
            text=f"{icon} {file['file_name']}",
            size=12,
            bold=True
        )
        name_label.pack(side="left")
        
        # File size
        size_mb = file['file_size'] / (1024 * 1024)
        size_label = CustomLabel(
            header_row,
            text=f"{size_mb:.2f} MB",
            size=10,
            color=("#666666", "#999999")
        )
        size_label.pack(side="right", padx=(10, 0))
        
        # Info row
        info_row = CustomFrame(content, transparent=True)
        info_row.pack(fill="x", pady=(0, 5))
        
        # Upload info
        try:
            upload_time = datetime.fromisoformat(file['uploaded_at'])
            time_str = upload_time.strftime("%Y-%m-%d %H:%M")
        except:
            time_str = file['uploaded_at']
        
        info_text = f"Uploaded by User {file['uploaded_by']} on {time_str} | {file['downloads']} downloads"
        CustomLabel(
            info_row,
            text=info_text,
            size=9,
            color=("#666666", "#999999")
        ).pack(anchor="w")
        
        # Description
        if file.get('description'):
            desc_label = CustomLabel(
                content,
                text=file['description'],
                size=10,
                color=("#888888", "#888888")
            )
            desc_label.pack(anchor="w", pady=(0, 5))
        
        # Actions row
        actions_row = CustomFrame(content, transparent=True)
        actions_row.pack(fill="x", pady=(5, 0))
        
        # Download button
        CustomButton(
            actions_row,
            text="⬇️ Download",
            command=lambda f=file: self._download_file(f),
            style="primary",
            width=120,
            height=30
        ).pack(side="left", padx=(0, 5))
        
        # Delete button (only for uploader)
        if file['uploaded_by'] == self.current_user_id:
            CustomButton(
                actions_row,
                text="🗑️ Delete",
                command=lambda f=file: self._delete_file(f),
                style="secondary",
                width=100,
                height=30
            ).pack(side="left")
    
    def _select_and_upload(self):
        """Select and upload file"""
        debug("FileServerModule", "Selecting file to upload")
        
        file_path = filedialog.askopenfilename(
            title="Select file to upload",
            filetypes=[("All files", "*.*")]
        )
        
        if not file_path:
            debug("FileServerModule", "No file selected")
            return
        
        info("FileServerModule", f"File selected: {file_path}")
        
        # Get description
        # For now, no description dialog - just upload
        self._upload_file(file_path, "")
    
    def _upload_file(self, file_path: str, description: str):
        """Upload file to server"""
        debug("FileServerModule", f"Uploading file: {file_path}")
        
        try:
            file_id = self.fileserver.upload_file(
                file_path,
                self.current_user_id,
                description
            )
            
            if file_id:
                file_name = Path(file_path).name
                info("FileServerModule", f"File uploaded: {file_name}")
                
                # Show success message
                MessageBox.show_success(
                    self,
                    "Upload Successful",
                    f"File '{file_name}' uploaded successfully!"
                )
                
                # Desktop notification
                if self.notification_system:
                    self.notification_system.show_success(
                        f"File uploaded: {file_name}",
                        duration=3000
                    )
                
                # Sound notification
                if self.sound_system:
                    self.sound_system.play_sound('file_upload')
                
                # Reload files
                self._load_files()
            else:
                error("FileServerModule", "Upload failed")
                MessageBox.show_error(self, "Upload Failed", "Failed to upload file")
                
        except Exception as e:
            error("FileServerModule", f"Upload error: {e}")
            MessageBox.show_error(self, "Upload Error", f"Error: {str(e)}")
    
    def _download_file(self, file: Dict):
        """Download file from server"""
        debug("FileServerModule", f"Downloading file: {file['file_name']}")
        
        try:
            # Select destination
            dest_path = filedialog.asksaveasfilename(
                title="Save file as",
                initialfile=file['file_name'],
                defaultextension=f".{file['file_type']}"
            )
            
            if not dest_path:
                debug("FileServerModule", "Download cancelled")
                return
            
            success = self.fileserver.download_file(
                file['id'],
                self.current_user_id,
                dest_path
            )
            
            if success:
                info("FileServerModule", f"File downloaded: {file['file_name']}")
                
                # Show success message
                MessageBox.show_success(
                    self,
                    "Download Successful",
                    f"File '{file['file_name']}' downloaded successfully!"
                )
                
                # Desktop notification
                if self.notification_system:
                    self.notification_system.show_success(
                        f"File downloaded: {file['file_name']}",
                        duration=3000
                    )
                
                # Sound notification
                if self.sound_system:
                    self.sound_system.play_sound('file_download')
                
                # Reload to update download count
                self._load_files()
            else:
                error("FileServerModule", "Download failed")
                MessageBox.show_error(self, "Download Failed", "Failed to download file")
                
        except Exception as e:
            error("FileServerModule", f"Download error: {e}")
            MessageBox.show_error(self, "Download Error", f"Error: {str(e)}")
    
    def _delete_file(self, file: Dict):
        """Delete file from server"""
        debug("FileServerModule", f"Deleting file: {file['file_name']}")
        
        # Confirm deletion
        def on_confirm():
            success = self.fileserver.delete_file(file['id'], self.current_user_id)
            
            if success:
                info("FileServerModule", f"File deleted: {file['file_name']}")
                
                # Show success message
                MessageBox.show_success(
                    self,
                    "Delete Successful",
                    f"File '{file['file_name']}' deleted successfully!"
                )
                
                # Desktop notification
                if self.notification_system:
                    self.notification_system.show_info(
                        f"File deleted: {file['file_name']}",
                        duration=3000
                    )
                
                # Sound notification
                if self.sound_system:
                    self.sound_system.play_sound('file_delete')
                
                # Reload files
                self._load_files()
            else:
                error("FileServerModule", "Delete failed")
                MessageBox.show_error(self, "Delete Failed", "Failed to delete file")
        
        MessageBox.show_confirm(
            self,
            "Delete File",
            f"Are you sure you want to delete '{file['file_name']}'?\n\nThis action cannot be undone.",
            on_confirm
        )

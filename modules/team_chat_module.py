"""
Team Chat Module
Real-time chat för teams med P2P-synkronisering
"""

import customtkinter as ctk
from typing import Callable, Optional, Dict
from datetime import datetime
import uuid
from pathlib import Path
from tkinter import filedialog
from core.debug_logger import debug, info, warning, error
from core.ui_components import (
    CustomButton, CustomLabel, CustomFrame, CustomEntry, MessageBox
)
from core.file_transfer import FileTransfer
from core.typing_indicator import TypingIndicator


class TeamChatModule(ctk.CTkFrame):
    """Team chat module med P2P sync"""
    
    def __init__(
        self,
        master,
        team_system,
        p2p_system,
        file_transfer,
        team_info: dict,
        user_info: dict,
        on_back: Callable = None,
        **kwargs
    ):
        """
        Initialize team chat module
        
        Args:
            master: Parent widget
            team_system: TeamSystem instance
            p2p_system: P2PSystem instance
            file_transfer: FileTransfer instance
            team_info: Team information dict
            user_info: Current user information
            on_back: Callback for back button
        """
        debug("TeamChatModule", f"Initializing chat for team: {team_info['name']}")
        
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.team_system = team_system
        self.p2p_system = p2p_system
        self.typing_indicator = TypingIndicator(p2p_system)
        self.file_transfer = file_transfer
        self.team_info = team_info
        self.user_info = user_info
        self.on_back = on_back
        
        self._create_ui()
        self._load_messages()
        
        # Auto-refresh messages
        self._start_auto_refresh()
        
        info("TeamChatModule", "Team chat initialized")
    
    def _create_ui(self):
        """Create chat UI"""
        debug("TeamChatModule", "Creating chat UI")
        
        # Main container
        main_container = CustomFrame(self, transparent=True)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = CustomFrame(main_container, transparent=False)
        header_frame.pack(fill="x", pady=(0, 15))
        
        header_content = CustomFrame(header_frame, transparent=True)
        header_content.pack(fill="x", padx=20, pady=15)
        
        # Back button
        if self.on_back:
            CustomButton(
                header_content,
                text="← Back",
                command=self.on_back,
                width=100,
                height=35,
                style="secondary"
            ).pack(side="left", padx=(0, 15))
        
        # Team name
        CustomLabel(
            header_content,
            text=f"💬 {self.team_info['name']}",
            size=16,
            bold=True
        ).pack(side="left")
        
        # Members count
        members = self.team_system.get_team_members(self.team_info['team_id'])
        CustomLabel(
            header_content,
            text=f"({len(members)} members)",
            size=11,
            color=("#999999", "#999999")
        ).pack(side="left", padx=(10, 0))
        
        # Messages container (no scrollbar)
        self.messages_frame = ctk.CTkScrollableFrame(
            main_container,
            fg_color=("#2b2b2b", "#2b2b2b"),
            scrollbar_button_color=("#2b2b2b", "#2b2b2b")
        )
        # Hide scrollbar completely
        self.messages_frame._scrollbar.configure(width=0)
        self.messages_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Input area
        input_frame = CustomFrame(main_container, transparent=False)
        input_frame.pack(fill="x")
        
        input_content = CustomFrame(input_frame, transparent=True)
        input_content.pack(fill="x", padx=20, pady=15)
        
        # Message input
        self.message_entry = ctk.CTkEntry(
            input_content,
            placeholder_text="Type a message...",
            height=40,
            font=("Segoe UI", 12),
            fg_color=("#3b3b3b", "#3b3b3b"),
            border_color=("#4b4b4b", "#4b4b4b"),
            text_color=("#ffffff", "#ffffff")
        )
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        # Set focus after a short delay
        self.message_entry.after(100, lambda: self.message_entry.focus())
        
        # File button
        file_btn = CustomButton(
            input_content,
            text="📎",
            command=self._send_file,
            width=50,
            height=40,
            style="secondary"
        )
        file_btn.pack(side="right", padx=(0, 5))
        
        # Send button
        send_btn = CustomButton(
            input_content,
            text="Send",
            command=self._send_message,
            width=100,
            height=40,
            style="success"
        )
        send_btn.pack(side="right")
        
        # Typing indicator label
        self.typing_label = CustomLabel(
            main_container,
            text="",
            size=10,
            color=("#888888", "#888888")
        )
        self.typing_label.pack(fill="x", padx=20, pady=(0, 5))
        
        # Enter key binding
        self.message_entry.bind("<Return>", lambda e: self._send_message())
        
        # Typing detection
        self.message_entry.bind("<KeyPress>", lambda e: self._on_typing())
        self.typing_timer = None
        
        # Setup typing indicator callbacks
        self.typing_indicator.on_typing_started = self._on_user_typing_started
        self.typing_indicator.on_typing_stopped = self._on_user_typing_stopped
        
        # Start typing indicator system
        self.typing_indicator.start()
        
        debug("TeamChatModule", "Chat UI created")
    
    def _load_messages(self):
        """Load and display messages"""
        debug("TeamChatModule", "Loading messages")
        
        # Clear existing messages
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
        
        # Get chat messages from team data
        team_data = self.team_system.get_team_data(
            self.team_info['team_id'],
            data_type='chat'
        )
        
        if not team_data:
            # No messages yet
            no_msg_label = CustomLabel(
                self.messages_frame,
                text="No messages yet. Start the conversation!",
                size=12,
                color=("#999999", "#999999")
            )
            no_msg_label.pack(pady=50)
            return
        
        # Sort by timestamp
        messages = sorted(team_data, key=lambda x: x.get('created_at', ''))
        
        # Display messages
        for msg_data in messages:
            try:
                message = msg_data['data_value']
                self._create_message_widget(message)
            except Exception as e:
                error("TeamChatModule", f"Error displaying message: {e}")
        
        # Scroll to bottom
        self.messages_frame._parent_canvas.yview_moveto(1.0)
        
        debug("TeamChatModule", f"Loaded {len(messages)} messages")
    
    def _create_message_widget(self, message: dict):
        """Create widget for a message"""
        is_own = message.get('user_id') == self.user_info['id']
        
        # Message container
        msg_container = CustomFrame(
            self.messages_frame,
            transparent=True
        )
        msg_container.pack(fill="x", pady=3, padx=10)
        
        # Message bubble
        bubble_color = ("#1f6aa5", "#144870") if is_own else ("#3a3a3a", "#3a3a3a")
        
        bubble = CustomFrame(
            msg_container,
            transparent=False
        )
        bubble.configure(fg_color=bubble_color)
        
        if is_own:
            bubble.pack(side="right", padx=(50, 0))
        else:
            bubble.pack(side="left", padx=(0, 50))
        
        bubble_content = CustomFrame(bubble, transparent=True)
        bubble_content.pack(padx=15, pady=10)
        
        # Username (if not own message)
        if not is_own:
            username = message.get('username', f"User #{message.get('user_id')}")
            CustomLabel(
                bubble_content,
                text=username,
                size=10,
                bold=True,
                color=("#1f6aa5", "#4da6ff")
            ).pack(anchor="w")
        
        # Message text
        CustomLabel(
            bubble_content,
            text=message.get('text', ''),
            size=11,
            wraplength=400
        ).pack(anchor="w", pady=(2, 0) if not is_own else 0)
        
        # Timestamp
        timestamp = message.get('timestamp', '')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%H:%M")
            except:
                time_str = timestamp[:5]
            
            CustomLabel(
                bubble_content,
                text=time_str,
                size=9,
                color=("#999999", "#999999")
            ).pack(anchor="e", pady=(3, 0))
    
    def _on_typing(self):
        """Handle typing event"""
        debug("TeamChatModule", "User is typing")
        
        # Send typing indicator
        self.typing_indicator.send_typing(
            self.team_info['team_id'],
            str(self.user_info['id']),
            self.user_info['name']
        )
        
        # Cancel existing timer
        if self.typing_timer:
            self.after_cancel(self.typing_timer)
        
        # Set timer to stop typing indicator after 3 seconds
        self.typing_timer = self.after(3000, self._stop_typing)
    
    def _stop_typing(self):
        """Stop typing indicator"""
        debug("TeamChatModule", "User stopped typing")
        
        self.typing_indicator.stop_typing(
            self.team_info['team_id'],
            str(self.user_info['id'])
        )
        
        self.typing_timer = None
    
    def _on_user_typing_started(self, team_id: str, user_id: str, username: str):
        """Handle when another user starts typing"""
        if team_id != self.team_info['team_id']:
            return
        
        if str(user_id) == str(self.user_info['id']):
            return  # Ignore own typing
        
        info("TeamChatModule", f"{username} started typing")
        self._update_typing_label()
    
    def _on_user_typing_stopped(self, team_id: str, user_id: str):
        """Handle when another user stops typing"""
        if team_id != self.team_info['team_id']:
            return
        
        debug("TeamChatModule", f"User {user_id[:8]}... stopped typing")
        self._update_typing_label()
    
    def _update_typing_label(self):
        """Update typing indicator label"""
        typing_users = self.typing_indicator.get_typing_users(self.team_info['team_id'])
        
        # Filter out own user
        typing_users = [uid for uid in typing_users if str(uid) != str(self.user_info['id'])]
        
        if not typing_users:
            self.typing_label.configure(text="")
        elif len(typing_users) == 1:
            self.typing_label.configure(text="Someone is typing...")
        else:
            self.typing_label.configure(text=f"{len(typing_users)} people are typing...")
    
    def _send_message(self):
        """Send a message"""
        text = self.message_entry.get().strip()
        
        if not text:
            return
        
        debug("TeamChatModule", f"Sending message: {text[:50]}...")
        
        # Stop typing indicator
        self._stop_typing()
        
        # Create message
        message = {
            'text': text,
            'user_id': self.user_info['id'],
            'username': self.user_info['name'],
            'timestamp': datetime.now().isoformat(),
            'type': 'text'
        }
        
        # Generate unique message ID
        msg_id = str(uuid.uuid4())[:8]
        
        # Save to team data (will auto-sync via TeamSync)
        success = self.team_system.set_team_data(
            self.team_info['team_id'],
            'chat',
            msg_id,
            message
        )
        
        if success:
            # Clear input
            self.message_entry.delete(0, 'end')
            
            # Reload messages
            self._load_messages()
            
            info("TeamChatModule", "Message sent and synced")
        else:
            error("TeamChatModule", "Failed to send message")
    
    def _send_file(self):
        """Send a file"""
        debug("TeamChatModule", "Opening file dialog")
        
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select file to send",
            filetypes=[
                ("All files", "*.*"),
                ("Images", "*.png *.jpg *.jpeg *.gif"),
                ("Documents", "*.pdf *.doc *.docx *.txt"),
            ]
        )
        
        if not file_path:
            return
        
        file_path = Path(file_path)
        info("TeamChatModule", f"Sending file: {file_path.name}")
        
        # Get team members
        members = self.team_system.get_team_members(self.team_info['team_id'])
        connected_peers = self.p2p_system.get_connected_peers()
        connected_ids = [p['id'] for p in connected_peers]
        
        # Find connected team members
        target_peers = [m['peer_id'] for m in members if m.get('peer_id') and m['peer_id'] in connected_ids and m['user_id'] != self.user_info['id']]
        
        if not target_peers:
            MessageBox.show_info(
                self.master,
                "No Recipients",
                "No team members are currently online to receive the file."
            )
            return
        
        # Send file to all connected team members
        for peer_id in target_peers:
            metadata = {
                'team_id': self.team_info['team_id'],
                'from_user': self.user_info['name']
            }
            
            transfer_id = self.file_transfer.send_file(peer_id, file_path, metadata)
            
            if transfer_id:
                info("TeamChatModule", f"File transfer started: {transfer_id}")
        
        # Also save file message to chat
        message = {
            'text': f"📎 Sent file: {file_path.name}",
            'user_id': self.user_info['id'],
            'username': self.user_info['name'],
            'timestamp': datetime.now().isoformat(),
            'type': 'file',
            'file_name': file_path.name
        }
        
        msg_id = str(uuid.uuid4())[:8]
        self.team_system.set_team_data(
            self.team_info['team_id'],
            'chat',
            msg_id,
            message
        )
        
        self._load_messages()
        
        MessageBox.show_success(
            self.master,
            "File Sent",
            f"File '{file_path.name}' is being sent to {len(target_peers)} team member(s)."
        )
    
    def _start_auto_refresh(self):
        """Start auto-refresh of messages"""
        def refresh():
            if self.winfo_exists():
                self._load_messages()
                # Refresh every 3 seconds
                self.after(3000, refresh)
        
        # Start after 3 seconds
        self.after(3000, refresh)
        debug("TeamChatModule", "Auto-refresh started")
    
    def cleanup(self):
        """Cleanup when module is destroyed"""
        debug("TeamChatModule", "Cleaning up chat module")
        # Stop auto-refresh by destroying widget
        self.destroy()


if __name__ == "__main__":
    # Test team chat
    info("TEST", "Testing TeamChatModule...")
    
    from core.custom_window import CustomWindow
    from core.p2p_system import P2PSystem
    from core.team_system import TeamSystem
    from core.team_sync import TeamSync
    
    # Create window
    app = CustomWindow(title="Team Chat Test", width=800, height=700)
    
    # Create systems
    p2p = P2PSystem()
    team_sys = TeamSystem(user_id=1, p2p_system=p2p)
    team_sync = TeamSync(team_system=team_sys, p2p_system=p2p)
    team_sys.team_sync = team_sync
    
    # Start systems
    p2p.start()
    team_sync.start()
    
    # Create a test team
    team_id = team_sys.create_team("Test Team", "A test team")
    teams = team_sys.get_my_teams()
    team_info = teams[0] if teams else None
    
    if team_info:
        # Create chat module
        user_info = {
            'id': 1,
            'name': 'Test User',
            'email': 'test@example.com'
        }
        
        chat_module = TeamChatModule(
            app.content_frame,
            team_system=team_sys,
            team_info=team_info,
            user_info=user_info
        )
        chat_module.pack(fill="both", expand=True)
        
        info("TEST", "Starting mainloop...")
        app.mainloop()
        
        # Cleanup
        team_sync.stop()
        p2p.stop()
    else:
        print("No team found!")

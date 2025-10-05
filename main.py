"""
MultiTeam P2P Communication - Main Application
Huvudapplikation med modulärt window-in-window system
"""

import customtkinter as ctk
from core.debug_logger import debug, info, warning, error, exception
from core.custom_window import CustomWindow
from core.ui_components import CustomLabel, CustomFrame, CustomButton, MessageBox
from core.global_settings import settings
from core.system_tray import SystemTray
from core.notification_system import NotificationSystem
from modules.login_module import LoginModule
from modules.registration_module import RegistrationModule
from modules.settings_module import SettingsModule
from modules.twofa_setup_module import TwoFASetupModule
from modules.peers_module import PeersModule
from modules.teams_module import TeamsModule
from core.p2p_system import P2PSystem
from core.team_system import TeamSystem
from core.team_sync import TeamSync
from core.file_transfer import FileTransfer
from core.offline_queue import OfflineQueue
from core.queue_processor import QueueProcessor
from core.heartbeat_system import HeartbeatSystem
from core.auto_reconnect import AutoReconnect
from core.read_receipts import ReadReceipts
from core.presence_system import PresenceSystem
from core.remember_me import RememberMe
from core.session_manager import SessionManager, ActivityTracker
from modules.timeout_warning_dialog import TimeoutWarningDialog
from core.license_system import LicenseSystem


class MultiTeamApp:
    """Main application class"""
    
    def __init__(self):
        info("MultiTeamApp", "=" * 60)
        info("MultiTeamApp", "Starting MultiTeam P2P Communication")
        info("MultiTeamApp", "=" * 60)
        debug("MultiTeamApp", "Initializing main application")
        
        # Create main window with large size
        self.window = CustomWindow(
            title="MultiTeam Communication",
            width=1400,
            height=1200,
            resizable=True
        )
        
        # System tray
        self.system_tray = SystemTray(self.window)
        # Notification system
        self.notifications = NotificationSystem(self.window)
        debug("MultiTeamApp", "Notification system created")
        
        # P2P System
        self.p2p_system = P2PSystem()
        debug("MultiTeamApp", "P2P system created")
        
        # Team System (will be initialized after login)
        self.team_system = None
        self.team_sync = None
        self.file_transfer = None
        self.offline_queue = None
        self.queue_processor = None
        self.heartbeat_system = None
        self.auto_reconnect = None
        self.read_receipts = None
        self.presence_system = None
        
        # Session management
        self.session_manager = SessionManager(timeout_minutes=30)
        self.activity_tracker = ActivityTracker(self.session_manager)
        self.session_manager.on_timeout = self._handle_session_timeout
        self.session_manager.on_warning = self._handle_session_warning
        
        # Current user
        self.current_user = None
        self.current_module = None
        
        # Setup window close handler
        self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        # Setup application
        self._setup_app()
        
        info("MultiTeamApp", "Application initialized successfully")
    
    def _setup_app(self):
        """Setup application"""
        debug("MultiTeamApp", "Setting up application")
        
        # Check for remember me session
        remember_me = RememberMe()
        session = remember_me.get_session()
        
        if session:
            info("MultiTeamApp", f"Found valid session for user: {session['user_id']}")
            # Auto-login with session
            self._handle_login_success(session)
        else:
            # Show login module as first screen
            self._show_login_module()
        
        debug("MultiTeamApp", "Application setup completed")
    
    def _clear_content(self):
        """Clear content by recreating content_frame"""
        debug("MultiTeamApp", "=" * 60)
        debug("MultiTeamApp", "CLEARING CONTENT - START")
        debug("MultiTeamApp", "=" * 60)
        
        # Log current state
        if self.current_module:
            debug("MultiTeamApp", f"Current module: {type(self.current_module).__name__}")
            debug("MultiTeamApp", f"Current module children: {len(self.current_module.winfo_children())}")
        else:
            debug("MultiTeamApp", "No current module")
        
        # Log content_frame state
        try:
            children_count = len(self.window.content_frame.winfo_children())
            debug("MultiTeamApp", f"Content frame children before clear: {children_count}")
            for i, child in enumerate(self.window.content_frame.winfo_children()):
                debug("MultiTeamApp", f"  Child {i}: {type(child).__name__}")
        except Exception as e:
            error("MultiTeamApp", f"Error logging content_frame state: {e}")
        
        # Destroy current module
        if self.current_module:
            try:
                debug("MultiTeamApp", "Destroying current module...")
                self.current_module.destroy()
                debug("MultiTeamApp", "✓ Current module destroyed")
            except Exception as e:
                error("MultiTeamApp", f"Error destroying module: {e}")
            finally:
                self.current_module = None
        
        # RADICAL APPROACH: Clear ALL widgets from main_container
        try:
            debug("MultiTeamApp", "Checking main_container widgets...")
            main_children = list(self.window.main_container.winfo_children())
            debug("MultiTeamApp", f"Main container has {len(main_children)} children")
            
            for i, child in enumerate(main_children):
                child_type = type(child).__name__
                debug("MultiTeamApp", f"  Main child {i}: {child_type}")
                
                # Destroy everything except titlebar (row 0)
                try:
                    grid_info = child.grid_info()
                    if grid_info and grid_info.get('row', 0) != 0:
                        debug("MultiTeamApp", f"  Destroying {child_type} at row {grid_info.get('row')}")
                        child.destroy()
                except Exception as e:
                    debug("MultiTeamApp", f"  Error checking/destroying {child_type}: {e}")
            
            debug("MultiTeamApp", "✓ Main container cleared (except titlebar)")
        except Exception as e:
            error("MultiTeamApp", f"Error clearing main_container: {e}")
        
        # Create new content_frame (använd grid som original)
        debug("MultiTeamApp", "Creating new content_frame...")
        self.window.content_frame = ctk.CTkFrame(
            self.window.main_container,
            fg_color="transparent",
            corner_radius=0
        )
        self.window.content_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.window.content_frame.grid_rowconfigure(0, weight=1)
        self.window.content_frame.grid_columnconfigure(0, weight=1)
        debug("MultiTeamApp", "✓ New content_frame created")
        
        # Force update
        debug("MultiTeamApp", "Forcing window update...")
        self.window.update()
        debug("MultiTeamApp", "✓ Window updated")
        
        # Verify clean state
        try:
            new_children = len(self.window.content_frame.winfo_children())
            debug("MultiTeamApp", f"Content frame children after clear: {new_children}")
            if new_children > 0:
                warning("MultiTeamApp", f"⚠️ WARNING: {new_children} children still exist!")
                for i, child in enumerate(self.window.content_frame.winfo_children()):
                    warning("MultiTeamApp", f"  Remaining child {i}: {type(child).__name__}")
        except Exception as e:
            error("MultiTeamApp", f"Error verifying clean state: {e}")
        
        debug("MultiTeamApp", "=" * 60)
        debug("MultiTeamApp", "CLEARING CONTENT - COMPLETE")
        debug("MultiTeamApp", "=" * 60)
    
    def _show_login_module(self):
        """Show login module"""
        info("MultiTeamApp", "Showing login module")
        
        # Användare måste logga in först, license hanteras efter login
        self._clear_content()
        
        self.current_module = LoginModule(
            self.window.content_frame,
            on_login_success=self._handle_login_success,
            on_register_click=self._show_registration_module,
            on_forgot_password=self._show_password_reset_module,
            on_license_activation=self._show_license_activation,
            on_license_application=self._show_license_application
        )
        self.current_module.pack(fill="both", expand=True)
        
        # Set focus to email field after module is visible
        self.window.update_idletasks()
        self.current_module.update_idletasks()
        
        def set_focus():
            try:
                self.current_module.email_entry.configure(state="normal")
                self.current_module.email_entry.focus_force()
                self.current_module.email_entry.icursor(0)
                debug("MultiTeamApp", "Focus set to email field")
            except Exception as e:
                error("MultiTeamApp", f"Failed to set focus: {e}")
        
        self.window.after(300, set_focus)
    
    def _show_license_activation(self):
        """Show license activation screen in main window"""
        info("MultiTeamApp", "=" * 60)
        info("MultiTeamApp", "SHOWING LICENSE ACTIVATION (MAIN WINDOW)")
        info("MultiTeamApp", "=" * 60)
        
        self._clear_content()
        
        # Use original CustomTkinter module in main window
        def show_module():
            debug("MultiTeamApp", "Creating LicenseActivationModule...")
            from modules.license_activation_module import LicenseActivationModule
            
            self.current_module = LicenseActivationModule(
                self.window.content_frame,
                on_success=self._show_login_module
            )
            debug("MultiTeamApp", f"Module created: {type(self.current_module).__name__}")
            
            self.current_module.pack(fill="both", expand=True)
            debug("MultiTeamApp", "✓ Module packed")
            
            info("MultiTeamApp", "License activation screen displayed")
        
        debug("MultiTeamApp", "Scheduling module display in 100ms...")
        self.window.after(100, show_module)
    
    def _handle_license_success(self):
        """Handle successful license activation"""
        info("MultiTeamApp", "License activation successful")
        # Window will close automatically
    
    def _handle_license_close(self):
        """Handle license activation window close"""
        debug("MultiTeamApp", "License activation window closed")
        self.license_window = None
    
    def _show_license_application(self):
        """Show license application screen"""
        info("MultiTeamApp", "Showing license application screen")
        self._clear_content()
        
        # Delay för att säkerställa att gamla widgets rensas
        def show_module():
            from modules.license_application_module import LicenseApplicationModule
            from core.license_activation import LicenseActivation
            
            activation_system = LicenseActivation()
            
            self.current_module = LicenseApplicationModule(
                self.window.content_frame,
                activation_system=activation_system,
                on_back=self._show_license_activation,
                on_success=self._show_license_activation
            )
            self.current_module.pack(fill="both", expand=True)
            
            debug("MultiTeamApp", "License application screen displayed")
        
        self.window.after(100, show_module)
    
    def _show_registration_module(self):
        """Show registration module"""
        info("MultiTeamApp", "Showing registration module")
        self._clear_content()
        
        self.current_module = RegistrationModule(
            self.window.content_frame,
            on_registration_complete=self._handle_registration_complete,
            on_back_to_login=self._show_login_module
        )
        self.current_module.pack(fill="both", expand=True)
        
        # Force update and set focus
        self.window.update_idletasks()
        self.current_module.update_idletasks()
        
        # Set focus to first field after module is visible
        def set_focus():
            try:
                self.current_module.name_entry.configure(state="normal")
                self.current_module.name_entry.focus_force()
                self.current_module.name_entry.icursor(0)
                debug("MultiTeamApp", "Focus set to name field")
            except Exception as e:
                error("MultiTeamApp", f"Failed to set focus: {e}")
        
        self.window.after(300, set_focus)
        
        debug("MultiTeamApp", "Registration module displayed")
    
    def _show_password_reset_module(self):
        """Show password reset module"""
        info("MultiTeamApp", "Showing password reset module")
        self._clear_content()
        
        from modules.password_reset_module import PasswordResetModule
        
        self.current_module = PasswordResetModule(
            self.window.content_frame,
            on_back=self._show_login_module,
            on_success=self._show_login_module
        )
        self.current_module.pack(fill="both", expand=True)
        
        debug("MultiTeamApp", "Password reset module displayed")
    
    def _handle_login_success(self, user: dict):
        """Handle successful login"""
        info("MultiTeamApp", f"Login successful for user: {user['email']}")
        debug("MultiTeamApp", f"User data: {user}")
        
        self.current_user = user
        
        # Update user status widget
        self.window.update_user_status(
            username=user['name'],
            status="connecting",
            avatar_text=user['name'][0]
        )
        
        # Initialize License System
        info("MultiTeamApp", "Initializing license system for user")
        self.license_system = LicenseSystem(user_id=user['id'])
        
        # Initialize Team System
        info("MultiTeamApp", "Initializing team system for user")
        self.team_system = TeamSystem(user_id=user['id'], p2p_system=self.p2p_system, license_system=self.license_system)
        
        # Initialize Team Sync
        info("MultiTeamApp", "Initializing team sync system")
        self.team_sync = TeamSync(team_system=self.team_system, p2p_system=self.p2p_system)
        self.team_system.team_sync = self.team_sync  # Link back
        
        # Initialize File Transfer
        info("MultiTeamApp", "Initializing file transfer system")
        self.file_transfer = FileTransfer(p2p_system=self.p2p_system)
        
        # Initialize Offline Queue
        info("MultiTeamApp", "Initializing offline queue system")
        self.offline_queue = OfflineQueue(user_id=str(user['id']))
        
        # Initialize Queue Processor
        info("MultiTeamApp", "Initializing queue processor")
        self.queue_processor = QueueProcessor(
            offline_queue=self.offline_queue,
            p2p_system=self.p2p_system,
            file_transfer=self.file_transfer,
            team_sync=self.team_sync
        )
        
        # Setup queue processor callbacks
        self.queue_processor.on_item_sent = self._on_queue_item_sent
        
        # Start P2P system
        info("MultiTeamApp", "Starting P2P system for user")
        self.p2p_system.start()
        
        info("MultiTeamApp", "Starting team sync system")
        self.team_sync.start()
        
        # Start queue processor
        info("MultiTeamApp", "Starting queue processor")
        self.queue_processor.start()
        
        # Initialize Heartbeat System
        info("MultiTeamApp", "Initializing heartbeat system")
        self.heartbeat_system = HeartbeatSystem(p2p_system=self.p2p_system)
        self.heartbeat_system.on_peer_timeout = self._on_peer_timeout
        
        # Initialize Auto-Reconnect
        info("MultiTeamApp", "Initializing auto-reconnect system")
        self.auto_reconnect = AutoReconnect(
            p2p_system=self.p2p_system,
            heartbeat_system=self.heartbeat_system
        )
        self.auto_reconnect.on_reconnect_success = self._on_reconnect_success
        self.auto_reconnect.on_reconnect_failed = self._on_reconnect_failed
        
        # Start heartbeat and auto-reconnect
        info("MultiTeamApp", "Starting heartbeat system")
        self.heartbeat_system.start()
        
        info("MultiTeamApp", "Starting auto-reconnect system")
        self.auto_reconnect.start()
        
        # Initialize Read Receipts
        info("MultiTeamApp", "Initializing read receipts system")
        self.read_receipts = ReadReceipts(user_id=str(user['id']))
        
        # Initialize Presence System
        info("MultiTeamApp", "Initializing presence system")
        self.presence_system = PresenceSystem(p2p_system=self.p2p_system)
        self.presence_system.on_user_online = self._on_user_online
        self.presence_system.on_user_offline = self._on_user_offline
        
        # Start presence system
        info("MultiTeamApp", "Starting presence system")
        self.presence_system.start()
        
        # Update status to online after P2P starts
        self.window.after(1000, lambda: self.window.update_user_status(
            username=user.get('name', user.get('email', 'User')),
            status="online",
            avatar_text=user['name'][0]
        ))
        
        # Update Client ID display
        client_id = self.p2p_system.get_client_id()
        self.window.update_client_id(client_id)
        
        # Show success notification
        self.notifications.show_success(
            f"Welcome back, {user.get('name', user.get('email', 'User'))}!",
            duration=4000
        )
        
        # Start session monitoring
        info("MultiTeamApp", "Starting session monitoring")
        self.session_manager.start()
        self.activity_tracker.bind_to_window(self.window)
        
        # Show main dashboard
        self._show_dashboard()
    
    def _handle_registration_complete(self, email: str):
        """Handle completed registration"""
        info("MultiTeamApp", f"Registration completed for: {email}")
        
        # Go back to login and pre-fill email
        self._show_login_module()
        if self.current_module and hasattr(self.current_module, 'set_email'):
            self.current_module.set_email(email)
    
    def _create_dashboard_card(self, parent, title: str, icon: str = "", width: int = 300, height: int = 333):
        """
        Global helper to create a dashboard card
        
        Args:
            parent: Parent container
            title: Card title
            icon: Optional emoji icon
            width: Card width (default 300)
            height: Card height (default 333 - en tredjedel lägre)
            
        Returns:
            tuple: (card_frame, content_frame) - card frame and content container
        """
        card = CustomFrame(parent, transparent=False)
        card.pack(side="left", padx=10)
        card.configure(
            border_width=2,
            border_color=("#3a3a3a", "#3a3a3a"),
            corner_radius=15,  # Rundare hörn (från default ~10)
            width=width,
            height=height
        )
        # FORCE the size - prevent content from resizing the card
        card.pack_propagate(False)
        
        # Card header
        header = CustomFrame(card, transparent=True)
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        title_text = f"{icon} {title}" if icon else title
        CustomLabel(header, text=title_text, size=16, bold=True).pack(anchor="w")
        
        # Divider
        ctk.CTkFrame(card, height=1, fg_color=("#3a3a3a", "#3a3a3a")).pack(fill="x", padx=20, pady=10)
        
        # Content container
        content = CustomFrame(card, transparent=True)
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        return card, content
    
    def _show_dashboard(self):
        """Show main dashboard with sidebar and card grid"""
        info("MultiTeamApp", "Showing main dashboard")
        self._clear_content()
        
        # Main container
        main_container = CustomFrame(
            self.window.content_frame,
            transparent=False
        )
        main_container.pack(fill="both", expand=True)
        
        # LEFT SIDEBAR - Navigation menu
        sidebar = CustomFrame(main_container, transparent=False)
        sidebar.pack(side="left", fill="y", padx=0, pady=0)
        sidebar.configure(width=200, border_width=0)
        
        # Sidebar header
        sidebar_header = CustomFrame(sidebar, transparent=True)
        sidebar_header.pack(fill="x", padx=15, pady=20)
        
        CustomLabel(
            sidebar_header,
            text="📋 Menu",
            size=18,
            bold=True
        ).pack(anchor="w")
        
        # Sidebar buttons (vertical stack)
        sidebar_buttons = [
            ("⚙️ Settings", self._show_settings),
            ("📜 License", self._show_license_management),
            ("🔐 2FA Setup", self._show_2fa_setup),
            ("👥 Teams", self._show_teams),
            ("🌐 Peers", self._show_peers),
            ("🚪 Logout", self._handle_logout),
        ]
        
        for text, command in sidebar_buttons:
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                command=command,
                width=170,
                height=35,
                fg_color=("#2d2d2d", "#2d2d2d"),
                hover_color=("#3d3d3d", "#3d3d3d"),
                text_color=("#cccccc", "#cccccc"),
                font=("Segoe UI", 11),
                corner_radius=6,
                border_width=0,
                anchor="w"  # Vänsterjusterad text
            )
            btn.pack(padx=15, pady=3, anchor="w")  # Knapp också vänsterjusterad
        
        # RIGHT CONTENT AREA - Card grid
        content_area = CustomFrame(main_container, transparent=False)
        content_area.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        # Store content area for adding cards
        self.dashboard_content = content_area
        
        # Top bar with welcome and search
        top_bar = CustomFrame(content_area, transparent=True)
        top_bar.pack(fill="x", pady=10)
        
        # Welcome (left)
        welcome_frame = CustomFrame(top_bar, transparent=True)
        welcome_frame.pack(side="left")
        
        CustomLabel(
            welcome_frame,
            text=f"Welcome, {self.current_user['name']}!",
            size=24,
            bold=True
        ).pack(side="left")
        
        # Search box (right)
        search_frame = CustomFrame(top_bar, transparent=True)
        search_frame.pack(side="right")
        
        CustomLabel(search_frame, text="🔍", size=14).pack(side="left", padx=(0, 5))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search modules...",
            width=200,
            height=32,
            fg_color=("#2d2d2d", "#2d2d2d"),
            border_color=("#3a3a3a", "#3a3a3a"),
            text_color=("#ffffff", "#ffffff"),
            placeholder_text_color=("#888888", "#888888")
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", lambda e: self._filter_cards())
        
        # Scrollable card grid container with SUPER SUBTLE scrollbar
        card_scroll = ctk.CTkScrollableFrame(
            content_area,
            fg_color="transparent",
            scrollbar_button_color=("#2a2a2a", "#2a2a2a"),  # Mycket mörk
            scrollbar_button_hover_color=("#3a3a3a", "#3a3a3a"),  # Lite ljusare vid hover
            corner_radius=0
        )
        card_scroll.pack(fill="both", expand=True, pady=20)
        
        # Card grid container inside scrollable frame
        self.card_grid = CustomFrame(card_scroll, transparent=True)
        self.card_grid.pack(fill="both", expand=True)
        
        # Store all cards for filtering
        self.all_cards = []
        
        # Add default cards
        self._add_dashboard_cards()
        
        # Start real-time updates
        self._start_realtime_updates()
        
        self.current_module = main_container
        debug("MultiTeamApp", "Dashboard displayed with sidebar")
    
    def _add_dashboard_cards(self):
        """Add default dashboard cards to the grid - ALL SAME SIZE"""
        # FIXED CARD SIZE - all cards must be this size
        CARD_WIDTH = 300
        CARD_HEIGHT = 333  # En tredjedel lägre (500 * 2/3)
        CARDS_PER_ROW = 3
        
        # Module definitions with actions, update functions, and status
        # Status determined by license system
        self.modules_data = [
            {
                "icon": "👤",
                "title": "User Info",
                "content": lambda: f"📧 {self.current_user['email']}\n🏢 {self.current_user['company']}\n👤 {self.current_user['role'].title()}\n📜 License: {self.license_system.get_tier_info()['name']}",
                "action": lambda: self._show_settings(),
                "update": True,
                "module_index": 0
            },
            {
                "icon": "📊",
                "title": "Statistics",
                "content": lambda: f"Total Users: 1\nActive Teams: {len(self.team_system.get_user_teams(self.current_user['id']))}\nMessages: 0",
                "action": None,
                "update": True,
                "module_index": 1
            },
            {
                "icon": "💬",
                "title": "Messages",
                "content": lambda: "No new messages\nLast message: Never",
                "action": lambda: self._show_teams(),
                "update": False,
                "module_index": 2
            },
            {
                "icon": "📁",
                "title": "Files",
                "content": lambda: "Total Files: 0\nStorage Used: 0 MB\nShared: 0",
                "action": lambda: self._show_teams(),
                "update": False,
                "module_index": 3
            },
            {
                "icon": "🔔",
                "title": "Notifications",
                "content": lambda: "No notifications\nAll caught up!",
                "action": None,
                "update": False,
                "module_index": 4
            },
            {
                "icon": "⏰",
                "title": "Activity",
                "content": lambda: f"Last Login: Today\nSession Time: {self._get_session_time()}\nActions: 3",
                "action": None,
                "update": True,
                "module_index": 5
            },
            {
                "icon": "🌐",
                "title": "Network",
                "content": lambda: f"Connected Peers: {len(self.p2p_system.get_connected_peers())}\nNetwork Status: Online\nLatency: 0ms",
                "action": lambda: self._show_peers(),
                "update": True,
                "module_index": 6
            },
            {
                "icon": "🔒",
                "title": "Security",
                "content": lambda: "2FA: Not Setup\nLast Password Change: Never\nSessions: 1",
                "action": lambda: self._show_2fa_setup(),
                "update": False,
                "module_index": 7
            },
            {
                "icon": "📈",
                "title": "Analytics",
                "content": lambda: "Page Views: 12\nClicks: 8\nTime Spent: 15min",
                "action": None,
                "update": False,
                "module_index": 8
            },
            {
                "icon": "⚡",
                "title": "Quick Actions",
                "content": lambda: "Create Team\nInvite User\nSend Message",
                "action": lambda: self._show_teams(),
                "update": False,
                "module_index": 9
            },
        ]
        
        # Create rows dynamically
        current_row = None
        cards_in_row = 0
        
        for module in self.modules_data:
            # Create new row if needed
            if cards_in_row == 0:
                current_row = CustomFrame(self.card_grid, transparent=True)
                current_row.pack(fill="x", pady=5)
            
            # Get status from license system
            module_status = self.license_system.get_module_status(module["module_index"])
            
            # Get status color
            status_colors = {
                "active": ("#2d7a2d", "#2d7a2d"),      # Grön - aktiv modul
                "error": ("#c42b1c", "#c42b1c"),       # Röd - fel/licens utgått
                "warning": ("#f7630c", "#f7630c"),     # Gul - dålig kontakt
                "disabled": ("#3a3a3a", "#3a3a3a")     # Grå - nedsläckt/ingen licens
            }
            border_color = status_colors.get(module_status, status_colors["disabled"])
            hover_color = ("#4a4a4a", "#4a4a4a")  # Ljusare vid hover
            
            # Create card with FIXED size and status color
            card, content = self._create_dashboard_card(
                current_row,
                title=module["title"],
                icon=module["icon"],
                width=CARD_WIDTH,
                height=CARD_HEIGHT
            )
            
            # Set initial border color based on status
            card.configure(border_color=border_color)
            
            # Make ENTIRE card clickable if action exists
            if module["action"]:
                card.configure(cursor="hand2")
                # Bind to card AND all children for full clickability
                def make_clickable(widget, action):
                    widget.bind("<Button-1>", lambda e: action())
                    for child in widget.winfo_children():
                        make_clickable(child, action)
                
                make_clickable(card, module["action"])
                
                # Add hover effect to entire card
                def on_enter(e, c=card, bc=border_color):
                    c.configure(border_color=hover_color)
                
                def on_leave(e, c=card, bc=border_color):
                    c.configure(border_color=bc)
                
                card.bind("<Enter>", on_enter)
                card.bind("<Leave>", on_leave)
                for child in card.winfo_children():
                    child.bind("<Enter>", on_enter)
                    child.bind("<Leave>", on_leave)
            
            # Add content label (will be updated)
            content_label = CustomLabel(
                content,
                text=module["content"](),
                size=10,
                color=("#cccccc", "#cccccc")
            )
            content_label.pack(anchor="w", pady=5)
            
            # Store card info for updates and filtering
            self.all_cards.append({
                "card": card,
                "row": current_row,
                "label": content_label,
                "module": module,
                "visible": True
            })
            
            cards_in_row += 1
            
            # Reset row counter after CARDS_PER_ROW
            if cards_in_row >= CARDS_PER_ROW:
                cards_in_row = 0
        
        debug("MultiTeamApp", f"Dashboard cards added: {len(self.modules_data)} modules")
    
    def _filter_cards(self):
        """Filter cards based on search query"""
        query = self.search_entry.get().lower()
        
        # Hide/show cards based on search
        for card_info in self.all_cards:
            module = card_info["module"]
            title = module["title"].lower()
            
            if query in title:
                if not card_info["visible"]:
                    card_info["card"].pack(side="left", padx=10)
                    card_info["visible"] = True
            else:
                if card_info["visible"]:
                    card_info["card"].pack_forget()
                    card_info["visible"] = False
        
        debug("MultiTeamApp", f"Filtered cards with query: {query}")
    
    def _start_realtime_updates(self):
        """Start real-time updates for dashboard cards"""
        def update_cards():
            try:
                for card_info in self.all_cards:
                    module = card_info["module"]
                    
                    # Only update cards that need real-time updates
                    if module["update"] and card_info["visible"]:
                        # Update content
                        new_content = module["content"]()
                        card_info["label"].configure(text=new_content)
                
                # Schedule next update (every 5 seconds)
                if hasattr(self, 'window') and self.window.winfo_exists():
                    self.window.after(5000, update_cards)
            except Exception as e:
                debug("MultiTeamApp", f"Error updating cards: {e}")
        
        # Start updates
        self.window.after(5000, update_cards)
        debug("MultiTeamApp", "Real-time updates started")
    
    def _get_session_time(self):
        """Get current session time"""
        import time
        from datetime import datetime
        if hasattr(self, 'session_manager') and self.session_manager:
            try:
                # Check if last_activity is datetime object
                if isinstance(self.session_manager.last_activity, datetime):
                    elapsed = int(time.time() - self.session_manager.last_activity.timestamp())
                else:
                    elapsed = int(time.time() - self.session_manager.last_activity)
                minutes = elapsed // 60
                return f"{minutes} min"
            except:
                return "0 min"
        return "0 min"
    
    def _show_settings(self):
        """Show settings module"""
        info("MultiTeamApp", "Showing settings module")
        self._clear_content()
        
        self.current_module = SettingsModule(
            self.window.content_frame,
            on_back=self._show_dashboard
        )
        self.current_module.pack(fill="both", expand=True)
        
        debug("MultiTeamApp", "Settings module displayed")
    
    def _show_license_management(self):
        """Show license management module"""
        info("MultiTeamApp", "Showing license management module")
        self._clear_content()
        
        from modules.license_management_module import LicenseManagementModule
        
        # Check if SuperAdmin (ID 1 or role 'superadmin')
        is_superadmin = (
            self.current_user.get('id') == 1 or 
            self.current_user.get('email') == 'superadmin' or
            self.current_user.get('role') == 'superadmin'
        )
        
        self.current_module = LicenseManagementModule(
            self.window.content_frame,
            license_system=self.license_system,
            on_back=self._show_dashboard,
            is_superadmin=is_superadmin
        )
        self.current_module.pack(fill="both", expand=True)
        
        debug("MultiTeamApp", "License management module displayed")
    
    def _show_2fa_setup(self):
        """Show 2FA setup module"""
        info("MultiTeamApp", "Showing 2FA setup module")
        
        # Check if user is SuperAdmin (no database ID)
        if self.current_user.get('role') == 'superadmin' and self.current_user.get('id', 0) == 0:
            MessageBox.show_info(
                self.window,
                "SuperAdmin Notice",
                "2FA is not available for the SuperAdmin account.\n\nPlease use a regular user account to enable 2FA."
            )
            return
        
        self._clear_content()
        
        self.current_module = TwoFASetupModule(
            self.window.content_frame,
            user_id=self.current_user['id'],
            user_email=self.current_user['email'],
            on_complete=self._handle_2fa_setup_complete,
            on_cancel=self._show_dashboard
        )
        self.current_module.pack(fill="both", expand=True)
        
        debug("MultiTeamApp", "2FA setup module displayed")
    
    def _handle_2fa_setup_complete(self):
        """Handle 2FA setup completion"""
        info("MultiTeamApp", "2FA setup completed")
        self._show_dashboard()
    
    def _show_teams(self):
        """Show team details directly (skip teams list)"""
        info("MultiTeamApp", "Showing team details")
        
        # Check if user has teams
        if not self.team_system:
            MessageBox.show_info(
                self.window,
                "No Team",
                "Please create or join a team first."
            )
            return
        
        teams = self.team_system.get_user_teams(self.current_user['id'])
        
        if not teams:
            MessageBox.show_info(
                self.window,
                "No Teams",
                "You are not a member of any team yet.\n\nCreate or join a team first."
            )
            return
        
        # Use first team (or let user select if multiple teams)
        team = teams[0]
        
        # Show team details directly
        self._show_team_details(team)
    
    def _show_team_details(self, team: dict):
        """Show integrated team details view"""
        info("MultiTeamApp", f"Showing team details for: {team['name']}")
        self._clear_content()
        
        from modules.team_details_module import TeamDetailsModule
        
        self.current_module = TeamDetailsModule(
            self.window.content_frame,
            team_id=team['team_id'],
            team_name=team['name'],
            current_user_id=str(self.current_user['id']),
            team_system=self.team_system,
            notification_system=self.notifications,
            sound_system=self.sound_notifications if hasattr(self, 'sound_notifications') else None,
            on_back=self._show_dashboard  # Back går till dashboard
        )
        self.current_module.pack(fill="both", expand=True)
        
        debug("MultiTeamApp", "Team details displayed")
    
    def _show_peers(self):
        """Show peers module"""
        info("MultiTeamApp", "Showing peers module")
        self._clear_content()
        
        self.current_module = PeersModule(
            self.window.content_frame,
            p2p_system=self.p2p_system,
            user_info=self.current_user,
            on_back=self._show_dashboard
        )
        self.current_module.pack(fill="both", expand=True)
        
        self.p2p_system.on_peer_discovered = self.current_module.on_peer_discovered
        self.p2p_system.on_peer_connected = self.current_module.on_peer_connected
        self.p2p_system.on_peer_disconnected = self.current_module.on_peer_disconnected
        
        debug("MultiTeamApp", "Peers module displayed")
    
    def _show_task_manager(self):
        """Show task manager module"""
        info("MultiTeamApp", "Showing task manager module")
        
        # Check if user has teams
        if not self.team_system:
            MessageBox.show_info(
                self.window,
                "No Team",
                "Task Manager requires a team.\n\nPlease create or join a team first."
            )
            return
        
        teams = self.team_system.get_user_teams(self.current_user['id'])
        
        if not teams:
            MessageBox.show_info(
                self.window,
                "No Teams",
                "You are not a member of any team yet.\n\nCreate or join a team to use Task Manager."
            )
            return
        
        # Use first team for now (in future, let user select)
        team = teams[0]
        
        self._clear_content()
        
        from modules.task_manager_module import TaskManagerModule
        
        self.current_module = TaskManagerModule(
            self.window.content_frame,
            team_id=team['team_id'],
            team_name=team['name'],
            current_user_id=str(self.current_user['id']),
            on_back=self._show_dashboard
        )
        self.current_module.pack(fill="both", expand=True)
        
        debug("MultiTeamApp", "Task manager module displayed")
    
    def _show_calendar(self):
        """Show calendar module"""
        info("MultiTeamApp", "Showing calendar module")
        
        # Check if user has teams
        if not self.team_system:
            MessageBox.show_info(
                self.window,
                "No Team",
                "Calendar requires a team.\n\nPlease create or join a team first."
            )
            return
        
        teams = self.team_system.get_user_teams(self.current_user['id'])
        
        if not teams:
            MessageBox.show_info(
                self.window,
                "No Teams",
                "You are not a member of any team yet.\n\nCreate or join a team to use Calendar."
            )
            return
        
        # Use first team for now (in future, let user select)
        team = teams[0]
        
        self._clear_content()
        
        from modules.calendar_module import CalendarModule
        
        self.current_module = CalendarModule(
            self.window.content_frame,
            team_id=team['team_id'],
            team_name=team['name'],
            current_user_id=str(self.current_user['id']),
            on_back=self._show_dashboard
        )
        self.current_module.pack(fill="both", expand=True)
        
        debug("MultiTeamApp", "Calendar module displayed")
    
    def _show_fileserver(self):
        """Show file server module"""
        info("MultiTeamApp", "Showing file server module")
        
        # Check if user has teams
        if not self.team_system:
            MessageBox.show_info(
                self.window,
                "No Team",
                "File Server requires a team.\n\nPlease create or join a team first."
            )
            return
        
        teams = self.team_system.get_user_teams(self.current_user['id'])
        
        if not teams:
            MessageBox.show_info(
                self.window,
                "No Teams",
                "You are not a member of any team yet.\n\nCreate or join a team to use File Server."
            )
            return
        
        # Use first team for now (in future, let user select)
        team = teams[0]
        
        self._clear_content()
        
        from modules.fileserver_module import FileServerModule
        
        self.current_module = FileServerModule(
            self.window.content_frame,
            team_id=team['team_id'],
            team_name=team['name'],
            current_user_id=str(self.current_user['id']),
            notification_system=self.notifications,
            sound_system=self.sound_notifications if hasattr(self, 'sound_notifications') else None,
            on_back=self._show_dashboard
        )
        self.current_module.pack(fill="both", expand=True)
        
        debug("MultiTeamApp", "File server module displayed")
    
    def _on_queue_item_sent(self, item_type: str, item: dict):
        """Handle queue item sent"""
        info("MultiTeamApp", f"Queue item sent: {item_type}")
        
        # Show notification
        if item_type == 'message':
            self.notifications.show_success("Offline message sent", duration=3000)
        elif item_type == 'file':
            self.notifications.show_success(f"Offline file sent: {item.get('file_name', 'file')}", duration=3000)
        elif item_type == 'team_action':
            self.notifications.show_success("Team action synced", duration=3000)
    
    def _on_peer_timeout(self, peer_id: str):
        """Handle peer timeout"""
        warning("MultiTeamApp", f"Peer timed out: {peer_id[:8]}...")
        
        # Show notification
        self.notifications.show_warning(f"Peer disconnected: {peer_id[:8]}...", duration=4000)
        
        # Add to auto-reconnect queue
        if self.auto_reconnect:
            self.auto_reconnect.add_peer_to_reconnect(peer_id)
    
    def _on_reconnect_success(self, peer_id: str, retry_count: int):
        """Handle successful reconnect"""
        info("MultiTeamApp", f"Reconnected to peer: {peer_id[:8]}... (after {retry_count} attempts)")
        
        # Show notification
        self.notifications.show_success(f"Reconnected to peer: {peer_id[:8]}...", duration=4000)
    
    def _on_reconnect_failed(self, peer_id: str, retry_count: int):
        """Handle failed reconnect"""
        error("MultiTeamApp", f"Failed to reconnect to peer: {peer_id[:8]}... (after {retry_count} attempts)")
        
        # Show notification
        self.notifications.show_error(f"Could not reconnect to peer: {peer_id[:8]}...", duration=5000)
    
    def _on_user_online(self, user_id: str, user_info: dict):
        """Handle user coming online"""
        username = user_info.get('username', f"User {user_id[:8]}...")
        info("MultiTeamApp", f"User came online: {username}")
        
        # Show notification
        self.notifications.show_info(f"{username} is now online", duration=3000)
    
    def _on_user_offline(self, user_id: str, user_info: dict):
        """Handle user going offline"""
        username = user_info.get('username', f"User {user_id[:8]}...")
        info("MultiTeamApp", f"User went offline: {username}")
        
        # No notification for offline (too spammy)
    
    def _on_window_close(self):
        """Handle window close event"""
        debug("MultiTeamApp", "Window close requested")
        
        # Check if minimize to tray is enabled
        if settings.get("minimize_to_tray", False):
            info("MultiTeamApp", "Minimizing to system tray")
            self.window.withdraw()  # Hide window
            
            # Show tray icon if not already shown
            if not self.system_tray.is_running:
                self.system_tray.show()
        else:
            info("MultiTeamApp", "Closing application")
            self._exit_app()
    
    def _exit_app(self):
        """Exit application completely"""
        info("MultiTeamApp", "Exiting application")
        
        # Stop P2P system
        info("MultiTeamApp", "Stopping P2P system")
        self.p2p_system.stop()
        
        # Hide system tray if running
        if self.system_tray.is_running:
            self.system_tray.hide()
        
        # Destroy window
        self.window.destroy()
    
    def _handle_logout(self):
        """Handle logout"""
        info("MultiTeamApp", f"User logging out: {self.current_user['email']}")
        
        # Stop Team Sync
        if self.team_sync:
            info("MultiTeamApp", "Stopping team sync system")
            self.team_sync.stop()
            self.team_sync = None
        
        # Stop P2P system
        info("MultiTeamApp", "Stopping P2P system")
        self.p2p_system.stop()
        
        self.current_user = None
        self.team_system = None
        
        # Update user status widget to offline
        self.window.update_user_status(
            username=None,
            status="offline",
            avatar_text=None
        )
        
        # Stop session monitoring
        if self.session_manager:
            info("MultiTeamApp", "Stopping session monitoring")
            self.session_manager.stop()
        
        self._show_login_module()
        
        debug("MultiTeamApp", "User logged out successfully")
    
    def _handle_session_timeout(self):
        """Handle session timeout"""
        error("MultiTeamApp", "Session timeout - logging out user")
        
        # Show notification
        self.notifications.show_error(
            "Session Expired",
            "You have been logged out due to inactivity."
        )
        
        # Logout user
        self._handle_logout()
    
    def _handle_session_warning(self, remaining_seconds: int):
        """Handle session timeout warning"""
        warning("MultiTeamApp", f"Session timeout warning - {remaining_seconds}s remaining")
        
        # Show warning dialog
        dialog = TimeoutWarningDialog(
            parent=self.window,
            remaining_seconds=remaining_seconds,
            on_extend=self._extend_session,
            on_logout=self._handle_logout
        )
    
    def _extend_session(self):
        """Extend user session"""
        info("MultiTeamApp", "User extended session")
        
        self.session_manager.extend_session()
        
        # Show notification
        self.notifications.show_success(
            "Session Extended",
            "Your session has been extended."
        )
    
    def show_license_management(self):
        """Show license management dialog - public method"""
        info("MultiTeamApp", "Opening license management from main app")
        
        try:
            from modules.settings_module import SettingsModule
            
            # Skapa en temporär settings-instans för att använda dess license management
            temp_settings = SettingsModule(
                self.window.content_frame,
                on_back=lambda: None
            )
            
            # Anropa license management-funktionen
            temp_settings._show_license_management()
            
            # Ta bort temporär instans
            temp_settings.destroy()
            
        except Exception as e:
            error("MultiTeamApp", f"Error opening license management: {e}")
            MessageBox.show_error(
                self.window,
                "Error",
                f"Failed to open license management.\n\nError: {str(e)}"
            )
    
    def run(self):
        """Run application"""
        info("MultiTeamApp", "Starting application main loop")
        
        try:
            self.window.mainloop()
        except KeyboardInterrupt:
            info("MultiTeamApp", "Application interrupted by user")
        except Exception as e:
            exception("MultiTeamApp", "Unexpected error in main loop")
        finally:
            info("MultiTeamApp", "Application shutting down")
            info("MultiTeamApp", "=" * 60)


def main():
    """Main entry point"""
    try:
        app = MultiTeamApp()
        app.run()
    except Exception as e:
        error("MAIN", "Fatal error starting application")
        exception("MAIN", "Application startup failed")
        raise


if __name__ == "__main__":
    main()

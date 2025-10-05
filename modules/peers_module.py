"""
Peers Module
Visa och hantera P2P-anslutningar till andra klienter
"""

import customtkinter as ctk
from typing import Callable, Optional, List
from datetime import datetime
from core.debug_logger import debug, info, warning, error
from core.ui_components import (
    CustomButton, CustomLabel, CustomFrame, MessageBox
)


class PeersModule(ctk.CTkFrame):
    """Peer management module"""
    
    def __init__(
        self,
        master,
        p2p_system,
        user_info: dict,
        on_back: Callable = None,
        **kwargs
    ):
        """
        Initialize peers module
        
        Args:
            master: Parent widget
            p2p_system: P2PSystem instance
            user_info: Current user information
            on_back: Callback for back button
        """
        debug("PeersModule", "Initializing peers module")
        
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.p2p_system = p2p_system
        self.user_info = user_info
        self.on_back = on_back
        self.peer_widgets = {}  # peer_id -> widget dict
        
        self._create_ui()
        self._refresh_peers()
        
        info("PeersModule", "Peers module initialized")
    
    def _create_ui(self):
        """Create peers UI"""
        debug("PeersModule", "Creating peers UI")
        
        # Main scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_fg_color=("#2b2b2b", "#2b2b2b"),
            scrollbar_button_color=("#3b3b3b", "#3b3b3b"),
            scrollbar_button_hover_color=("#4b4b4b", "#4b4b4b")
        )
        scroll_frame.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Header
        header_frame = CustomFrame(scroll_frame, transparent=True)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Back button (if callback provided)
        if self.on_back:
            CustomButton(
                header_frame,
                text="← Back",
                command=self.on_back,
                width=100,
                height=35,
                style="secondary"
            ).pack(side="left", padx=(0, 15))
        
        CustomLabel(
            header_frame,
            text="🌐 Network Peers",
            size=20,
            bold=True
        ).pack(side="left")
        
        # Refresh button
        CustomButton(
            header_frame,
            text="🔄 Refresh",
            command=self._refresh_peers,
            width=120,
            height=35,
            style="secondary"
        ).pack(side="right", padx=5)
        
        # Client ID info
        id_frame = CustomFrame(scroll_frame, transparent=False)
        id_frame.pack(fill="x", pady=(0, 20))
        
        CustomLabel(
            id_frame,
            text="Your Client ID",
            size=12,
            bold=True
        ).pack(anchor="w", padx=20, pady=(15, 5))
        
        client_id = self.p2p_system.get_client_id()
        CustomLabel(
            id_frame,
            text=f"🔑 {client_id}",
            size=10,
            color=("#999999", "#999999")
        ).pack(anchor="w", padx=20, pady=(0, 15))
        
        # Stats
        stats_frame = CustomFrame(scroll_frame, transparent=True)
        stats_frame.pack(fill="x", pady=(0, 15))
        
        self.discovered_label = CustomLabel(
            stats_frame,
            text="Discovered: 0",
            size=11,
            color=("#999999", "#999999")
        )
        self.discovered_label.pack(side="left", padx=10)
        
        self.connected_label = CustomLabel(
            stats_frame,
            text="Connected: 0",
            size=11,
            color=("#107c10", "#0d5e0d")
        )
        self.connected_label.pack(side="left", padx=10)
        
        # Peers list container
        self.peers_container = CustomFrame(scroll_frame, transparent=True)
        self.peers_container.pack(fill="both", expand=True)
        
        debug("PeersModule", "Peers UI created")
    
    def _refresh_peers(self):
        """Refresh peer list"""
        debug("PeersModule", "Refreshing peer list")
        
        # Clear existing widgets
        for widget in self.peers_container.winfo_children():
            widget.destroy()
        self.peer_widgets.clear()
        
        # Get peers from P2P system
        discovered_peers = self.p2p_system.get_peers()
        connected_peers = self.p2p_system.get_connected_peers()
        
        # Update stats
        self.discovered_label.configure(text=f"Discovered: {len(discovered_peers)}")
        self.connected_label.configure(text=f"Connected: {len(connected_peers)}")
        
        if not discovered_peers:
            # No peers found
            no_peers_frame = CustomFrame(self.peers_container, transparent=False)
            no_peers_frame.pack(fill="x", pady=10)
            
            CustomLabel(
                no_peers_frame,
                text="No peers discovered yet",
                size=12,
                color=("#999999", "#999999")
            ).pack(pady=30)
            
            CustomLabel(
                no_peers_frame,
                text="Make sure other clients are running on the same network",
                size=10,
                color=("#666666", "#666666")
            ).pack(pady=(0, 30))
            
            return
        
        # Show each peer
        for peer in discovered_peers:
            self._create_peer_widget(peer)
        
        info("PeersModule", f"Displayed {len(discovered_peers)} peers")
    
    def _create_peer_widget(self, peer: dict):
        """Create widget for a peer"""
        peer_id = peer['id']
        is_connected = self.p2p_system.is_connected(peer_id)
        
        # Peer card
        peer_frame = CustomFrame(self.peers_container, transparent=False)
        peer_frame.pack(fill="x", pady=5)
        
        # Left side - info
        info_frame = CustomFrame(peer_frame, transparent=True)
        info_frame.pack(side="left", fill="x", expand=True, padx=20, pady=15)
        
        # Peer ID (shortened)
        id_label = CustomLabel(
            info_frame,
            text=f"🖥️ {peer_id[:16]}...",
            size=12,
            bold=True
        )
        id_label.pack(anchor="w")
        
        # Connection info
        details_frame = CustomFrame(info_frame, transparent=True)
        details_frame.pack(anchor="w", pady=(5, 0))
        
        # IP and method
        CustomLabel(
            details_frame,
            text=f"📍 {peer['ip']}:{peer.get('port', 'N/A')}",
            size=10,
            color=("#999999", "#999999")
        ).pack(side="left", padx=(0, 15))
        
        if 'method' in peer:
            CustomLabel(
                details_frame,
                text=f"🔗 {peer['method']}",
                size=9,
                color=("#666666", "#666666")
            ).pack(side="left")
        
        # Right side - actions
        action_frame = CustomFrame(peer_frame, transparent=True)
        action_frame.pack(side="right", padx=20, pady=15)
        
        # Status indicator
        status_color = ("#107c10", "#0d5e0d") if is_connected else ("#c42b1c", "#a52318")
        status_text = "● Connected" if is_connected else "○ Disconnected"
        
        CustomLabel(
            action_frame,
            text=status_text,
            size=10,
            color=status_color
        ).pack(side="left", padx=(0, 15))
        
        # Connect/Disconnect button
        if is_connected:
            btn = CustomButton(
                action_frame,
                text="Disconnect",
                command=lambda: self._disconnect_peer(peer_id),
                width=120,
                height=35,
                style="secondary"
            )
        else:
            btn = CustomButton(
                action_frame,
                text="Connect",
                command=lambda: self._connect_peer(peer_id),
                width=120,
                height=35,
                style="success"
            )
        
        btn.pack(side="left")
        
        # Store widget reference
        self.peer_widgets[peer_id] = {
            'frame': peer_frame,
            'button': btn,
            'status_label': status_text
        }
    
    def _connect_peer(self, peer_id: str):
        """Connect to a peer"""
        info("PeersModule", f"Connecting to peer: {peer_id[:8]}...")
        
        # Show connecting message
        MessageBox.show_info(
            self.master,
            "Connecting",
            f"Connecting to peer {peer_id[:16]}..."
        )
        
        # Connect in background
        import threading
        def connect():
            success = self.p2p_system.connect_to_peer(peer_id)
            
            # Update UI in main thread
            self.after(100, lambda: self._handle_connect_result(peer_id, success))
        
        thread = threading.Thread(target=connect, daemon=True)
        thread.start()
    
    def _handle_connect_result(self, peer_id: str, success: bool):
        """Handle connection result"""
        if success:
            info("PeersModule", f"Successfully connected to peer: {peer_id[:8]}...")
            MessageBox.show_success(
                self.master,
                "Connected",
                f"Successfully connected to peer!"
            )
        else:
            warning("PeersModule", f"Failed to connect to peer: {peer_id[:8]}...")
            MessageBox.show_error(
                self.master,
                "Connection Failed",
                f"Could not connect to peer.\n\nPlease try again."
            )
        
        # Refresh UI
        self._refresh_peers()
    
    def _disconnect_peer(self, peer_id: str):
        """Disconnect from a peer"""
        info("PeersModule", f"Disconnecting from peer: {peer_id[:8]}...")
        
        # TODO: Implement disconnect in P2P system
        MessageBox.show_info(
            self.master,
            "Disconnected",
            "Disconnected from peer"
        )
        
        # Refresh UI
        self._refresh_peers()
    
    def on_peer_discovered(self, peer_info: dict):
        """Callback when new peer is discovered"""
        info("PeersModule", f"New peer discovered: {peer_info['id'][:8]}...")
        
        # Refresh UI in main thread
        self.after(100, self._refresh_peers)
    
    def on_peer_connected(self, peer_info: dict):
        """Callback when peer connects"""
        info("PeersModule", f"Peer connected: {peer_info['id'][:8]}...")
        
        # Refresh UI in main thread
        self.after(100, self._refresh_peers)
    
    def on_peer_disconnected(self, peer_info: dict):
        """Callback when peer disconnects"""
        info("PeersModule", f"Peer disconnected: {peer_info['id'][:8]}...")
        
        # Refresh UI in main thread
        self.after(100, self._refresh_peers)


if __name__ == "__main__":
    # Test peers module
    info("TEST", "Testing PeersModule...")
    
    from core.custom_window import CustomWindow
    from core.p2p_system import P2PSystem
    
    # Create window
    app = CustomWindow(title="Peers Test", width=900, height=700)
    
    # Create P2P system
    p2p = P2PSystem()
    p2p.start()
    
    # Create peers module
    user_info = {
        'id': 1,
        'name': 'Test User',
        'email': 'test@example.com'
    }
    
    peers_module = PeersModule(
        app.content_frame,
        p2p_system=p2p,
        user_info=user_info
    )
    peers_module.pack(fill="both", expand=True)
    
    # Set callbacks
    p2p.on_peer_discovered = peers_module.on_peer_discovered
    p2p.on_peer_connected = peers_module.on_peer_connected
    p2p.on_peer_disconnected = peers_module.on_peer_disconnected
    
    info("TEST", "Starting mainloop...")
    app.mainloop()
    
    p2p.stop()

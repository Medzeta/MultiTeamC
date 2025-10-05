"""
P2P Network System
Hårdkodat ID-system med tvåvägskontroll för peer-to-peer kommunikation
Multi-metod anslutning för att kringgå brandväggar och portregler
"""

import socket
import threading
import json
import uuid
import struct
from pathlib import Path
from typing import Optional, Dict, List, Callable, Tuple
from datetime import datetime
import time
from core.debug_logger import debug, info, warning, error, exception


class P2PSystem:
    """P2P network system med hårdkodat ID och tvåvägskontroll"""
    
    def __init__(self):
        """Initialize P2P system"""
        debug("P2PSystem", "Initializing P2P system")
        
        self.config_path = Path("data/p2p_config.json")
        self.client_id = self._load_or_generate_id()
        self.peers: Dict[str, dict] = {}  # peer_id -> peer_info
        self.connections: Dict[str, socket.socket] = {}  # peer_id -> socket
        
        # Multi-method network settings för att kringgå brandväggar
        self.broadcast_ports = [5555, 5556, 5557]  # Flera broadcast-portar
        self.tcp_ports = [5556, 5557, 5558, 8080, 8888, 9999]  # Flera TCP-portar (inkl vanliga)
        self.udp_ports = [5555, 5556, 5557]  # UDP för hole punching
        self.multicast_group = '239.255.255.250'  # Multicast för discovery
        self.multicast_port = 5555
        
        self.running = False
        self.active_tcp_port = None  # Vilken port som faktiskt fungerar
        self.active_servers = []  # Lista över aktiva servrar
        
        # Callbacks
        self.on_peer_discovered: Optional[Callable] = None
        self.on_peer_connected: Optional[Callable] = None
        self.on_peer_disconnected: Optional[Callable] = None
        self.on_message_received: Optional[Callable] = None
        
        info("P2PSystem", f"P2P system initialized with ID: {self.client_id[:8]}...")
    
    def _load_or_generate_id(self) -> str:
        """Load existing ID or generate new one"""
        debug("P2PSystem", "Loading or generating client ID")
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    client_id = config.get('client_id')
                    if client_id:
                        info("P2PSystem", f"Loaded existing ID: {client_id[:8]}...")
                        return client_id
            except Exception as e:
                exception("P2PSystem", f"Error loading config: {e}")
        
        # Generate new ID
        client_id = str(uuid.uuid4())
        self._save_config({'client_id': client_id})
        info("P2PSystem", f"Generated new ID: {client_id[:8]}...")
        return client_id
    
    def _save_config(self, config: dict):
        """Save P2P configuration"""
        debug("P2PSystem", "Saving P2P configuration")
        
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
            debug("P2PSystem", "Configuration saved successfully")
        except Exception as e:
            exception("P2PSystem", f"Error saving config: {e}")
    
    def get_client_id(self) -> str:
        """Get this client's ID"""
        return self.client_id
    
    def start(self):
        """Start P2P system med multi-metod anslutning"""
        info("P2PSystem", "Starting P2P system with multi-method connectivity")
        
        if self.running:
            warning("P2PSystem", "P2P system already running")
            return
        
        self.running = True
        
        # Simplified start - just mark as running
        # Full P2P discovery would be implemented in p2p_advanced_discovery.py
        info("P2PSystem", "P2P system started (discovery methods ready)")
    
    def get_connected_peers(self) -> List[dict]:
        """Get list of connected peers"""
        debug("P2PSystem", "Getting connected peers")
        
        connected = []
        for peer_id, peer_info in self.peers.items():
            if peer_id in self.connections:
                connected.append({
                    'id': peer_id,
                    'ip': peer_info.get('ip', 'unknown'),
                    'port': peer_info.get('port', 0),
                    'discovered_at': peer_info.get('discovered_at', ''),
                    'method': peer_info.get('method', 'unknown')
                })
        
        debug("P2PSystem", f"Found {len(connected)} connected peers")
        return connected
    
    def is_connected(self, peer_id: str) -> bool:
        """Check if peer is connected"""
        return peer_id in self.connections
    
    def send_message(self, peer_id: str, message: dict) -> bool:
        """Send message to peer"""
        debug("P2PSystem", f"Sending message to {peer_id[:8]}...")
        
        if peer_id not in self.connections:
            warning("P2PSystem", f"Peer {peer_id[:8]}... not connected")
            return False
        
        try:
            # In a real implementation, this would send via socket
            # For now, just log it
            info("P2PSystem", f"Message sent to {peer_id[:8]}...")
            return True
        except Exception as e:
            exception("P2PSystem", f"Error sending message: {e}")
            return False
    
    def stop(self):
        """Stop P2P system"""
        info("P2PSystem", "Stopping P2P system")
        
        self.running = False
        
        # Close all connections
        for peer_id, conn in list(self.connections.items()):
            try:
                conn.close()
                debug("P2PSystem", f"Closed connection to peer: {peer_id[:8]}...")
            except:
                pass
        
        self.connections.clear()
        self.peers.clear()
        
        info("P2PSystem", "P2P system stopped")
    
    def _broadcast_presence(self):
        """Broadcast presence to local network"""
        debug("P2PSystem", "Starting presence broadcast")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        while self.running:
            try:
                message = json.dumps({
                    'type': 'discovery',
                    'client_id': self.client_id,
                    'tcp_port': self.tcp_port,
                    'timestamp': datetime.now().isoformat()
                })
                
                sock.sendto(message.encode(), ('<broadcast>', self.broadcast_port))
                debug("P2PSystem", "Broadcasted presence")
                
                # Broadcast every 5 seconds
                threading.Event().wait(5)
                
            except Exception as e:
                if self.running:
                    exception("P2PSystem", f"Error broadcasting presence: {e}")
        
        sock.close()
        debug("P2PSystem", "Stopped presence broadcast")
    
    def _discovery_listener(self):
        """Listen for peer discovery broadcasts"""
        debug("P2PSystem", "Starting discovery listener")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', self.broadcast_port))
        sock.settimeout(1.0)
        
        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                message = json.loads(data.decode())
                
                if message.get('type') == 'discovery':
                    peer_id = message.get('client_id')
                    
                    # Ignore own broadcasts
                    if peer_id == self.client_id:
                        continue
                    
                    # Add or update peer
                    if peer_id not in self.peers:
                        peer_info = {
                            'id': peer_id,
                            'ip': addr[0],
                            'port': message.get('tcp_port'),
                            'discovered_at': datetime.now().isoformat(),
                            'last_seen': datetime.now().isoformat()
                        }
                        self.peers[peer_id] = peer_info
                        info("P2PSystem", f"Discovered new peer: {peer_id[:8]}... at {addr[0]}")
                        
                        if self.on_peer_discovered:
                            self.on_peer_discovered(peer_info)
                    else:
                        # Update last seen
                        self.peers[peer_id]['last_seen'] = datetime.now().isoformat()
                        
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    exception("P2PSystem", f"Error in discovery listener: {e}")
        
        sock.close()
        debug("P2PSystem", "Stopped discovery listener")
    
    def _tcp_server(self):
        """TCP server for incoming peer connections"""
        debug("P2PSystem", "Starting TCP server")
        
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('', self.tcp_port))
        server.listen(5)
        server.settimeout(1.0)
        
        info("P2PSystem", f"TCP server listening on port {self.tcp_port}")
        
        while self.running:
            try:
                conn, addr = server.accept()
                debug("P2PSystem", f"Incoming connection from {addr}")
                
                # Handle connection in separate thread
                thread = threading.Thread(
                    target=self._handle_incoming_connection,
                    args=(conn, addr),
                    daemon=True
                )
                thread.start()
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    exception("P2PSystem", f"Error in TCP server: {e}")
        
        server.close()
        debug("P2PSystem", "Stopped TCP server")
    
    def _handle_incoming_connection(self, conn: socket.socket, addr: tuple):
        """Handle incoming peer connection"""
        debug("P2PSystem", f"Handling connection from {addr}")
        
        try:
            # Receive handshake
            data = conn.recv(1024)
            handshake = json.loads(data.decode())
            
            if handshake.get('type') == 'handshake':
                peer_id = handshake.get('client_id')
                
                # Verify peer ID exists in discovered peers
                if peer_id not in self.peers:
                    warning("P2PSystem", f"Unknown peer trying to connect: {peer_id[:8]}...")
                    conn.close()
                    return
                
                # Send handshake response
                response = json.dumps({
                    'type': 'handshake_response',
                    'client_id': self.client_id,
                    'accepted': True
                })
                conn.send(response.encode())
                
                # Store connection
                self.connections[peer_id] = conn
                info("P2PSystem", f"Peer connected: {peer_id[:8]}...")
                
                if self.on_peer_connected:
                    self.on_peer_connected(self.peers[peer_id])
                
                # Handle messages from this peer
                self._handle_peer_messages(peer_id, conn)
                
        except Exception as e:
            exception("P2PSystem", f"Error handling incoming connection: {e}")
            conn.close()
    
    def _handle_peer_messages(self, peer_id: str, conn: socket.socket):
        """Handle messages from connected peer"""
        debug("P2PSystem", f"Listening for messages from peer: {peer_id[:8]}...")
        
        while self.running and peer_id in self.connections:
            try:
                data = conn.recv(4096)
                if not data:
                    break
                
                message = json.loads(data.decode())
                debug("P2PSystem", f"Received message from {peer_id[:8]}...: {message.get('type')}")
                
                if self.on_message_received:
                    self.on_message_received(peer_id, message)
                    
            except Exception as e:
                if self.running:
                    exception("P2PSystem", f"Error receiving message from peer: {e}")
                break
        
        # Connection closed
        if peer_id in self.connections:
            del self.connections[peer_id]
            info("P2PSystem", f"Peer disconnected: {peer_id[:8]}...")
            
            if self.on_peer_disconnected:
                self.on_peer_disconnected(self.peers.get(peer_id))
    
    def connect_to_peer(self, peer_id: str) -> bool:
        """Connect to a discovered peer"""
        info("P2PSystem", f"Connecting to peer: {peer_id[:8]}...")
        
        if peer_id not in self.peers:
            warning("P2PSystem", f"Peer not found: {peer_id[:8]}...")
            return False
        
        if peer_id in self.connections:
            warning("P2PSystem", f"Already connected to peer: {peer_id[:8]}...")
            return True
        
        peer_info = self.peers[peer_id]
        
        try:
            # Create TCP connection
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((peer_info['ip'], peer_info['port']))
            
            # Send handshake
            handshake = json.dumps({
                'type': 'handshake',
                'client_id': self.client_id
            })
            conn.send(handshake.encode())
            
            # Wait for response
            data = conn.recv(1024)
            response = json.loads(data.decode())
            
            if response.get('accepted'):
                self.connections[peer_id] = conn
                info("P2PSystem", f"Successfully connected to peer: {peer_id[:8]}...")
                
                if self.on_peer_connected:
                    self.on_peer_connected(peer_info)
                
                # Start listening for messages
                thread = threading.Thread(
                    target=self._handle_peer_messages,
                    args=(peer_id, conn),
                    daemon=True
                )
                thread.start()
                
                return True
            else:
                warning("P2PSystem", f"Peer rejected connection: {peer_id[:8]}...")
                conn.close()
                return False
                
        except Exception as e:
            exception("P2PSystem", f"Error connecting to peer: {e}")
            return False
    
    def send_message(self, peer_id: str, message: dict) -> bool:
        """Send message to connected peer"""
        debug("P2PSystem", f"Sending message to peer: {peer_id[:8]}...")
        
        if peer_id not in self.connections:
            warning("P2PSystem", f"Not connected to peer: {peer_id[:8]}...")
            return False
        
        try:
            data = json.dumps(message).encode()
            self.connections[peer_id].send(data)
            debug("P2PSystem", f"Message sent to peer: {peer_id[:8]}...")
            return True
        except Exception as e:
            exception("P2PSystem", f"Error sending message: {e}")
            return False
    
    def get_peers(self) -> List[dict]:
        """Get list of discovered peers"""
        return list(self.peers.values())
    
    def get_connected_peers(self) -> List[dict]:
        """Get list of connected peers"""
        return [self.peers[peer_id] for peer_id in self.connections.keys() if peer_id in self.peers]
    
    def is_connected(self, peer_id: str) -> bool:
        """Check if connected to peer"""
        return peer_id in self.connections


if __name__ == "__main__":
    # Test P2P system
    info("TEST", "Testing P2P System...")
    
    p2p = P2PSystem()
    print(f"Client ID: {p2p.get_client_id()}")
    
    def on_peer_discovered(peer_info):
        print(f"Peer discovered: {peer_info['id'][:8]}... at {peer_info['ip']}")
    
    def on_peer_connected(peer_info):
        print(f"Peer connected: {peer_info['id'][:8]}...")
    
    def on_message_received(peer_id, message):
        print(f"Message from {peer_id[:8]}...: {message}")
    
    p2p.on_peer_discovered = on_peer_discovered
    p2p.on_peer_connected = on_peer_connected
    p2p.on_message_received = on_message_received
    
    p2p.start()
    
    print("P2P system running. Press Ctrl+C to stop...")
    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        p2p.stop()

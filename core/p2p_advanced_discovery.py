"""
Advanced P2P Discovery Methods
Multi-metod anslutning för att kringgå brandväggar, NAT och portregler
"""

import socket
import struct
import threading
import json
from typing import Callable, Optional
from core.debug_logger import debug, info, warning, error, exception


class AdvancedDiscovery:
    """Avancerade discovery-metoder för P2P"""
    
    def __init__(self, client_id: str, on_peer_found: Callable):
        """
        Initialize advanced discovery
        
        Args:
            client_id: This client's unique ID
            on_peer_found: Callback when peer is discovered (peer_info dict)
        """
        self.client_id = client_id
        self.on_peer_found = on_peer_found
        self.running = False
    
    def _udp_broadcast_listener(self, port: int):
        """Listen for UDP broadcasts on specific port"""
        debug("AdvancedDiscovery", f"Starting UDP broadcast listener on port {port}")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', port))
            sock.settimeout(1.0)
            
            info("AdvancedDiscovery", f"UDP broadcast listener active on port {port}")
            
            while self.running:
                try:
                    data, addr = sock.recvfrom(1024)
                    message = json.loads(data.decode())
                    
                    if message.get('type') == 'discovery' and message.get('client_id') != self.client_id:
                        peer_info = {
                            'id': message.get('client_id'),
                            'ip': addr[0],
                            'port': message.get('tcp_port'),
                            'method': 'udp_broadcast',
                            'discovery_port': port
                        }
                        self.on_peer_found(peer_info)
                        
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        debug("AdvancedDiscovery", f"Error in UDP listener port {port}: {e}")
            
            sock.close()
            debug("AdvancedDiscovery", f"Stopped UDP broadcast listener on port {port}")
            
        except Exception as e:
            error("AdvancedDiscovery", f"Failed to start UDP listener on port {port}: {e}")
    
    def _multicast_listener(self, group: str = '239.255.255.250', port: int = 5555):
        """Listen for multicast messages (för större nätverk)"""
        debug("AdvancedDiscovery", f"Starting multicast listener on {group}:{port}")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind to the multicast port
            sock.bind(('', port))
            
            # Join multicast group
            mreq = struct.pack("4sl", socket.inet_aton(group), socket.INADDR_ANY)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            sock.settimeout(1.0)
            
            info("AdvancedDiscovery", f"Multicast listener active on {group}:{port}")
            
            while self.running:
                try:
                    data, addr = sock.recvfrom(1024)
                    message = json.loads(data.decode())
                    
                    if message.get('type') == 'discovery' and message.get('client_id') != self.client_id:
                        peer_info = {
                            'id': message.get('client_id'),
                            'ip': addr[0],
                            'port': message.get('tcp_port'),
                            'method': 'multicast'
                        }
                        self.on_peer_found(peer_info)
                        
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        debug("AdvancedDiscovery", f"Error in multicast listener: {e}")
            
            sock.close()
            debug("AdvancedDiscovery", "Stopped multicast listener")
            
        except Exception as e:
            error("AdvancedDiscovery", f"Failed to start multicast listener: {e}")
    
    def _udp_hole_punching(self, ports: list = [5555, 5556, 5557]):
        """UDP hole punching för NAT traversal"""
        debug("AdvancedDiscovery", "Starting UDP hole punching")
        
        try:
            # Skapa UDP socket för varje port
            sockets = []
            for port in ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.bind(('', port))
                    sock.settimeout(1.0)
                    sockets.append((sock, port))
                    debug("AdvancedDiscovery", f"UDP hole punching socket on port {port}")
                except:
                    pass
            
            if not sockets:
                warning("AdvancedDiscovery", "No UDP sockets available for hole punching")
                return
            
            info("AdvancedDiscovery", f"UDP hole punching active on {len(sockets)} ports")
            
            while self.running:
                for sock, port in sockets:
                    try:
                        data, addr = sock.recvfrom(1024)
                        message = json.loads(data.decode())
                        
                        if message.get('type') == 'punch' and message.get('client_id') != self.client_id:
                            # Respond to punch (öppnar NAT)
                            response = json.dumps({
                                'type': 'punch_response',
                                'client_id': self.client_id,
                                'tcp_port': message.get('tcp_port')
                            })
                            sock.sendto(response.encode(), addr)
                            
                            peer_info = {
                                'id': message.get('client_id'),
                                'ip': addr[0],
                                'port': message.get('tcp_port'),
                                'method': 'udp_hole_punch'
                            }
                            self.on_peer_found(peer_info)
                            
                    except socket.timeout:
                        continue
                    except Exception as e:
                        if self.running:
                            debug("AdvancedDiscovery", f"Error in hole punching: {e}")
            
            for sock, _ in sockets:
                sock.close()
            debug("AdvancedDiscovery", "Stopped UDP hole punching")
            
        except Exception as e:
            error("AdvancedDiscovery", f"Failed UDP hole punching: {e}")
    
    def _local_network_scan(self, ports: list = [5556, 8080]):
        """Scan local network för peers (sista utvägen)"""
        debug("AdvancedDiscovery", "Starting local network scan")
        
        try:
            # Få lokal IP och subnet
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # Beräkna subnet (antar /24)
            ip_parts = local_ip.split('.')
            subnet = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}"
            
            info("AdvancedDiscovery", f"Scanning subnet {subnet}.0/24")
            
            # Scanna varje IP i subnetet
            for i in range(1, 255):
                if not self.running:
                    break
                
                target_ip = f"{subnet}.{i}"
                
                # Skippa egen IP
                if target_ip == local_ip:
                    continue
                
                # Försök ansluta till varje port
                for port in ports:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.1)  # Snabb timeout
                        result = sock.connect_ex((target_ip, port))
                        
                        if result == 0:
                            # Port är öppen, försök handshake
                            try:
                                handshake = json.dumps({
                                    'type': 'scan_handshake',
                                    'client_id': self.client_id
                                })
                                sock.send(handshake.encode())
                                
                                data = sock.recv(1024)
                                response = json.loads(data.decode())
                                
                                if response.get('client_id') and response.get('client_id') != self.client_id:
                                    peer_info = {
                                        'id': response.get('client_id'),
                                        'ip': target_ip,
                                        'port': port,
                                        'method': 'network_scan'
                                    }
                                    self.on_peer_found(peer_info)
                                    info("AdvancedDiscovery", f"Found peer via scan: {target_ip}:{port}")
                            except:
                                pass
                        
                        sock.close()
                        
                    except:
                        pass
            
            debug("AdvancedDiscovery", "Completed local network scan")
            
        except Exception as e:
            error("AdvancedDiscovery", f"Failed local network scan: {e}")
    
    def _multi_method_broadcast(self, broadcast_ports: list, multicast_group: str, multicast_port: int, tcp_ports: list):
        """Broadcast presence på alla metoder"""
        debug("AdvancedDiscovery", "Starting multi-method broadcast")
        
        # UDP Broadcast sockets
        broadcast_sockets = []
        for port in broadcast_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                broadcast_sockets.append((sock, port))
            except:
                pass
        
        # Multicast socket
        multicast_sock = None
        try:
            multicast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            multicast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        except:
            pass
        
        # UDP hole punching sockets
        punch_sockets = []
        for port in [5555, 5556, 5557]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                punch_sockets.append(sock)
            except:
                pass
        
        info("AdvancedDiscovery", f"Broadcasting on {len(broadcast_sockets)} UDP + multicast + {len(punch_sockets)} punch")
        
        while self.running:
            try:
                # Hitta första fungerande TCP port
                active_port = tcp_ports[0] if tcp_ports else 5556
                
                message = json.dumps({
                    'type': 'discovery',
                    'client_id': self.client_id,
                    'tcp_port': active_port
                })
                
                # UDP Broadcast
                for sock, port in broadcast_sockets:
                    try:
                        sock.sendto(message.encode(), ('<broadcast>', port))
                    except:
                        pass
                
                # Multicast
                if multicast_sock:
                    try:
                        multicast_sock.sendto(message.encode(), (multicast_group, multicast_port))
                    except:
                        pass
                
                # UDP Hole Punching
                punch_message = json.dumps({
                    'type': 'punch',
                    'client_id': self.client_id,
                    'tcp_port': active_port
                })
                for sock in punch_sockets:
                    try:
                        sock.sendto(punch_message.encode(), ('<broadcast>', 5555))
                    except:
                        pass
                
                debug("AdvancedDiscovery", "Broadcasted presence on all methods")
                
                # Broadcast var 5:e sekund
                threading.Event().wait(5)
                
            except Exception as e:
                if self.running:
                    exception("AdvancedDiscovery", f"Error in multi-method broadcast: {e}")
        
        # Cleanup
        for sock, _ in broadcast_sockets:
            sock.close()
        if multicast_sock:
            multicast_sock.close()
        for sock in punch_sockets:
            sock.close()
        
        debug("AdvancedDiscovery", "Stopped multi-method broadcast")
    
    def start(self, broadcast_ports, multicast_group, multicast_port, udp_ports, tcp_ports):
        """Start all discovery methods"""
        self.running = True
        
        # Start alla listeners
        for port in broadcast_ports:
            threading.Thread(target=self._udp_broadcast_listener, args=(port,), daemon=True).start()
        
        threading.Thread(target=self._multicast_listener, args=(multicast_group, multicast_port), daemon=True).start()
        threading.Thread(target=self._udp_hole_punching, args=(udp_ports,), daemon=True).start()
        threading.Thread(target=self._local_network_scan, args=(tcp_ports,), daemon=True).start()
        threading.Thread(target=self._multi_method_broadcast, args=(broadcast_ports, multicast_group, multicast_port, tcp_ports), daemon=True).start()
    
    def stop(self):
        """Stop all discovery methods"""
        self.running = False

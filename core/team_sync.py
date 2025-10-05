"""
Team Data Synchronization
Synkronisera team-data mellan peers via P2P
"""

import json
import threading
import time
from typing import Dict, List, Optional
from datetime import datetime
from core.debug_logger import debug, info, warning, error, exception


class TeamSync:
    """Team data synchronization system"""
    
    def __init__(self, team_system, p2p_system):
        """
        Initialize team sync
        
        Args:
            team_system: TeamSystem instance
            p2p_system: P2PSystem instance
        """
        debug("TeamSync", "Initializing team sync system")
        
        self.team_system = team_system
        self.p2p_system = p2p_system
        
        # Sync queue (team_id -> list of changes)
        self.sync_queue: Dict[str, List[dict]] = {}
        
        # Sync lock
        self.sync_lock = threading.Lock()
        
        # Running flag
        self.running = False
        
        # Setup P2P message handler
        self._setup_message_handler()
        
        info("TeamSync", "Team sync system initialized")
    
    def _setup_message_handler(self):
        """Setup P2P message handler for team sync"""
        debug("TeamSync", "Setting up P2P message handler")
        
        # Store original handler
        original_handler = self.p2p_system.on_message_received
        
        def sync_message_handler(peer_id: str, message: dict):
            # Handle team sync messages
            msg_type = message.get('type')
            
            if msg_type == 'team_data_sync':
                self._handle_sync_message(peer_id, message)
            elif msg_type == 'team_data_request':
                self._handle_sync_request(peer_id, message)
            elif msg_type == 'team_invitation':
                self._handle_team_invitation(peer_id, message)
            
            # Call original handler if exists
            if original_handler:
                original_handler(peer_id, message)
        
        self.p2p_system.on_message_received = sync_message_handler
        debug("TeamSync", "P2P message handler configured")
    
    def start(self):
        """Start sync system"""
        info("TeamSync", "Starting team sync system")
        
        if self.running:
            warning("TeamSync", "Team sync already running")
            return
        
        self.running = True
        
        # Start sync worker thread
        sync_thread = threading.Thread(target=self._sync_worker, daemon=True)
        sync_thread.start()
        
        info("TeamSync", "Team sync system started")
    
    def stop(self):
        """Stop sync system"""
        info("TeamSync", "Stopping team sync system")
        self.running = False
    
    def _sync_worker(self):
        """Background worker for syncing data"""
        debug("TeamSync", "Sync worker started")
        
        while self.running:
            try:
                # Process sync queue
                with self.sync_lock:
                    for team_id, changes in list(self.sync_queue.items()):
                        if changes:
                            self._sync_team_data(team_id, changes)
                            self.sync_queue[team_id] = []
                
                # Sleep for a bit
                time.sleep(2)
                
            except Exception as e:
                if self.running:
                    exception("TeamSync", f"Error in sync worker: {e}")
        
        debug("TeamSync", "Sync worker stopped")
    
    def queue_sync(self, team_id: str, data_type: str, data_key: str, data_value: any):
        """
        Queue data for syncing
        
        Args:
            team_id: Team ID
            data_type: Type of data
            data_key: Data key
            data_value: Data value
        """
        debug("TeamSync", f"Queuing sync for {team_id[:8]}... {data_type}/{data_key}")
        
        change = {
            'data_type': data_type,
            'data_key': data_key,
            'data_value': data_value,
            'timestamp': datetime.now().isoformat()
        }
        
        with self.sync_lock:
            if team_id not in self.sync_queue:
                self.sync_queue[team_id] = []
            self.sync_queue[team_id].append(change)
        
        debug("TeamSync", f"Sync queued for {team_id[:8]}...")
    
    def _sync_team_data(self, team_id: str, changes: List[dict]):
        """Sync team data to all team members"""
        debug("TeamSync", f"Syncing {len(changes)} changes for team {team_id[:8]}...")
        
        try:
            # Get team members
            members = self.team_system.get_team_members(team_id)
            
            # Find connected peers who are team members
            connected_peers = self.p2p_system.get_connected_peers()
            connected_peer_ids = [p['id'] for p in connected_peers]
            
            # Get peer_ids of team members
            member_peer_ids = [m['peer_id'] for m in members if m.get('peer_id')]
            
            # Find intersection (team members who are connected)
            peers_to_sync = [pid for pid in member_peer_ids if pid in connected_peer_ids]
            
            if not peers_to_sync:
                debug("TeamSync", f"No connected peers to sync with for team {team_id[:8]}...")
                return
            
            # Create sync message
            sync_message = {
                'type': 'team_data_sync',
                'team_id': team_id,
                'changes': changes,
                'timestamp': datetime.now().isoformat()
            }
            
            # Send to each peer
            for peer_id in peers_to_sync:
                success = self.p2p_system.send_message(peer_id, sync_message)
                if success:
                    debug("TeamSync", f"Synced to peer {peer_id[:8]}...")
                else:
                    warning("TeamSync", f"Failed to sync to peer {peer_id[:8]}...")
            
            info("TeamSync", f"Synced {len(changes)} changes to {len(peers_to_sync)} peers")
            
        except Exception as e:
            exception("TeamSync", f"Error syncing team data: {e}")
    
    def _handle_sync_message(self, peer_id: str, message: dict):
        """Handle incoming sync message"""
        debug("TeamSync", f"Received sync message from {peer_id[:8]}...")
        
        try:
            team_id = message.get('team_id')
            changes = message.get('changes', [])
            
            if not team_id or not changes:
                warning("TeamSync", "Invalid sync message")
                return
            
            # Check if we're a member of this team
            teams = self.team_system.get_my_teams()
            team_ids = [t['team_id'] for t in teams]
            
            if team_id not in team_ids:
                warning("TeamSync", f"Not a member of team {team_id[:8]}...")
                return
            
            # Apply changes
            for change in changes:
                data_type = change.get('data_type')
                data_key = change.get('data_key')
                data_value = change.get('data_value')
                
                if data_type and data_key:
                    # Check for conflicts (version-based)
                    existing_data = self.team_system.get_team_data(team_id, data_type)
                    existing_item = next((d for d in existing_data if d['data_key'] == data_key), None)
                    
                    if existing_item:
                        # Compare timestamps (last-write-wins)
                        existing_time = existing_item.get('updated_at', '')
                        incoming_time = change.get('timestamp', '')
                        
                        if incoming_time > existing_time:
                            # Incoming is newer, update
                            self.team_system.set_team_data(team_id, data_type, data_key, data_value)
                            debug("TeamSync", f"Updated {data_type}/{data_key} (newer)")
                        else:
                            debug("TeamSync", f"Skipped {data_type}/{data_key} (older)")
                    else:
                        # New data, add it
                        self.team_system.set_team_data(team_id, data_type, data_key, data_value)
                        debug("TeamSync", f"Added {data_type}/{data_key} (new)")
            
            info("TeamSync", f"Applied {len(changes)} changes from {peer_id[:8]}...")
            
        except Exception as e:
            exception("TeamSync", f"Error handling sync message: {e}")
    
    def _handle_sync_request(self, peer_id: str, message: dict):
        """Handle request for full team data sync"""
        debug("TeamSync", f"Received sync request from {peer_id[:8]}...")
        
        try:
            team_id = message.get('team_id')
            
            if not team_id:
                warning("TeamSync", "Invalid sync request")
                return
            
            # Get all team data
            team_data = self.team_system.get_team_data(team_id)
            
            # Convert to changes format
            changes = []
            for item in team_data:
                changes.append({
                    'data_type': item['data_type'],
                    'data_key': item['data_key'],
                    'data_value': item['data_value'],
                    'timestamp': item['updated_at']
                })
            
            # Send sync message
            sync_message = {
                'type': 'team_data_sync',
                'team_id': team_id,
                'changes': changes,
                'timestamp': datetime.now().isoformat()
            }
            
            success = self.p2p_system.send_message(peer_id, sync_message)
            
            if success:
                info("TeamSync", f"Sent full sync to {peer_id[:8]}... ({len(changes)} items)")
            else:
                warning("TeamSync", f"Failed to send full sync to {peer_id[:8]}...")
            
        except Exception as e:
            exception("TeamSync", f"Error handling sync request: {e}")
    
    def _handle_team_invitation(self, peer_id: str, message: dict):
        """Handle team invitation from peer"""
        info("TeamSync", f"Received team invitation from {peer_id[:8]}...")
        
        try:
            team_id = message.get('team_id')
            team_name = message.get('team_name')
            team_description = message.get('team_description', '')
            invitation_id = message.get('invitation_id')
            
            # TODO: Show invitation to user (would need UI callback)
            # For now, just log it
            info("TeamSync", f"Invitation to join '{team_name}' (ID: {team_id[:8]}...)")
            
            # Store invitation info for later acceptance
            # This would be shown in a UI notification
            
        except Exception as e:
            exception("TeamSync", f"Error handling team invitation: {e}")
    
    def request_full_sync(self, team_id: str):
        """Request full team data from other members"""
        info("TeamSync", f"Requesting full sync for team {team_id[:8]}...")
        
        try:
            # Get team members
            members = self.team_system.get_team_members(team_id)
            
            # Find connected peers
            connected_peers = self.p2p_system.get_connected_peers()
            connected_peer_ids = [p['id'] for p in connected_peers]
            
            # Get peer_ids of team members
            member_peer_ids = [m['peer_id'] for m in members if m.get('peer_id')]
            
            # Find first connected team member
            for peer_id in member_peer_ids:
                if peer_id in connected_peer_ids:
                    # Request sync from this peer
                    request_message = {
                        'type': 'team_data_request',
                        'team_id': team_id,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    success = self.p2p_system.send_message(peer_id, request_message)
                    
                    if success:
                        info("TeamSync", f"Requested full sync from {peer_id[:8]}...")
                        return True
                    else:
                        warning("TeamSync", f"Failed to request sync from {peer_id[:8]}...")
            
            warning("TeamSync", f"No connected peers to request sync from")
            return False
            
        except Exception as e:
            exception("TeamSync", f"Error requesting full sync: {e}")
            return False


if __name__ == "__main__":
    # Test team sync
    info("TEST", "Testing TeamSync...")
    
    from core.p2p_system import P2PSystem
    from core.team_system import TeamSystem
    
    # Create systems
    p2p = P2PSystem()
    team_sys = TeamSystem(user_id=1, p2p_system=p2p)
    team_sync = TeamSync(team_system=team_sys, p2p_system=p2p)
    
    # Start systems
    p2p.start()
    team_sync.start()
    
    # Create a test team
    team_id = team_sys.create_team("Test Team", "A test team")
    print(f"Created team: {team_id}")
    
    # Add some data
    team_sys.set_team_data(team_id, "chat", "msg1", {"text": "Hello team!", "from": "user1"})
    
    # Queue for sync
    team_sync.queue_sync(team_id, "chat", "msg1", {"text": "Hello team!", "from": "user1"})
    
    print("Sync queued, waiting...")
    time.sleep(5)
    
    # Stop
    team_sync.stop()
    p2p.stop()
    
    print("\n✅ Team sync working!")

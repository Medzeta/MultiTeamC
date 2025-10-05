"""
Queue Processor
Processar offline queue och skickar meddelanden när online
"""

import threading
import time
from typing import Optional, Callable
from core.debug_logger import debug, info, warning, error
from core.offline_queue import OfflineQueue


class QueueProcessor:
    """Processor för offline queue"""
    
    def __init__(
        self,
        offline_queue: OfflineQueue,
        p2p_system,
        file_transfer=None,
        team_sync=None
    ):
        """
        Initialize queue processor
        
        Args:
            offline_queue: OfflineQueue instance
            p2p_system: P2PSystem instance
            file_transfer: FileTransfer instance (optional)
            team_sync: TeamSync instance (optional)
        """
        debug("QueueProcessor", "Initializing queue processor")
        
        self.offline_queue = offline_queue
        self.p2p_system = p2p_system
        self.file_transfer = file_transfer
        self.team_sync = team_sync
        
        self.running = False
        self.process_thread = None
        self.check_interval = 30  # Check every 30 seconds
        self.max_retries = 3
        
        # Callbacks
        self.on_queue_processed: Optional[Callable] = None
        self.on_item_sent: Optional[Callable] = None
        self.on_item_failed: Optional[Callable] = None
        
        info("QueueProcessor", "Queue processor initialized")
    
    def start(self):
        """Start queue processor"""
        info("QueueProcessor", "Starting queue processor")
        
        if self.running:
            warning("QueueProcessor", "Queue processor already running")
            return
        
        self.running = True
        self.process_thread = threading.Thread(target=self._process_loop, daemon=True)
        self.process_thread.start()
        
        info("QueueProcessor", "Queue processor started")
    
    def stop(self):
        """Stop queue processor"""
        info("QueueProcessor", "Stopping queue processor")
        
        self.running = False
        
        if self.process_thread:
            self.process_thread.join(timeout=5)
        
        info("QueueProcessor", "Queue processor stopped")
    
    def _process_loop(self):
        """Main processing loop"""
        debug("QueueProcessor", "Starting processing loop")
        
        while self.running:
            try:
                # Process queue
                self._process_queue()
                
                # Wait before next check
                time.sleep(self.check_interval)
                
            except Exception as e:
                error("QueueProcessor", f"Error in processing loop: {e}")
                time.sleep(self.check_interval)
    
    def _process_queue(self):
        """Process all pending items in queue"""
        debug("QueueProcessor", "Processing queue")
        
        # Get queue stats
        stats = self.offline_queue.get_queue_stats()
        
        if stats['total_pending'] == 0:
            debug("QueueProcessor", "No pending items in queue")
            return
        
        info("QueueProcessor", f"Processing {stats['total_pending']} pending items")
        
        # Process messages
        self._process_messages()
        
        # Process files
        if self.file_transfer:
            self._process_files()
        
        # Process team actions
        if self.team_sync:
            self._process_team_actions()
        
        # Callback
        if self.on_queue_processed:
            self.on_queue_processed(stats)
        
        info("QueueProcessor", "Queue processing completed")
    
    def _process_messages(self):
        """Process pending messages"""
        debug("QueueProcessor", "Processing pending messages")
        
        messages = self.offline_queue.get_pending_messages()
        
        for msg in messages:
            try:
                # Check if recipient is online
                if not self.p2p_system.is_connected(msg['recipient_id']):
                    debug("QueueProcessor", f"Recipient {msg['recipient_id'][:8]}... not online, skipping")
                    continue
                
                # Check retry count
                if msg['retry_count'] >= self.max_retries:
                    warning("QueueProcessor", f"Message {msg['id']} exceeded max retries")
                    if self.on_item_failed:
                        self.on_item_failed('message', msg)
                    continue
                
                # Send message
                success = self.p2p_system.send_message(
                    msg['recipient_id'],
                    {
                        'type': msg['message_type'],
                        'content': msg['content'],
                        'metadata': msg['metadata']
                    }
                )
                
                if success:
                    # Mark as sent
                    self.offline_queue.mark_message_sent(msg['id'])
                    info("QueueProcessor", f"Message {msg['id']} sent successfully")
                    
                    if self.on_item_sent:
                        self.on_item_sent('message', msg)
                else:
                    # Increment retry count
                    self.offline_queue.increment_retry('offline_messages', msg['id'])
                    warning("QueueProcessor", f"Failed to send message {msg['id']}")
                    
            except Exception as e:
                error("QueueProcessor", f"Error processing message {msg['id']}: {e}")
                self.offline_queue.increment_retry('offline_messages', msg['id'])
    
    def _process_files(self):
        """Process pending files"""
        debug("QueueProcessor", "Processing pending files")
        
        files = self.offline_queue.get_pending_files()
        
        for file_item in files:
            try:
                # Check if recipient is online
                if not self.p2p_system.is_connected(file_item['recipient_id']):
                    debug("QueueProcessor", f"Recipient {file_item['recipient_id'][:8]}... not online, skipping")
                    continue
                
                # Check retry count
                if file_item['retry_count'] >= self.max_retries:
                    warning("QueueProcessor", f"File {file_item['id']} exceeded max retries")
                    if self.on_item_failed:
                        self.on_item_failed('file', file_item)
                    continue
                
                # Send file
                success = self.file_transfer.send_file(
                    file_item['recipient_id'],
                    file_item['file_path']
                )
                
                if success:
                    # Mark as sent
                    self.offline_queue.mark_file_sent(file_item['id'])
                    info("QueueProcessor", f"File {file_item['id']} sent successfully")
                    
                    if self.on_item_sent:
                        self.on_item_sent('file', file_item)
                else:
                    # Increment retry count
                    self.offline_queue.increment_retry('offline_files', file_item['id'])
                    warning("QueueProcessor", f"Failed to send file {file_item['id']}")
                    
            except Exception as e:
                error("QueueProcessor", f"Error processing file {file_item['id']}: {e}")
                self.offline_queue.increment_retry('offline_files', file_item['id'])
    
    def _process_team_actions(self):
        """Process pending team actions"""
        debug("QueueProcessor", "Processing pending team actions")
        
        actions = self.offline_queue.get_pending_team_actions()
        
        for action in actions:
            try:
                # Check retry count
                if action['retry_count'] >= self.max_retries:
                    warning("QueueProcessor", f"Team action {action['id']} exceeded max retries")
                    if self.on_item_failed:
                        self.on_item_failed('team_action', action)
                    continue
                
                # Process action based on type
                success = False
                
                if action['action_type'] == 'sync':
                    success = self.team_sync.sync_team(action['team_id'])
                elif action['action_type'] == 'update':
                    success = self.team_sync.broadcast_update(
                        action['team_id'],
                        action['action_data']
                    )
                
                if success:
                    # Mark as sent
                    self.offline_queue.mark_team_action_sent(action['id'])
                    info("QueueProcessor", f"Team action {action['id']} processed successfully")
                    
                    if self.on_item_sent:
                        self.on_item_sent('team_action', action)
                else:
                    # Increment retry count
                    self.offline_queue.increment_retry('offline_team_actions', action['id'])
                    warning("QueueProcessor", f"Failed to process team action {action['id']}")
                    
            except Exception as e:
                error("QueueProcessor", f"Error processing team action {action['id']}: {e}")
                self.offline_queue.increment_retry('offline_team_actions', action['id'])
    
    def process_now(self):
        """Process queue immediately (manual trigger)"""
        info("QueueProcessor", "Manual queue processing triggered")
        
        if not self.running:
            warning("QueueProcessor", "Queue processor not running")
            return
        
        # Process in separate thread to not block
        threading.Thread(target=self._process_queue, daemon=True).start()

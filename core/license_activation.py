"""
License Activation System
Handles trial activation and license applications
Now integrated with central database system
"""

import uuid
import platform
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
from .debug_logger import debug, info, warning, error
from .database_manager import db

class LicenseActivation:
    """
    License activation and application system
    Now uses centralized database through DatabaseManager
    """
    
    def __init__(self):
        """Initialize license activation system"""
        # No longer needs separate database - uses centralized DatabaseManager
        debug("LicenseActivation", "Initializing with centralized database")
        
        # Initialize email service
        try:
            from .license_email_service import LicenseEmailService
            self.email_service = LicenseEmailService()
        except Exception as e:
            warning("LicenseActivation", f"Email service not available: {e}")
            self.email_service = None
        
        # Initialize payment system
        try:
            from .payment_system import PaymentSystem
            self.payment_system = PaymentSystem(provider="stripe")
        except Exception as e:
            warning("LicenseActivation", f"Payment system not available: {e}")
            self.payment_system = None
        
        info("LicenseActivation", "License activation system initialized")
    
    def get_machine_uid(self) -> str:
        """
        Get unique machine identifier (Windows UID)
        Uses a combination of machine UUID and hostname
        """
        try:
            # Get machine UUID
            machine_uuid = str(uuid.UUID(int=uuid.getnode()))
            
            # Get hostname
            hostname = platform.node()
            
            # Combine for unique ID
            uid = f"{machine_uuid}-{hostname}"
            
            return uid
        except Exception as e:
            error("LicenseActivation", f"Error getting machine UID: {e}")
            return str(uuid.uuid4())
    
    def activate_trial(self, machine_uid: str = None, user_id: Optional[int] = None) -> Tuple[bool, str]:
        """
        Activate 30-day trial using centralized database
        
        Args:
            machine_uid: Machine UID (optional, will auto-detect)
            user_id: User ID (optional)
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not machine_uid:
            machine_uid = self.get_machine_uid()
        
        debug("LicenseActivation", f"Activating trial for machine: {machine_uid}")
        
        # Use centralized database through DatabaseManager
        return db.activate_trial(machine_uid, user_id)
    
    def check_trial_status(self, machine_uid: str = None) -> Dict:
        """
        Check trial status using centralized database
        
        Args:
            machine_uid: Machine UID (optional, will auto-detect)
        
        Returns:
            Dict with status info
        """
        if not machine_uid:
            machine_uid = self.get_machine_uid()
        
        debug("LicenseActivation", f"Checking trial status for machine: {machine_uid}")
        
        # Use centralized database through DatabaseManager
        return db.check_trial_status(machine_uid)
    
    def submit_license_application(
        self,
        name: str,
        company: str,
        email: str,
        requested_tier: str,
        machine_uid: str = None,
        user_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Submit license application using centralized database
        
        Args:
            name: Applicant name
            company: Company name
            email: Email address
            requested_tier: Requested license tier
            machine_uid: Machine UID (optional)
            user_id: User ID (optional)
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not machine_uid:
            machine_uid = self.get_machine_uid()
        
        debug("LicenseActivation", f"Submitting license application for: {email}")
        
        # Use centralized database through DatabaseManager
        success, message = db.create_license_application(
            user_id, machine_uid, name, company, email, requested_tier
        )
        
        if success:
            # Send confirmation email
            if self.email_service:
                try:
                    self.email_service.send_application_confirmation(
                        to_email=email,
                        name=name,
                        tier=requested_tier,
                        machine_uid=machine_uid
                    )
                    info("LicenseActivation", f"Confirmation email sent to {email}")
                except Exception as e:
                    warning("LicenseActivation", f"Failed to send confirmation email: {e}")
        
        return success, message
    
    def validate_license_key(self, license_key: str, machine_uid: str = None) -> tuple:
        """
        Validate license key format and check against database
        
        Args:
            license_key: License key to validate (XXXX-XXXX-XXXX-XXXX)
            machine_uid: Machine UID (optional)
            
        Returns:
            tuple: (is_valid, message, tier)
        """
        if not machine_uid:
            machine_uid = self.get_machine_uid()
        
        # Validate format
        if not license_key or len(license_key) != 19:
            return False, "Invalid license key format", None
        
        parts = license_key.split('-')
        if len(parts) != 4 or not all(len(p) == 4 for p in parts):
            return False, "Invalid license key format (must be XXXX-XXXX-XXXX-XXXX)", None
        
        if not all(c.isalnum() for part in parts for c in part):
            return False, "Invalid characters in license key", None
        
        # Check against database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT requested_tier, status, machine_uid
                FROM license_applications
                WHERE license_key = ?
            """, (license_key,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return False, "License key not found", None
            
            tier, status, db_machine_uid = result
            
            if status != 'approved':
                return False, f"License key is {status}", None
            
            # Check if key is for this machine
            if db_machine_uid != machine_uid:
                return False, "License key is not valid for this machine", None
            
            info("LicenseActivation", f"License key validated: {license_key}")
            return True, "License key is valid", tier
            
        except Exception as e:
            error("LicenseActivation", f"Error validating license key: {e}")
            return False, f"Validation error: {e}", None
    
    def activate_license_key(self, license_key: str, user_id: int, machine_uid: str = None) -> tuple:
        """
        Activate a license key for a user
        
        Args:
            license_key: License key to activate
            user_id: User ID
            machine_uid: Machine UID (optional)
            
        Returns:
            tuple: (success, message, tier)
        """
        # Validate key first
        is_valid, message, tier = self.validate_license_key(license_key, machine_uid)
        
        if not is_valid:
            return False, message, None
        
        # Activate license
        from core.license_system import LicenseSystem
        
        try:
            license_system = LicenseSystem(user_id=user_id)
            
            # Generate license with the approved tier
            license_system.upgrade_license(tier, duration_days=365)
            
            info("LicenseActivation", f"License activated for user {user_id}: {tier}")
            return True, f"License activated successfully! Tier: {tier.title()}", tier
            
        except Exception as e:
            error("LicenseActivation", f"Error activating license: {e}")
            return False, f"Activation failed: {e}", None
    
    def get_all_applications(self, status_filter: str = None) -> list:
        """
        Get all license applications (for admin)
        
        Args:
            status_filter: Filter by status (pending, approved, rejected)
            
        Returns:
            List of applications
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if status_filter:
                cursor.execute("""
                    SELECT * FROM license_applications
                    WHERE status = ?
                    ORDER BY created_at DESC
                """, (status_filter,))
            else:
                cursor.execute("""
                    SELECT * FROM license_applications
                    ORDER BY created_at DESC
                """)
            
            applications = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            debug("LicenseActivation", f"Retrieved {len(applications)} applications")
            return applications
            
        except Exception as e:
            error("LicenseActivation", f"Error getting applications: {e}")
            return []
    
    def process_application(
        self,
        application_id: int,
        status: str,
        payment_status: str,
        license_key: str = None,
        notes: str = None,
        processed_by: int = None
    ) -> Tuple[bool, str]:
        """
        Process license application (admin function)
        
        Args:
            application_id: Application ID
            status: New status (approved, rejected, pending)
            payment_status: Payment status (paid, unpaid, pending)
            license_key: Generated license key (optional)
            notes: Admin notes (optional)
            processed_by: Admin user ID
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get application details for email
            cursor.execute("""
                SELECT name, email, requested_tier
                FROM license_applications
                WHERE id = ?
            """, (application_id,))
            
            app_data = cursor.fetchone()
            
            if not app_data:
                conn.close()
                return False, "Application not found"
            
            name, email, tier = app_data
            
            # Update application
            cursor.execute("""
                UPDATE license_applications
                SET status = ?, payment_status = ?, license_key = ?, notes = ?,
                    processed_at = ?, processed_by = ?
                WHERE id = ?
            """, (status, payment_status, license_key, notes, 
                  datetime.now().isoformat(), processed_by, application_id))
            
            conn.commit()
            conn.close()
            
            # Send email notification
            if self.email_service:
                try:
                    if status == 'approved' and license_key:
                        self.email_service.send_approval_notification(
                            to_email=email,
                            name=name,
                            tier=tier,
                            license_key=license_key
                        )
                        info("LicenseActivation", f"Approval email sent to {email}")
                    elif status == 'rejected':
                        self.email_service.send_rejection_notification(
                            to_email=email,
                            name=name,
                            reason=notes
                        )
                        info("LicenseActivation", f"Rejection email sent to {email}")
                except Exception as e:
                    warning("LicenseActivation", f"Failed to send email: {e}")
            
            info("LicenseActivation", f"Application {application_id} processed: {status}")
            return True, "Application processed successfully"
            
        except Exception as e:
            error("LicenseActivation", f"Error processing application: {e}")
            return False, f"Failed to process application: {e}"
    def _hash_license_key(self, license_key: str) -> str:
        """Create secure hash of license key"""
        import hashlib
        return hashlib.sha256(license_key.encode()).hexdigest()
    
    def validate_license(self, license_key: str, machine_uid: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Validate license key against machine UID
        
        Args:
            license_key: License key to validate
            machine_uid: Machine UID to check
            
        Returns:
            Tuple[bool, str, Optional[Dict]]: (is_valid, message, license_data)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Hash the license key
            key_hash = self._hash_license_key(license_key)
            
            # Check active licenses
            cursor.execute("""
                SELECT * FROM active_licenses
                WHERE license_key_hash = ? AND is_active = 1
            """, (key_hash,))
            
            license_data = cursor.fetchone()
            
            if not license_data:
                conn.close()
                return False, "Invalid or inactive license key", None
            
            # Check if machine UID matches
            if license_data['machine_uid'] != machine_uid:
                conn.close()
                warning("LicenseActivation", f"License key used on different machine: {license_key[:8]}...")
                return False, "License key is registered to a different machine", None
            
            # Update validation timestamp and count
            cursor.execute("""
                UPDATE active_licenses
                SET last_validated = ?, validation_count = validation_count + 1
                WHERE license_key_hash = ?
            """, (datetime.now().isoformat(), key_hash))
            
            conn.commit()
            conn.close()
            
            info("LicenseActivation", f"License validated successfully: {license_key[:8]}...")
            return True, "License is valid", dict(license_data)
            
        except Exception as e:
            error("LicenseActivation", f"License validation error: {e}")
            return False, f"Validation error: {e}", None
    
    def activate_license(self, license_key: str, machine_uid: str, application_id: int) -> Tuple[bool, str]:
        """
        Activate a license key for a machine
        
        Args:
            license_key: License key to activate
            machine_uid: Machine UID
            application_id: Application ID
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get application data
            cursor.execute("""
                SELECT email, company, requested_tier
                FROM license_applications
                WHERE id = ?
            """, (application_id,))
            
            app_data = cursor.fetchone()
            if not app_data:
                conn.close()
                return False, "Application not found"
            
            # Hash the license key
            key_hash = self._hash_license_key(license_key)
            
            # Check if already activated
            cursor.execute("""
                SELECT id FROM active_licenses
                WHERE license_key_hash = ?
            """, (key_hash,))
            
            if cursor.fetchone():
                conn.close()
                return False, "License key already activated"
            
            # Insert into active licenses
            cursor.execute("""
                INSERT INTO active_licenses (
                    license_key, license_key_hash, machine_uid,
                    email, company, tier, activated_at,
                    last_validated, application_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                license_key, key_hash, machine_uid,
                app_data['email'], app_data['company'], app_data['requested_tier'],
                datetime.now().isoformat(), datetime.now().isoformat(),
                application_id
            ))
            
            conn.commit()
            conn.close()
            
            info("LicenseActivation", f"License activated: {license_key[:8]}... for {machine_uid[:16]}...")
            return True, "License activated successfully"
            
        except Exception as e:
            error("LicenseActivation", f"License activation error: {e}")
            return False, f"Activation failed: {e}"
    
    def request_migration(self, old_license_key: str, old_machine_uid: str, 
                         new_machine_uid: str, email: str, company: str, 
                         reason: str) -> Tuple[bool, str]:
        """
        Request license migration to new machine
        
        Args:
            old_license_key: Current license key
            old_machine_uid: Old machine UID
            new_machine_uid: New machine UID
            email: User email
            company: Company name
            reason: Migration reason
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Validate old license
            key_hash = self._hash_license_key(old_license_key)
            cursor.execute("""
                SELECT id, machine_uid FROM active_licenses
                WHERE license_key_hash = ? AND is_active = 1
            """, (key_hash,))
            
            old_license = cursor.fetchone()
            if not old_license:
                conn.close()
                return False, "Invalid or inactive license key"
            
            if old_license[1] != old_machine_uid:
                conn.close()
                return False, "License key does not match machine UID"
            
            # Create migration request
            cursor.execute("""
                INSERT INTO license_migrations (
                    old_license_key, old_machine_uid, new_machine_uid,
                    email, company, reason, requested_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                old_license_key, old_machine_uid, new_machine_uid,
                email, company, reason, datetime.now().isoformat()
            ))
            
            migration_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            info("LicenseActivation", f"Migration request created: {migration_id}")
            return True, f"Migration request submitted (ID: {migration_id})"
            
        except Exception as e:
            error("LicenseActivation", f"Migration request error: {e}")
            return False, f"Failed to create migration request: {e}"
    
    def process_migration(self, migration_id: int, approved: bool, 
                         processed_by: int, notes: str = "") -> Tuple[bool, str]:
        """
        Process license migration request (admin only)
        
        Args:
            migration_id: Migration request ID
            approved: Whether to approve migration
            processed_by: Admin user ID
            notes: Processing notes
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get migration request
            cursor.execute("""
                SELECT * FROM license_migrations WHERE id = ?
            """, (migration_id,))
            
            migration = cursor.fetchone()
            if not migration:
                conn.close()
                return False, "Migration request not found"
            
            if not approved:
                # Reject migration
                cursor.execute("""
                    UPDATE license_migrations
                    SET status = 'rejected', processed_at = ?, 
                        processed_by = ?, notes = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), processed_by, notes, migration_id))
                conn.commit()
                conn.close()
                return True, "Migration request rejected"
            
            # Approve migration - create new license
            # Get old license data
            old_key_hash = self._hash_license_key(migration['old_license_key'])
            cursor.execute("""
                SELECT * FROM active_licenses
                WHERE license_key_hash = ?
            """, (old_key_hash,))
            
            old_license = cursor.fetchone()
            if not old_license:
                conn.close()
                return False, "Old license not found"
            
            # Generate new license key
            import hashlib
            import secrets
            seed = f"{migration['new_machine_uid']}-{old_license['tier']}-{datetime.now().isoformat()}-{secrets.token_hex(8)}"
            hash_obj = hashlib.sha256(seed.encode())
            hash_hex = hash_obj.hexdigest()
            
            tier_prefix = old_license['tier'][:3].upper()
            new_license_key = f"{tier_prefix}-{hash_hex[0:4].upper()}-{hash_hex[4:8].upper()}-{hash_hex[8:12].upper()}-{hash_hex[12:16].upper()}"
            new_key_hash = self._hash_license_key(new_license_key)
            
            # Create new application (merged data)
            cursor.execute("""
                INSERT INTO license_applications (
                    machine_uid, name, company, email, requested_tier,
                    status, payment_status, created_at, processed_at,
                    processed_by, license_key, license_key_hash, notes
                ) VALUES (?, ?, ?, ?, ?, 'approved', 'paid', ?, ?, ?, ?, ?, ?)
            """, (
                migration['new_machine_uid'],
                migration['company'],  # Use company as name
                migration['company'],
                migration['email'],
                old_license['tier'],
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                processed_by,
                new_license_key,
                new_key_hash,
                f"Migrated from {migration['old_license_key'][:8]}... - Reason: {migration['reason']}"
            ))
            
            new_app_id = cursor.lastrowid
            
            # Create new active license
            cursor.execute("""
                INSERT INTO active_licenses (
                    license_key, license_key_hash, machine_uid,
                    email, company, tier, activated_at,
                    last_validated, application_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                new_license_key, new_key_hash, migration['new_machine_uid'],
                migration['email'], migration['company'], old_license['tier'],
                datetime.now().isoformat(), datetime.now().isoformat(),
                new_app_id
            ))
            
            # Deactivate old license
            cursor.execute("""
                UPDATE active_licenses
                SET is_active = 0
                WHERE license_key_hash = ?
            """, (old_key_hash,))
            
            # Mark old application as migrated
            cursor.execute("""
                UPDATE license_applications
                SET is_migrated = 1, migrated_to = ?, 
                    migration_reason = ?
                WHERE license_key = ?
            """, (new_app_id, migration['reason'], migration['old_license_key']))
            
            # Update migration request
            cursor.execute("""
                UPDATE license_migrations
                SET status = 'approved', processed_at = ?,
                    processed_by = ?, new_license_key = ?,
                    new_application_id = ?, notes = ?
                WHERE id = ?
            """, (
                datetime.now().isoformat(), processed_by,
                new_license_key, new_app_id, notes, migration_id
            ))
            
            conn.commit()
            conn.close()
            
            info("LicenseActivation", f"Migration approved: {migration_id} -> New license: {new_license_key}")
            return True, f"Migration approved. New license key: {new_license_key}"
            
        except Exception as e:
            error("LicenseActivation", f"Migration processing error: {e}")
            return False, f"Failed to process migration: {e}"


# Debug logging
debug("LicenseActivation", "License activation module loaded")

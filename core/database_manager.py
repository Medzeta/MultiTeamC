"""
Database Manager - Centraliserad databashantering för Multi Team -C
Säkerställer att alla moduler använder samma databas-instans
"""

import sqlite3
import bcrypt
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from core.debug_logger import debug, info, warning, error, exception
from core.security_manager import security_manager


class DatabaseManager:
    """
    Centraliserad databas-manager som hanterar alla databas-operationer
    Säkerställer konsistens mellan alla moduler
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern - endast en databas-instans"""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize database manager (endast en gång)"""
        if not DatabaseManager._initialized:
            debug("DatabaseManager", "Initializing centralized database manager")
            
            self.db_path = Path("data/multiteam.db")
            self._setup_database()
            
            DatabaseManager._initialized = True
            info("DatabaseManager", "Centralized database manager initialized")
    
    def _setup_database(self):
        """Skapa databas och alla tabeller"""
        debug("DatabaseManager", "Setting up centralized database")
        
        # Skapa data directory
        self.db_path.parent.mkdir(exist_ok=True)
        debug("DatabaseManager", f"Database directory: {self.db_path.parent.absolute()}")
        
        # Skapa krypterad databas med SQLCipher-kompatibel kryptering
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Aktivera kryptering med säker nyckel från SecurityManager
        db_key = security_manager.get_database_key()
        cursor.execute(f"PRAGMA key = '{db_key}'")
        debug("DatabaseManager", "Database encryption enabled")
        
        # Users tabell med 2FA support
        debug("DatabaseManager", "Creating users table with 2FA support")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                company TEXT NOT NULL,
                verified INTEGER DEFAULT 0,
                verification_code TEXT,
                twofa_enabled INTEGER DEFAULT 0,
                twofa_secret TEXT,
                twofa_backup_codes TEXT,
                twofa_qr_code BLOB,
                twofa_email_sent_at TIMESTAMP,
                twofa_email_backup_codes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Sessions tabell
        debug("DatabaseManager", "Creating sessions table")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Reset tokens tabell
        debug("DatabaseManager", "Creating reset_tokens table")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                token TEXT NOT NULL,
                expiry TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # LICENSE SYSTEM TABLES - Integrerade i centrala databasen
        debug("DatabaseManager", "Creating license system tables")
        
        # License applications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS license_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                machine_uid TEXT NOT NULL,
                name TEXT NOT NULL,
                company TEXT NOT NULL,
                email TEXT NOT NULL,
                requested_tier TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                payment_status TEXT DEFAULT 'unpaid',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                processed_by INTEGER,
                license_key TEXT UNIQUE,
                license_key_hash TEXT,
                notes TEXT,
                is_migrated INTEGER DEFAULT 0,
                migrated_to INTEGER,
                migration_reason TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (processed_by) REFERENCES users (id)
            )
        """)
        
        # Active licenses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS active_licenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                license_key TEXT NOT NULL UNIQUE,
                license_key_hash TEXT NOT NULL UNIQUE,
                machine_uid TEXT NOT NULL,
                email TEXT NOT NULL,
                company TEXT NOT NULL,
                tier TEXT NOT NULL,
                activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                last_validated TIMESTAMP,
                validation_count INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                application_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (application_id) REFERENCES license_applications(id)
            )
        """)
        
        # License migration requests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS license_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                old_license_key TEXT NOT NULL,
                old_machine_uid TEXT NOT NULL,
                new_machine_uid TEXT NOT NULL,
                email TEXT NOT NULL,
                company TEXT NOT NULL,
                reason TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                processed_by INTEGER,
                new_license_key TEXT,
                new_application_id INTEGER,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (processed_by) REFERENCES users (id)
            )
        """)
        
        # Trial activations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trial_activations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                machine_uid TEXT NOT NULL UNIQUE,
                activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        conn.commit()
        # Migrera befintliga databaser - lägg till nya 2FA-kolumner om de saknas
        debug("DatabaseManager", "Checking for database migrations")
        try:
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'twofa_qr_code' not in columns:
                debug("DatabaseManager", "Adding twofa_qr_code column")
                cursor.execute("ALTER TABLE users ADD COLUMN twofa_qr_code BLOB")
                
            if 'twofa_email_sent_at' not in columns:
                debug("DatabaseManager", "Adding twofa_email_sent_at column")
                cursor.execute("ALTER TABLE users ADD COLUMN twofa_email_sent_at TIMESTAMP")
                
            if 'twofa_email_backup_codes' not in columns:
                debug("DatabaseManager", "Adding twofa_email_backup_codes column")
                cursor.execute("ALTER TABLE users ADD COLUMN twofa_email_backup_codes TEXT")
                
            conn.commit()
            info("DatabaseManager", "Database migrations completed")
        except Exception as e:
            warning("DatabaseManager", f"Migration check failed (may be expected): {e}")
        
        conn.close()
        
        info("DatabaseManager", "Database setup completed")
    
    def _get_connection(self):
        """Hämta krypterad databasanslutning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Aktivera kryptering
        db_key = security_manager.get_database_key()
        cursor.execute(f"PRAGMA key = '{db_key}'")
        
        return conn
    
    def get_connection(self):
        """Få krypterad databas-anslutning"""
        return self._get_connection()
    
    # USER OPERATIONS
    def create_user(self, email: str, password: str, name: str, company: str, verification_code: str) -> bool:
        """Skapa ny användare"""
        debug("DatabaseManager", f"Creating user: {email}")
        
        try:
            # Använd SecurityManager för säker lösenordshashing
            hashed_password = security_manager.hash_password(password)
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO users (email, password_hash, name, company, verification_code)
                VALUES (?, ?, ?, ?, ?)
            """, (email, hashed_password, name, company, verification_code))
            
            conn.commit()
            conn.close()
            
            info("DatabaseManager", f"User created successfully: {email}")
            return True
            
        except sqlite3.IntegrityError:
            warning("DatabaseManager", f"User already exists: {email}")
            return False
        except Exception as e:
            exception("DatabaseManager", f"Error creating user: {email}")
            return False
    
    def register_user(self, email: str, password: str, name: str, company: str, verification_code: str) -> bool:
        """Alias för create_user - registrera ny användare"""
        return self.create_user(email, password, name, company, verification_code)
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Hämta användare via email"""
        debug("DatabaseManager", f"Getting user by email: {email}")
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, email, password_hash, name, company, verified, 
                       twofa_enabled, twofa_secret, twofa_backup_codes
                FROM users WHERE email = ?
            """, (email,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                user_id, email, password_hash, name, company, verified, twofa_enabled, twofa_secret, twofa_backup_codes = result
                return {
                    "id": user_id,
                    "email": email,
                    "password_hash": password_hash,
                    "name": name,
                    "company": company,
                    "verified": bool(verified),
                    "twofa_enabled": bool(twofa_enabled),
                    "twofa_secret": twofa_secret,
                    "twofa_backup_codes": twofa_backup_codes
                }
            else:
                debug("DatabaseManager", f"User not found: {email}")
                return None
                
        except Exception as e:
            exception("DatabaseManager", f"Error getting user {email}: {e}")
            return None
    
    def verify_user(self, email: str, code: str) -> bool:
        """Verifiera användare med kod"""
        debug("DatabaseManager", f"Verifying user: {email}")
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, verification_code FROM users WHERE email = ?
            """, (email,))
            
            result = cursor.fetchone()
            if not result:
                warning("DatabaseManager", f"User not found for verification: {email}")
                conn.close()
                return False
            
            user_id, stored_code = result
            
            if stored_code == code:
                cursor.execute("""
                    UPDATE users SET verified = 1, verification_code = NULL WHERE id = ?
                """, (user_id,))
                conn.commit()
                conn.close()
                info("DatabaseManager", f"User verified successfully: {email}")
                return True
            else:
                warning("DatabaseManager", f"Verification code mismatch for: {email}")
                conn.close()
                return False
                
        except Exception as e:
            exception("DatabaseManager", f"Error verifying user {email}: {e}")
            return False
    
    def verify_user_email(self, email: str, code: str) -> bool:
        """Alias för verify_user - verifiera användarens email"""
        return self.verify_user(email, code)
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Autentisera användare"""
        debug("DatabaseManager", f"Authenticating user: {email}")
        
        user = self.get_user_by_email(email)
        if not user:
            debug("DatabaseManager", f"User not found: {email}")
            return None
        
        if not user["verified"]:
            warning("DatabaseManager", f"User not verified: {email}")
            return None
        
        # Kontrollera lösenord med SecurityManager
        if security_manager.verify_password(password, user["password_hash"]):
            info("DatabaseManager", f"User authenticated successfully: {email}")
            return user
        else:
            warning("DatabaseManager", f"Invalid password for: {email}")
            return None
    
    def update_user_password(self, email: str, new_password: str) -> bool:
        """Uppdatera användarens lösenord"""
        debug("DatabaseManager", f"Updating password for user: {email}")
        
        try:
            # Använd SecurityManager för säker lösenordshashing
            hashed_password = security_manager.hash_password(new_password)
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users SET password_hash = ? WHERE email = ?
            """, (hashed_password, email))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                info("DatabaseManager", f"Password updated successfully for: {email}")
                return True
            else:
                warning("DatabaseManager", f"No user found with email: {email}")
                conn.close()
                return False
                
        except Exception as e:
            exception("DatabaseManager", f"Error updating password for {email}: {e}")
            return False
    
    # RESET TOKEN OPERATIONS
    def save_reset_token(self, email: str, token: str, expiry: datetime) -> bool:
        """Spara reset token"""
        debug("DatabaseManager", f"Saving reset token for: {email}")
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Ta bort gamla tokens för denna email
            cursor.execute("DELETE FROM reset_tokens WHERE email = ?", (email,))
            
            # Spara ny token
            cursor.execute("""
                INSERT INTO reset_tokens (email, token, expiry)
                VALUES (?, ?, ?)
            """, (email, token, expiry))
            
            conn.commit()
            conn.close()
            
            debug("DatabaseManager", f"Reset token saved for {email}")
            return True
            
        except Exception as e:
            exception("DatabaseManager", f"Error saving reset token: {e}")
            return False
    
    def verify_reset_token(self, email: str, token: str) -> bool:
        """Verifiera reset token"""
        debug("DatabaseManager", f"Verifying reset token for: {email}")
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT expiry FROM reset_tokens WHERE email = ? AND token = ?
            """, (email, token))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                warning("DatabaseManager", f"Reset token not found for {email}")
                return False
            
            expiry_str = result[0]
            expiry = datetime.fromisoformat(expiry_str)
            
            if datetime.now() > expiry:
                warning("DatabaseManager", f"Reset token expired for {email}")
                return False
            
            debug("DatabaseManager", f"Reset token verified for {email}")
            return True
            
        except Exception as e:
            exception("DatabaseManager", f"Error verifying reset token: {e}")
            return False
    
    def delete_reset_token(self, email: str) -> bool:
        """Ta bort reset token"""
        debug("DatabaseManager", f"Deleting reset token for: {email}")
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM reset_tokens WHERE email = ?", (email,))
            
            conn.commit()
            conn.close()
            
            debug("DatabaseManager", f"Reset token deleted for {email}")
            return True
            
        except Exception as e:
            exception("DatabaseManager", f"Error deleting reset token: {e}")
            return False
    
    # 2FA OPERATIONS
    def enable_2fa_for_user(self, user_id: int, secret: str, backup_codes: List[str]) -> bool:
        """Aktivera 2FA för användare"""
        debug("DatabaseManager", f"Enabling 2FA for user ID: {user_id}")
        
        try:
            import json
            backup_codes_json = json.dumps(backup_codes)
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users 
                SET twofa_enabled = 1, 
                    twofa_secret = ?, 
                    twofa_backup_codes = ?
                WHERE id = ?
            """, (secret, backup_codes_json, user_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                info("DatabaseManager", f"2FA enabled for user ID: {user_id}")
                return True
            else:
                warning("DatabaseManager", f"No user found with ID: {user_id}")
                conn.close()
                return False
                
        except Exception as e:
            exception("DatabaseManager", f"Error enabling 2FA for user {user_id}: {e}")
            return False
    
    def disable_2fa_for_user(self, user_id: int) -> bool:
        """Inaktivera 2FA för användare"""
        debug("DatabaseManager", f"Disabling 2FA for user ID: {user_id}")
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users 
                SET twofa_enabled = 0, 
                    twofa_secret = NULL, 
                    twofa_backup_codes = NULL
                WHERE id = ?
            """, (user_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                info("DatabaseManager", f"2FA disabled for user ID: {user_id}")
                return True
            else:
                warning("DatabaseManager", f"No user found with ID: {user_id}")
                conn.close()
                return False
                
        except Exception as e:
            exception("DatabaseManager", f"Error disabling 2FA for user {user_id}: {e}")
            return False
    
    def get_user_2fa_status(self, user_id: int) -> tuple:
        """Hämta användarens 2FA status"""
        debug("DatabaseManager", f"Getting 2FA status for user ID: {user_id}")
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT twofa_enabled, twofa_secret, twofa_backup_codes
                FROM users 
                WHERE id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                enabled = bool(result[0])
                secret = result[1]
                backup_codes_json = result[2]
                
                backup_codes = []
                if backup_codes_json:
                    import json
                    backup_codes = json.loads(backup_codes_json)
                
                debug("DatabaseManager", f"2FA status: enabled={enabled}, has_secret={secret is not None}")
                return enabled, secret, backup_codes
            else:
                warning("DatabaseManager", f"User not found: {user_id}")
                return False, None, []
                
        except Exception as e:
            exception("DatabaseManager", f"Error getting 2FA status for user {user_id}: {e}")
            return False, None, []
    
    def verify_backup_code(self, user_id: int, code: str) -> bool:
        """Verifiera och förbruka backup code"""
        debug("DatabaseManager", f"Verifying backup code for user ID: {user_id}")
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT twofa_backup_codes 
                FROM users 
                WHERE id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            
            if not result or not result[0]:
                warning("DatabaseManager", "No backup codes found")
                conn.close()
                return False
            
            import json
            backup_codes = json.loads(result[0])
            
            if code.upper() in backup_codes:
                # Ta bort använd kod
                backup_codes.remove(code.upper())
                
                # Uppdatera databas
                cursor.execute("""
                    UPDATE users 
                    SET twofa_backup_codes = ?
                    WHERE id = ?
                """, (json.dumps(backup_codes), user_id))
                
                conn.commit()
                conn.close()
                
                info("DatabaseManager", f"Backup code verified and consumed for user {user_id}")
                return True
            else:
                debug("DatabaseManager", f"Backup code not found for user {user_id}")
                return False
                
        except Exception as e:
            exception("DatabaseManager", f"Error verifying backup code: {e}")
            return False
    
    def save_2fa_email_data(self, user_id: int, qr_code_bytes: bytes, backup_codes: list) -> bool:
        """Spara 2FA email-data för framtida återanvändning"""
        debug("DatabaseManager", f"Saving 2FA email data for user ID: {user_id}")
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Konvertera backup codes till JSON
            import json
            from datetime import datetime
            backup_codes_json = json.dumps(backup_codes)
            current_time = datetime.now().isoformat()
            
            cursor.execute("""
                UPDATE users 
                SET twofa_qr_code = ?,
                    twofa_email_sent_at = ?,
                    twofa_email_backup_codes = ?
                WHERE id = ?
            """, (qr_code_bytes, current_time, backup_codes_json, user_id))
            
            conn.commit()
            conn.close()
            
            info("DatabaseManager", f"2FA email data saved for user ID: {user_id}")
            return True
            
        except Exception as e:
            exception("DatabaseManager", f"Error saving 2FA email data: {e}")
            return False
    
    def get_2fa_email_data(self, user_id: int) -> tuple:
        """Hämta sparad 2FA email-data"""
        debug("DatabaseManager", f"Getting 2FA email data for user ID: {user_id}")
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT twofa_secret, twofa_qr_code, twofa_email_backup_codes, twofa_email_sent_at
                FROM users 
                WHERE id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                secret, qr_bytes, backup_codes_json, sent_at = result
                
                # Konvertera backup codes från JSON
                import json
                backup_codes = json.loads(backup_codes_json) if backup_codes_json else []
                
                debug("DatabaseManager", f"Retrieved 2FA email data for user ID: {user_id}")
                return secret, qr_bytes, backup_codes, sent_at
            else:
                debug("DatabaseManager", f"No 2FA email data found for user ID: {user_id}")
                return None, None, [], None
                
        except Exception as e:
            exception("DatabaseManager", f"Error getting 2FA email data: {e}")
            return None, None, [], None
    
    # LICENSE SYSTEM METHODS - Integrerade i centrala databasen
    def activate_trial(self, machine_uid: str, user_id: Optional[int] = None) -> Tuple[bool, str]:
        """
        Aktivera 30-dagars trial för maskin
        
        Args:
            machine_uid: Unik maskin-identifierare
            user_id: Användar-ID (optional)
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        debug("DatabaseManager", f"Activating trial for machine: {machine_uid}")
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Kontrollera om trial redan är aktiverad
            cursor.execute("""
                SELECT status, expires_at FROM trial_activations
                WHERE machine_uid = ?
            """, (machine_uid,))
            
            existing = cursor.fetchone()
            
            if existing:
                status, expires_at = existing
                
                if status == 'active':
                    # Kontrollera om trial fortfarande är giltig
                    expires_dt = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                    if expires_dt > datetime.now():
                        days_left = (expires_dt - datetime.now()).days
                        conn.close()
                        return False, f"Trial already active ({days_left} days remaining)"
                    else:
                        # Trial har gått ut
                        cursor.execute("""
                            UPDATE trial_activations 
                            SET status = 'expired'
                            WHERE machine_uid = ?
                        """, (machine_uid,))
                        conn.commit()
                        conn.close()
                        return False, "Trial has expired"
            
            # Aktivera ny trial
            activated_at = datetime.now()
            expires_at = activated_at + timedelta(days=30)
            
            cursor.execute("""
                INSERT OR REPLACE INTO trial_activations 
                (user_id, machine_uid, activated_at, expires_at, status)
                VALUES (?, ?, ?, ?, 'active')
            """, (user_id, machine_uid, activated_at.isoformat(), expires_at.isoformat()))
            
            conn.commit()
            conn.close()
            
            info("DatabaseManager", f"Trial activated for machine: {machine_uid}")
            return True, f"30-day trial activated successfully"
            
        except Exception as e:
            exception("DatabaseManager", f"Error activating trial: {e}")
            return False, f"Error activating trial: {str(e)}"
    
    def check_trial_status(self, machine_uid: str) -> Dict:
        """
        Kontrollera trial-status för maskin
        
        Args:
            machine_uid: Unik maskin-identifierare
            
        Returns:
            Dict: Trial status information
        """
        debug("DatabaseManager", f"Checking trial status for machine: {machine_uid}")
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT status, activated_at, expires_at FROM trial_activations
                WHERE machine_uid = ?
            """, (machine_uid,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return {
                    "has_trial": False,
                    "status": "none",
                    "message": "No trial activated",
                    "days_left": 0
                }
            
            status, activated_at, expires_at = result
            
            # Beräkna dagar kvar
            expires_dt = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            days_left = max(0, (expires_dt - datetime.now()).days)
            
            if status == 'active' and days_left > 0:
                return {
                    "has_trial": True,
                    "status": "active",
                    "message": f"Trial active ({days_left} days remaining)",
                    "days_left": days_left,
                    "expires_at": expires_at
                }
            else:
                return {
                    "has_trial": True,
                    "status": "expired",
                    "message": "Trial has expired",
                    "days_left": 0,
                    "expires_at": expires_at
                }
                
        except Exception as e:
            exception("DatabaseManager", f"Error checking trial status: {e}")
            return {
                "has_trial": False,
                "status": "error",
                "message": f"Error checking trial: {str(e)}",
                "days_left": 0
            }
    
    def create_license_application(self, user_id: Optional[int], machine_uid: str, 
                                 name: str, company: str, email: str, 
                                 requested_tier: str) -> Tuple[bool, str]:
        """
        Skapa licensansökan
        
        Args:
            user_id: Användar-ID (optional)
            machine_uid: Maskin-UID
            name: Namn
            company: Företag
            email: Email
            requested_tier: Begärd licensnivå
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        debug("DatabaseManager", f"Creating license application for: {email}")
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO license_applications 
                (user_id, machine_uid, name, company, email, requested_tier)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, machine_uid, name, company, email, requested_tier))
            
            conn.commit()
            conn.close()
            
            info("DatabaseManager", f"License application created for: {email}")
            return True, "License application submitted successfully"
            
        except Exception as e:
            exception("DatabaseManager", f"Error creating license application: {e}")
            return False, f"Error submitting application: {str(e)}"
    
    def get_user_licenses(self, user_id: int) -> List[Dict]:
        """
        Hämta alla licenser för användare
        
        Args:
            user_id: Användar-ID
            
        Returns:
            List[Dict]: Lista med licensinformation
        """
        debug("DatabaseManager", f"Getting licenses for user ID: {user_id}")
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, license_key, machine_uid, tier, activated_at, 
                       expires_at, is_active, validation_count
                FROM active_licenses
                WHERE user_id = ? AND is_active = 1
            """, (user_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            licenses = []
            for result in results:
                license_id, license_key, machine_uid, tier, activated_at, expires_at, is_active, validation_count = result
                licenses.append({
                    "id": license_id,
                    "license_key": license_key[:8] + "..." if license_key else None,  # Maskerad nyckel
                    "machine_uid": machine_uid,
                    "tier": tier,
                    "activated_at": activated_at,
                    "expires_at": expires_at,
                    "is_active": bool(is_active),
                    "validation_count": validation_count
                })
            
            debug("DatabaseManager", f"Found {len(licenses)} licenses for user ID: {user_id}")
            return licenses
            
        except Exception as e:
            exception("DatabaseManager", f"Error getting user licenses: {e}")
            return []


# Singleton instance
db = DatabaseManager()


# Export
__all__ = ['DatabaseManager', 'db']

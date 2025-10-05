"""
Security Manager - Hanterar kryptering och säkerhet för Multi Team -C
Implementerar databaskryptering, lösenordshashing och nyckelhantering
"""

import os
import hashlib
import bcrypt
import secrets
from pathlib import Path
from typing import Dict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from core.debug_logger import debug, info, warning, error, exception


class SecurityManager:
    """
    Centraliserad säkerhetshantering för Multi Team -C
    Hanterar kryptering, lösenordshashing och nyckelhantering
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern - endast en säkerhetsinstans"""
        if cls._instance is None:
            cls._instance = super(SecurityManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize security manager (endast en gång)"""
        if not self._initialized:
            debug("SecurityManager", "Initializing security manager")
            
            # Säkerhetskonfiguration
            self.data_dir = Path("data")
            self.data_dir.mkdir(exist_ok=True)
            
            # Krypterings-konfiguration
            self.key_file = self.data_dir / "master.key"
            self.salt_file = self.data_dir / "salt.key"
            
            # Initialisera kryptering
            self._initialize_encryption()
            
            SecurityManager._initialized = True
            info("SecurityManager", "Security manager initialized successfully")
    
    def _initialize_encryption(self):
        """Initialisera krypteringsnycklar"""
        debug("SecurityManager", "Initializing encryption keys")
        
        # Skapa master key om den inte finns
        if not self.key_file.exists():
            debug("SecurityManager", "Generating new master key")
            self._generate_master_key()
        
        # Skapa salt om den inte finns
        if not self.salt_file.exists():
            debug("SecurityManager", "Generating new salt")
            self._generate_salt()
        
        # Ladda nycklar
        self._load_keys()
        
        debug("SecurityManager", "Encryption keys initialized")
    
    def _generate_master_key(self):
        """Generera ny master key för databaskryptering"""
        debug("SecurityManager", "Generating master encryption key")
        
        # Använd maskinspecifik information för att skapa unik nyckel
        machine_info = f"{os.environ.get('COMPUTERNAME', 'unknown')}"
        machine_info += f"{os.environ.get('USERNAME', 'unknown')}"
        
        # Skapa password från maskininfo + random salt
        password = f"MultiTeam-{machine_info}-{secrets.token_hex(16)}".encode()
        
        # Generera salt för PBKDF2
        salt = os.urandom(16)
        
        # Skapa nyckel med PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        
        # Spara nyckel och salt tillsammans
        key_data = {
            'key': key.decode(),
            'salt': base64.b64encode(salt).decode(),
            'iterations': 100000
        }
        
        # Skriv till fil (endast läsbar av ägaren)
        import json
        with open(self.key_file, 'w') as f:
            json.dump(key_data, f)
        
        # Sätt filrättigheter (endast ägaren kan läsa)
        os.chmod(self.key_file, 0o600)
        
        info("SecurityManager", "Master key generated and saved securely")
    
    def _generate_salt(self):
        """Generera global salt för lösenordshashing"""
        debug("SecurityManager", "Generating global salt")
        
        # Generera kryptografiskt säker salt
        global_salt = secrets.token_bytes(32)
        
        # Spara salt
        with open(self.salt_file, 'wb') as f:
            f.write(global_salt)
        
        # Sätt filrättigheter
        os.chmod(self.salt_file, 0o600)
        
        info("SecurityManager", "Global salt generated and saved")
    
    def _load_keys(self):
        """Ladda krypteringsnycklar från filer"""
        debug("SecurityManager", "Loading encryption keys")
        
        try:
            # Ladda master key
            import json
            with open(self.key_file, 'r') as f:
                key_data = json.load(f)
            
            self.master_key = key_data['key'].encode()
            self.key_salt = base64.b64decode(key_data['salt'])
            self.iterations = key_data['iterations']
            
            # Skapa Fernet cipher
            self.cipher = Fernet(self.master_key)
            
            # Ladda global salt
            with open(self.salt_file, 'rb') as f:
                self.global_salt = f.read()
            
            debug("SecurityManager", "Encryption keys loaded successfully")
            
        except Exception as e:
            error("SecurityManager", f"Failed to load encryption keys: {e}")
            raise
    
    def get_database_key(self) -> str:
        """Hämta databas-krypteringsnyckel för SQLCipher"""
        debug("SecurityManager", "Generating database key")
        
        # Använd master key för att generera databas-specifik nyckel
        db_password = hashlib.sha256(self.master_key + b"database").hexdigest()
        
        debug("SecurityManager", "Database key generated")
        return db_password
    
    def hash_password(self, password: str) -> str:
        """Hasha lösenord med bcrypt och global salt"""
        debug("SecurityManager", "Hashing password with bcrypt")
        
        # Kombinera lösenord med global salt
        salted_password = password.encode() + self.global_salt
        
        # Generera bcrypt salt (per-lösenord)
        bcrypt_salt = bcrypt.gensalt(rounds=12)
        
        # Hasha med bcrypt
        hashed = bcrypt.hashpw(salted_password, bcrypt_salt)
        
        debug("SecurityManager", "Password hashed successfully")
        return hashed.decode()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verifiera lösenord mot hash"""
        debug("SecurityManager", "Verifying password")
        
        try:
            # Kombinera lösenord med global salt
            salted_password = password.encode() + self.global_salt
            
            # Verifiera med bcrypt
            result = bcrypt.checkpw(salted_password, hashed.encode())
            
            debug("SecurityManager", f"Password verification: {'success' if result else 'failed'}")
            return result
            
        except Exception as e:
            error("SecurityManager", f"Password verification error: {e}")
            return False
    
    def encrypt_data(self, data: str) -> str:
        """Kryptera data med Fernet"""
        debug("SecurityManager", "Encrypting data")
        
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            error("SecurityManager", f"Data encryption error: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Dekryptera data med Fernet"""
        debug("SecurityManager", "Decrypting data")
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            error("SecurityManager", f"Data decryption error: {e}")
            raise
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generera säker token för verifiering etc."""
        debug("SecurityManager", f"Generating secure token (length: {length})")
        
        token = secrets.token_urlsafe(length)
        
        debug("SecurityManager", "Secure token generated")
        return token
    
    def get_security_info(self) -> Dict:
        """Hämta säkerhetsinformation för diagnostik"""
        return {
            "encryption": "Fernet (AES 128)",
            "password_hashing": "bcrypt + global salt",
            "key_derivation": "PBKDF2-SHA256 (100k iterations)",
            "database_encryption": "SQLCipher compatible",
            "secure_random": "secrets module",
            "master_key_exists": self.key_file.exists(),
            "global_salt_exists": self.salt_file.exists()
        }


# Global security manager instance
security_manager = SecurityManager()

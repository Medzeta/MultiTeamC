"""
Authentication System
Hanterar SuperAdmin och user authentication
"""

from typing import Optional, Dict
from core.debug_logger import debug, info, warning, error, exception
from core.database_manager import db

class AuthSystem:
    """Authentication system med SuperAdmin support"""
    
    # SuperAdmin hårdkodat
    # PRODUCTION: SuperAdmin / Zph1209Zph!!gg03-jbe
    # DEVELOPMENT: 1 / 1
    SUPERADMIN = {
        "email": "1",
        "password": "1",
        "name": "Super Administrator",
        "company": "MultiTeam System",
        "role": "superadmin"
    }
    
    def __init__(self):
        """Initialize auth system"""
        
        # Använd global DatabaseManager
        self.db = db
        info("AuthSystem", "Authentication system initialized")
    
    
    def authenticate(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user (SuperAdmin eller regular user)"""
        debug("AuthSystem", f"Authentication attempt for: {email}")
        
        # Check SuperAdmin first
        if email.lower() == self.SUPERADMIN["email"].lower():
            debug("AuthSystem", "SuperAdmin authentication attempt")
            if password == self.SUPERADMIN["password"]:
                info("AuthSystem", "SuperAdmin authenticated successfully")
                return {
                    "id": 0,
                    "email": self.SUPERADMIN["email"],
                    "name": self.SUPERADMIN["name"],
                    "company": self.SUPERADMIN["company"],
                    "role": self.SUPERADMIN["role"],
                    "verified": True
                }
            else:
                warning("AuthSystem", "SuperAdmin authentication failed: wrong password")
                return None
        
        # Check regular users using DatabaseManager
        debug("AuthSystem", "Checking regular user authentication")
        return self.db.authenticate_user(email, password)
    
    def register_user(
        self,
        email: str,
        password: str,
        name: str,
        company: str,
        verification_code: str
    ) -> bool:
        """Register new user"""
        debug("AuthSystem", f"Registering new user: {email}")
        
        # Validate not SuperAdmin email
        if email.lower() == self.SUPERADMIN["email"].lower():
            error("AuthSystem", "Cannot register with SuperAdmin email")
            return False
        
        try:
            # Check if user exists using DatabaseManager
            existing_user = db.get_user_by_email(email)
            if existing_user:
                warning("AuthSystem", f"User already exists: {email}")
                return False
            
            # Register user using DatabaseManager
            debug("AuthSystem", "Registering user via DatabaseManager")
            success = db.register_user(email, password, name, company, verification_code)
            
            if success:
                info("AuthSystem", f"User registered successfully: {email}")
                return True
            else:
                error("AuthSystem", f"Failed to register user: {email}")
                return False
            
        except Exception as e:
            exception("AuthSystem", f"Error registering user: {email}")
            return False
    
    def verify_email(self, email: str, code: str) -> bool:
        """Verify user email with code"""
        debug("AuthSystem", f"Verifying email: {email} with code: {code}")
        
        try:
            # Use DatabaseManager for email verification
            success = db.verify_user_email(email, code)
            
            if success:
                info("AuthSystem", f"Email verified successfully: {email}")
                return True
            else:
                warning("AuthSystem", f"Email verification failed: {email}")
                return False
                
        except Exception as e:
            exception("AuthSystem", f"Error verifying email: {email}")
            return False
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        debug("AuthSystem", f"Getting user by email: {email}")
        
        # Check SuperAdmin
        if email.lower() == self.SUPERADMIN["email"].lower():
            debug("AuthSystem", "Returning SuperAdmin user")
            return {
                "id": 0,
                "email": self.SUPERADMIN["email"],
                "name": self.SUPERADMIN["name"],
                "company": self.SUPERADMIN["company"],
                "role": self.SUPERADMIN["role"],
                "verified": True
            }
        
        # Check regular users using DatabaseManager
        try:
            user = db.get_user_by_email(email)
            
            if user:
                debug("AuthSystem", f"User found: {email}")
                return user  # DatabaseManager returnerar redan en dictionary
            else:
                debug("AuthSystem", f"User not found: {email}")
                return None
                
        except Exception as e:
            exception("AuthSystem", f"Error getting user: {email}")
            return None
    
    def is_superadmin(self, email: str) -> bool:
        """Check if email is SuperAdmin"""
        is_admin = email.lower() == self.SUPERADMIN["email"].lower()
        debug("AuthSystem", f"SuperAdmin check for {email}: {is_admin}")
        return is_admin
    
    def update_user_password(self, email: str, new_password: str) -> bool:
        """Update user password"""
        debug("AuthSystem", f"Updating password for user: {email}")
        
        try:
            # Use DatabaseManager to update password
            success = db.update_user_password(email, new_password)
            
            if success:
                info("AuthSystem", f"Password updated successfully for: {email}")
                return True
            else:
                warning("AuthSystem", f"Failed to update password for: {email}")
                return False
                
        except Exception as e:
            exception("AuthSystem", f"Error updating password for {email}: {e}")
            return False


if __name__ == "__main__":
    # Test auth system
    info("TEST", "Testing AuthSystem...")
    
    auth = AuthSystem()
    
    # Test SuperAdmin
    print("\n=== Testing SuperAdmin ===")
    result = auth.authenticate("admin@multiteam.local", "SuperAdmin123!")
    print(f"SuperAdmin auth: {result}")
    
    # Test registration
    print("\n=== Testing Registration ===")
    success = auth.register_user(
        "test@example.com",
        "TestPassword123!",
        "Test User",
        "Test Company",
        "123456"
    )
    print(f"Registration: {success}")
    
    # Test verification
    print("\n=== Testing Verification ===")
    verified = auth.verify_email("test@example.com", "123456")
    print(f"Verification: {verified}")
    
    # Test user auth
    print("\n=== Testing User Auth ===")
    result = auth.authenticate("test@example.com", "TestPassword123!")
    print(f"User auth: {result}")
    
    info("TEST", "AuthSystem test completed")

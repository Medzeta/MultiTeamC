"""
Two-Factor Authentication System
TOTP (Time-based One-Time Password) implementation
Compatible med Google Authenticator, Microsoft Authenticator, etc.
"""

import pyotp
import qrcode
from io import BytesIO
from PIL import Image
from typing import Optional, Tuple
from core.debug_logger import debug, info, warning, error, exception
from core.database_manager import db


class TwoFASystem:
    """2FA system med TOTP support"""
    
    def __init__(self):
        """Initialize 2FA system"""
        debug("TwoFASystem", "Initializing 2FA system")
        # Använd global DatabaseManager
        self.db = db
        info("TwoFASystem", "2FA system initialized")
    
    
    def generate_secret(self) -> str:
        """Generate a new TOTP secret"""
        debug("TwoFASystem", "Generating new TOTP secret")
        secret = pyotp.random_base32()
        info("TwoFASystem", f"Generated secret: {secret[:8]}...")
        return secret
    
    def generate_backup_codes(self, count: int = 10) -> list:
        """Generate backup codes"""
        debug("TwoFASystem", f"Generating {count} backup codes")
        import random
        import string
        
        codes = []
        for _ in range(count):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            codes.append(code)
        
        info("TwoFASystem", f"Generated {len(codes)} backup codes")
        return codes
    
    def get_provisioning_uri(self, secret: str, email: str, issuer: str = "MultiTeam") -> str:
        """Get provisioning URI for QR code"""
        debug("TwoFASystem", f"Creating provisioning URI for: {email}")
        
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(name=email, issuer_name=issuer)
        
        debug("TwoFASystem", f"Provisioning URI created: {uri[:50]}...")
        return uri
    
    def generate_qr_code(self, secret: str, email: str) -> Image.Image:
        """Generate QR code image"""
        debug("TwoFASystem", f"Generating QR code for: {email}")
        
        uri = self.get_provisioning_uri(secret, email)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        info("TwoFASystem", "QR code generated successfully")
        return img
    
    def verify_token(self, secret: str, token: str) -> bool:
        """Verify TOTP token"""
        debug("TwoFASystem", f"Verifying token: {token}")
        
        if not token or not token.isdigit() or len(token) != 6:
            warning("TwoFASystem", "Invalid token format")
            return False
        
        totp = pyotp.TOTP(secret)
        is_valid = totp.verify(token, valid_window=1)  # Allow 1 window (30s) tolerance
        
        if is_valid:
            info("TwoFASystem", "Token verified successfully")
        else:
            warning("TwoFASystem", "Token verification failed")
        
        return is_valid
    
    def enable_2fa_for_user(self, user_id: int, secret: str, backup_codes: list) -> bool:
        """Enable 2FA for user"""
        debug("TwoFASystem", f"Enabling 2FA for user ID: {user_id}")
        return self.db.enable_2fa_for_user(user_id, secret, backup_codes)
    
    def disable_2fa_for_user(self, user_id: int) -> bool:
        """Disable 2FA for user"""
        debug("TwoFASystem", f"Disabling 2FA for user ID: {user_id}")
        return self.db.disable_2fa_for_user(user_id)
    
    def get_user_2fa_status(self, user_id: int) -> Tuple[bool, Optional[str], list]:
        """Get user's 2FA status"""
        debug("TwoFASystem", f"Getting 2FA status for user ID: {user_id}")
        return self.db.get_user_2fa_status(user_id)
    
    def verify_backup_code(self, user_id: int, code: str) -> bool:
        """Verify and consume backup code"""
        debug("TwoFASystem", f"Verifying backup code for user ID: {user_id}")
        return self.db.verify_backup_code(user_id, code)


if __name__ == "__main__":
    # Test 2FA system
    info("TEST", "Testing TwoFASystem...")
    
    twofa = TwoFASystem()
    
    print("\n=== Generating Secret ===")
    secret = twofa.generate_secret()
    print(f"Secret: {secret}")
    
    print("\n=== Generating Backup Codes ===")
    codes = twofa.generate_backup_codes(5)
    print(f"Backup codes: {codes}")
    
    print("\n=== Generating QR Code ===")
    qr_img = twofa.generate_qr_code(secret, "test@example.com")
    print(f"QR Code generated: {qr_img.size}")
    
    print("\n=== Testing Token Verification ===")
    totp = pyotp.TOTP(secret)
    current_token = totp.now()
    print(f"Current token: {current_token}")
    print(f"Verification: {twofa.verify_token(secret, current_token)}")
    
    info("TEST", "TwoFASystem test completed")

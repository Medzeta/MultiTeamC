"""
Password Reset System
Hantering av lösenordsåterställning via email
"""

import sqlite3
import secrets
import string
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict
from core.debug_logger import debug, info, warning, error, exception
from core.email_service import EmailService


class PasswordReset:
    """System för password reset via email"""
    
    def __init__(self):
        """Initialize password reset system"""
        debug("PasswordReset", "Initializing password reset system")
        
        self.db_path = Path("data/users.db")
        self.email_service = EmailService()
        
        # Token validity duration (1 hour)
        self.token_validity_hours = 1
        
        self._setup_database()
        
        info("PasswordReset", "Password reset system initialized")
    
    def _setup_database(self):
        """Setup database for password reset tokens"""
        debug("PasswordReset", "Setting up password reset database")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Password reset tokens table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    used BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Index for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_reset_token 
                ON password_reset_tokens(token)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_reset_user 
                ON password_reset_tokens(user_id)
            """)
            
            conn.commit()
            conn.close()
            
            debug("PasswordReset", "Database setup completed")
            
        except Exception as e:
            exception("PasswordReset", f"Error setting up database: {e}")
    
    def generate_reset_token(self, email: str) -> Optional[str]:
        """
        Generate password reset token for user
        
        Args:
            email: User email address
            
        Returns:
            Reset token if successful, None otherwise
        """
        debug("PasswordReset", f"Generating reset token for: {email}")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT id, name FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            
            if not user:
                warning("PasswordReset", f"User not found: {email}")
                conn.close()
                return None
            
            user_id, username = user
            
            # Generate secure random token
            token = self._generate_secure_token()
            
            # Calculate expiration time
            created_at = datetime.now()
            expires_at = created_at + timedelta(hours=self.token_validity_hours)
            
            # Store token in database
            cursor.execute("""
                INSERT INTO password_reset_tokens 
                (user_id, token, created_at, expires_at, used)
                VALUES (?, ?, ?, ?, 0)
            """, (user_id, token, created_at.isoformat(), expires_at.isoformat()))
            
            conn.commit()
            conn.close()
            
            # Send reset email
            self._send_reset_email(email, username, token)
            
            info("PasswordReset", f"Reset token generated for user: {user_id}")
            return token
            
        except Exception as e:
            exception("PasswordReset", f"Error generating reset token: {e}")
            return None
    
    def _generate_secure_token(self, length: int = 32) -> str:
        """Generate secure random token"""
        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for _ in range(length))
        debug("PasswordReset", f"Generated secure token: {token[:8]}...")
        return token
    
    def _send_reset_email(self, email: str, username: str, token: str) -> bool:
        """Send password reset email"""
        debug("PasswordReset", f"Sending reset email to: {email}")
        
        subject = "Password Reset Request - MultiTeam"
        
        # Create reset link (in production this would be a web URL)
        # For now, we just include the token
        reset_link = f"multiteam://reset-password?token={token}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">🔐 Password Reset</h1>
            </div>
            
            <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; color: #333;">Hi {username},</p>
                
                <p style="font-size: 14px; color: #666; line-height: 1.6;">
                    We received a request to reset your password for your MultiTeam account.
                    If you didn't make this request, you can safely ignore this email.
                </p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea;">
                    <p style="margin: 0; font-size: 14px; color: #666;">Your reset token:</p>
                    <p style="margin: 10px 0; font-size: 18px; font-weight: bold; color: #333; font-family: monospace;">
                        {token}
                    </p>
                    <p style="margin: 0; font-size: 12px; color: #999;">
                        This token will expire in {self.token_validity_hours} hour(s)
                    </p>
                </div>
                
                <p style="font-size: 14px; color: #666; line-height: 1.6;">
                    To reset your password:
                </p>
                <ol style="font-size: 14px; color: #666; line-height: 1.8;">
                    <li>Open MultiTeam application</li>
                    <li>Click "Forgot Password?" on the login screen</li>
                    <li>Enter this token when prompted</li>
                    <li>Create your new password</li>
                </ol>
                
                <div style="background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 8px; margin-top: 20px;">
                    <p style="margin: 0; font-size: 13px; color: #856404;">
                        <strong>⚠️ Security Note:</strong> Never share this token with anyone. 
                        MultiTeam staff will never ask for your reset token.
                    </p>
                </div>
                
                <p style="font-size: 12px; color: #999; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                    If you didn't request this password reset, please contact support immediately.
                </p>
            </div>
            
            <div style="text-align: center; margin-top: 20px; padding: 20px;">
                <p style="font-size: 12px; color: #999;">
                    © 2025 MultiTeam P2P Communication. All rights reserved.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Password Reset Request - MultiTeam
        
        Hi {username},
        
        We received a request to reset your password for your MultiTeam account.
        If you didn't make this request, you can safely ignore this email.
        
        Your reset token: {token}
        
        This token will expire in {self.token_validity_hours} hour(s).
        
        To reset your password:
        1. Open MultiTeam application
        2. Click "Forgot Password?" on the login screen
        3. Enter this token when prompted
        4. Create your new password
        
        Security Note: Never share this token with anyone.
        
        If you didn't request this password reset, please contact support immediately.
        
        © 2025 MultiTeam P2P Communication
        """
        
        success = self.email_service.send_email(
            to_email=email,
            subject=subject,
            html_body=html_body,
            text_body=text_body
        )
        
        if success:
            info("PasswordReset", f"Reset email sent to: {email}")
        else:
            error("PasswordReset", f"Failed to send reset email to: {email}")
        
        return success
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify reset token and return user info
        
        Args:
            token: Reset token
            
        Returns:
            Dict with user info if valid, None otherwise
        """
        debug("PasswordReset", f"Verifying token: {token[:8]}...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get token info
            cursor.execute("""
                SELECT user_id, expires_at, used 
                FROM password_reset_tokens 
                WHERE token = ?
            """, (token,))
            
            result = cursor.fetchone()
            
            if not result:
                warning("PasswordReset", "Token not found")
                conn.close()
                return None
            
            user_id, expires_at_str, used = result
            
            # Check if token is already used
            if used:
                warning("PasswordReset", "Token already used")
                conn.close()
                return None
            
            # Check if token is expired
            expires_at = datetime.fromisoformat(expires_at_str)
            if datetime.now() > expires_at:
                warning("PasswordReset", "Token expired")
                conn.close()
                return None
            
            # Get user info
            cursor.execute("SELECT email, name FROM users WHERE id = ?", (user_id,))
            user_info = cursor.fetchone()
            
            conn.close()
            
            if not user_info:
                error("PasswordReset", "User not found")
                return None
            
            email, name = user_info
            
            info("PasswordReset", f"Token verified for user: {user_id}")
            
            return {
                'user_id': user_id,
                'email': email,
                'name': name,
                'token': token
            }
            
        except Exception as e:
            exception("PasswordReset", f"Error verifying token: {e}")
            return None
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reset password using token
        
        Args:
            token: Reset token
            new_password: New password (will be hashed)
            
        Returns:
            True if successful
        """
        debug("PasswordReset", f"Resetting password with token: {token[:8]}...")
        
        # Verify token first
        user_info = self.verify_token(token)
        if not user_info:
            error("PasswordReset", "Invalid or expired token")
            return False
        
        try:
            import bcrypt
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Hash new password
            hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            
            # Update user password
            cursor.execute("""
                UPDATE users 
                SET password = ? 
                WHERE id = ?
            """, (hashed, user_info['user_id']))
            
            # Mark token as used
            cursor.execute("""
                UPDATE password_reset_tokens 
                SET used = 1 
                WHERE token = ?
            """, (token,))
            
            conn.commit()
            conn.close()
            
            info("PasswordReset", f"Password reset successful for user: {user_info['user_id']}")
            return True
            
        except Exception as e:
            exception("PasswordReset", f"Error resetting password: {e}")
            return False
    
    def cleanup_expired_tokens(self) -> int:
        """
        Clean up expired tokens
        
        Returns:
            Number of tokens deleted
        """
        debug("PasswordReset", "Cleaning up expired tokens")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete expired tokens
            cursor.execute("""
                DELETE FROM password_reset_tokens 
                WHERE expires_at < ?
            """, (datetime.now().isoformat(),))
            
            deleted = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            info("PasswordReset", f"Deleted {deleted} expired tokens")
            return deleted
            
        except Exception as e:
            exception("PasswordReset", f"Error cleaning up tokens: {e}")
            return 0

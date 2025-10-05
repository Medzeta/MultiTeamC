"""
Remember Me System
Hantering av persistent login sessions
"""

import json
import secrets
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict
from core.debug_logger import debug, info, warning, error, exception


class RememberMe:
    """System för remember me funktionalitet"""
    
    def __init__(self):
        """Initialize remember me system"""
        debug("RememberMe", "Initializing remember me system")
        
        self.session_file = Path("data/session.json")
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Session validity (30 days)
        self.session_validity_days = 30
        
        info("RememberMe", "Remember me system initialized")
    
    def create_session(self, user_id: int, email: str, name: str) -> str:
        """
        Create remember me session
        
        Args:
            user_id: User ID
            email: User email
            name: User name
            
        Returns:
            Session token
        """
        debug("RememberMe", f"Creating session for user: {user_id}")
        
        try:
            # Generate secure session token
            token = secrets.token_urlsafe(32)
            
            # Calculate expiration
            created_at = datetime.now()
            expires_at = created_at + timedelta(days=self.session_validity_days)
            
            # Create session data
            session_data = {
                'token': token,
                'user_id': user_id,
                'email': email,
                'name': name,
                'created_at': created_at.isoformat(),
                'expires_at': expires_at.isoformat()
            }
            
            # Save to file
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            info("RememberMe", f"Session created for user: {user_id}")
            return token
            
        except Exception as e:
            exception("RememberMe", f"Error creating session: {e}")
            return ""
    
    def get_session(self) -> Optional[Dict]:
        """
        Get current session if valid
        
        Returns:
            Session data dict if valid, None otherwise
        """
        debug("RememberMe", "Getting current session")
        
        try:
            # Check if session file exists
            if not self.session_file.exists():
                debug("RememberMe", "No session file found")
                return None
            
            # Load session data
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            # Check expiration
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if datetime.now() > expires_at:
                warning("RememberMe", "Session expired")
                self.clear_session()
                return None
            
            info("RememberMe", f"Valid session found for user: {session_data['user_id']}")
            return session_data
            
        except Exception as e:
            exception("RememberMe", f"Error getting session: {e}")
            return None
    
    def clear_session(self):
        """Clear current session"""
        debug("RememberMe", "Clearing session")
        
        try:
            if self.session_file.exists():
                self.session_file.unlink()
                info("RememberMe", "Session cleared")
            else:
                debug("RememberMe", "No session to clear")
                
        except Exception as e:
            exception("RememberMe", f"Error clearing session: {e}")
    
    def update_session(self, user_id: int, email: str, name: str):
        """
        Update existing session with new data
        
        Args:
            user_id: User ID
            email: User email
            name: User name
        """
        debug("RememberMe", f"Updating session for user: {user_id}")
        
        # Get current session
        session = self.get_session()
        
        if session and session['user_id'] == user_id:
            # Update with new data but keep token and timestamps
            session['email'] = email
            session['name'] = name
            
            try:
                with open(self.session_file, 'w') as f:
                    json.dump(session, f, indent=2)
                
                info("RememberMe", "Session updated")
                
            except Exception as e:
                exception("RememberMe", f"Error updating session: {e}")
        else:
            # Create new session
            self.create_session(user_id, email, name)
    
    def is_session_valid(self) -> bool:
        """
        Check if current session is valid
        
        Returns:
            True if session is valid
        """
        session = self.get_session()
        return session is not None
    
    def get_session_user(self) -> Optional[Dict]:
        """
        Get user info from session
        
        Returns:
            User dict if session valid, None otherwise
        """
        session = self.get_session()
        
        if session:
            return {
                'id': session['user_id'],
                'email': session['email'],
                'name': session['name']
            }
        
        return None
    
    def extend_session(self):
        """Extend session expiration"""
        debug("RememberMe", "Extending session")
        
        session = self.get_session()
        
        if session:
            # Extend expiration
            new_expires = datetime.now() + timedelta(days=self.session_validity_days)
            session['expires_at'] = new_expires.isoformat()
            
            try:
                with open(self.session_file, 'w') as f:
                    json.dump(session, f, indent=2)
                
                info("RememberMe", "Session extended")
                
            except Exception as e:
                exception("RememberMe", f"Error extending session: {e}")

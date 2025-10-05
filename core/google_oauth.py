"""
Google OAuth Integration
OAuth 2.0 login med Google
"""

import webbrowser
from typing import Optional, Dict, Callable
from core.debug_logger import debug, info, warning, error, exception

# Try to import google auth libraries
try:
    from google_auth_oauthlib.flow import Flow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False
    warning("GoogleOAuth", "google-auth-oauthlib not available - install with: pip install google-auth-oauthlib")


class GoogleOAuth:
    """System för Google OAuth login"""
    
    # OAuth 2.0 configuration
    # NOTE: These need to be replaced with actual credentials from Google Cloud Console
    CLIENT_ID = "YOUR_CLIENT_ID.apps.googleusercontent.com"
    CLIENT_SECRET = "YOUR_CLIENT_SECRET"
    REDIRECT_URI = "http://localhost:8080/oauth2callback"
    SCOPES = [
        'openid',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
    ]
    
    def __init__(self):
        """Initialize Google OAuth"""
        debug("GoogleOAuth", "Initializing Google OAuth")
        
        self.enabled = False
        self.flow = None
        self.credentials = None
        
        # Check if credentials are configured
        if self.CLIENT_ID.startswith("YOUR_"):
            warning("GoogleOAuth", "Google OAuth credentials not configured")
            warning("GoogleOAuth", "Please set CLIENT_ID and CLIENT_SECRET in google_oauth.py")
            self.enabled = False
        elif not GOOGLE_AUTH_AVAILABLE:
            warning("GoogleOAuth", "Google auth library not available")
            self.enabled = False
        else:
            self.enabled = True
            info("GoogleOAuth", "Google OAuth initialized")
        
        # Callbacks
        self.on_login_success: Optional[Callable] = None
        self.on_login_error: Optional[Callable] = None
    
    def start_oauth_flow(self) -> Optional[str]:
        """
        Start OAuth flow
        
        Returns:
            Authorization URL if successful
        """
        if not self.enabled:
            error("GoogleOAuth", "Google OAuth not enabled")
            return None
        
        info("GoogleOAuth", "Starting OAuth flow")
        
        try:
            # Create OAuth flow
            self.flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.CLIENT_ID,
                        "client_secret": self.CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.REDIRECT_URI]
                    }
                },
                scopes=self.SCOPES,
                redirect_uri=self.REDIRECT_URI
            )
            
            # Generate authorization URL
            auth_url, state = self.flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            
            info("GoogleOAuth", "Authorization URL generated")
            return auth_url
            
        except Exception as e:
            exception("GoogleOAuth", f"Error starting OAuth flow: {e}")
            return None
    
    def complete_oauth_flow(self, authorization_response: str) -> Optional[Dict]:
        """
        Complete OAuth flow with authorization response
        
        Args:
            authorization_response: Full callback URL with code
            
        Returns:
            User info dict if successful
        """
        if not self.enabled or not self.flow:
            error("GoogleOAuth", "OAuth flow not started")
            return None
        
        info("GoogleOAuth", "Completing OAuth flow")
        
        try:
            # Fetch token
            self.flow.fetch_token(authorization_response=authorization_response)
            
            # Get credentials
            self.credentials = self.flow.credentials
            
            # Get user info
            user_info = self._get_user_info()
            
            if user_info and self.on_login_success:
                self.on_login_success(user_info)
            
            return user_info
            
        except Exception as e:
            exception("GoogleOAuth", f"Error completing OAuth flow: {e}")
            
            if self.on_login_error:
                self.on_login_error(str(e))
            
            return None
    
    def _get_user_info(self) -> Optional[Dict]:
        """
        Get user info from Google
        
        Returns:
            User info dict
        """
        if not self.credentials:
            error("GoogleOAuth", "No credentials available")
            return None
        
        try:
            import requests
            
            # Call Google userinfo API
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {self.credentials.token}'}
            )
            
            if response.status_code == 200:
                user_info = response.json()
                info("GoogleOAuth", f"User info retrieved: {user_info.get('email')}")
                return user_info
            else:
                error("GoogleOAuth", f"Failed to get user info: {response.status_code}")
                return None
                
        except Exception as e:
            exception("GoogleOAuth", f"Error getting user info: {e}")
            return None
    
    def login_with_google(self) -> bool:
        """
        Initiate Google login (opens browser)
        
        Returns:
            True if flow started
        """
        auth_url = self.start_oauth_flow()
        
        if not auth_url:
            return False
        
        try:
            # Open browser for authorization
            webbrowser.open(auth_url)
            info("GoogleOAuth", "Browser opened for authorization")
            return True
            
        except Exception as e:
            exception("GoogleOAuth", f"Error opening browser: {e}")
            return False
    
    def is_configured(self) -> bool:
        """
        Check if OAuth is properly configured
        
        Returns:
            True if configured
        """
        return self.enabled and not self.CLIENT_ID.startswith("YOUR_")
    
    def get_configuration_instructions(self) -> str:
        """
        Get instructions for configuring Google OAuth
        
        Returns:
            Configuration instructions
        """
        return """
        Google OAuth Configuration Instructions:
        
        1. Go to Google Cloud Console: https://console.cloud.google.com/
        2. Create a new project or select existing
        3. Enable Google+ API
        4. Go to Credentials > Create Credentials > OAuth 2.0 Client ID
        5. Configure OAuth consent screen
        6. Add authorized redirect URI: http://localhost:8080/oauth2callback
        7. Copy Client ID and Client Secret
        8. Update CLIENT_ID and CLIENT_SECRET in core/google_oauth.py
        9. Install required library: pip install google-auth-oauthlib
        10. Restart application
        """

"""
License System for MultiTeam P2P Communication
Handles license key generation, validation, and enforcement
"""

import json
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from .debug_logger import debug, info, warning, error

class LicenseSystem:
    """
    License management system with 5 tiers
    
    License Tiers:
    1. Basic - 3 modules, 1 team, 5 members per team
    2. Standard - 5 modules, 3 teams, 10 members per team
    3. Professional - 7 modules, 10 teams, 25 members per team
    4. Enterprise - All modules, unlimited teams, 100 members per team
    5. Ultimate - All modules, unlimited teams, unlimited members, team groups
    """
    
    # License tier definitions
    TIERS = {
        "basic": {
            "name": "Basic",
            "max_modules": 3,
            "max_teams": 1,
            "max_members_per_team": 5,
            "team_groups": False,
            "price": "Free"
        },
        "standard": {
            "name": "Standard",
            "max_modules": 5,
            "max_teams": 3,
            "max_members_per_team": 10,
            "team_groups": False,
            "price": "$9.99/month"
        },
        "professional": {
            "name": "Professional",
            "max_modules": 7,
            "max_teams": 10,
            "max_members_per_team": 25,
            "team_groups": False,
            "price": "$29.99/month"
        },
        "enterprise": {
            "name": "Enterprise",
            "max_modules": -1,  # -1 = unlimited
            "max_teams": -1,
            "max_members_per_team": 100,
            "team_groups": False,
            "price": "$99.99/month"
        },
        "ultimate": {
            "name": "Ultimate",
            "max_modules": -1,
            "max_teams": -1,
            "max_members_per_team": -1,
            "team_groups": True,
            "price": "$199.99/month"
        }
    }
    
    def __init__(self, user_id: int):
        """Initialize license system for user"""
        self.user_id = user_id
        self.license_file = Path("data") / f"license_{user_id}.json"
        self.license_file.parent.mkdir(exist_ok=True)
        
        self.current_license = None
        self._load_license()
        
        info("LicenseSystem", f"License system initialized for user {user_id}")
    
    def _load_license(self):
        """Load license from file"""
        try:
            if self.license_file.exists():
                with open(self.license_file, 'r') as f:
                    self.current_license = json.load(f)
                    debug("LicenseSystem", f"License loaded: {self.current_license.get('tier', 'unknown')}")
            else:
                # Default to Basic tier
                self._create_default_license()
        except Exception as e:
            error("LicenseSystem", f"Error loading license: {e}")
            self._create_default_license()
    
    def _create_default_license(self):
        """Create default Basic license"""
        self.current_license = {
            "tier": "basic",
            "key": self._generate_license_key("basic"),
            "issued_date": datetime.now().isoformat(),
            "expiry_date": None,  # Basic never expires
            "user_id": self.user_id,
            "status": "active"
        }
        self._save_license()
        info("LicenseSystem", "Default Basic license created")
    
    def _save_license(self):
        """Save license to file"""
        try:
            with open(self.license_file, 'w') as f:
                json.dump(self.current_license, f, indent=4)
            debug("LicenseSystem", "License saved successfully")
        except Exception as e:
            error("LicenseSystem", f"Error saving license: {e}")
    
    def _generate_license_key(self, tier: str) -> str:
        """
        Generate a unique license key
        Format: XXXX-XXXX-XXXX-XXXX (16 chars)
        """
        # Create unique data for key
        data = f"{tier}_{self.user_id}_{time.time()}_{secrets.token_hex(8)}"
        hash_obj = hashlib.sha256(data.encode())
        hash_hex = hash_obj.hexdigest()[:16].upper()
        
        # Format as XXXX-XXXX-XXXX-XXXX
        key = f"{hash_hex[0:4]}-{hash_hex[4:8]}-{hash_hex[8:12]}-{hash_hex[12:16]}"
        
        debug("LicenseSystem", f"Generated license key: {key}")
        return key
    
    def generate_license(self, tier: str, duration_days: Optional[int] = None) -> str:
        """
        Generate and activate a new license
        
        Args:
            tier: License tier (basic, standard, professional, enterprise, ultimate)
            duration_days: License duration in days (None = no expiry)
            
        Returns:
            str: Generated license key
        """
        if tier not in self.TIERS:
            error("LicenseSystem", f"Invalid tier: {tier}")
            return None
        
        # Generate key
        key = self._generate_license_key(tier)
        
        # Calculate expiry
        expiry = None
        if duration_days:
            expiry = (datetime.now() + timedelta(days=duration_days)).isoformat()
        
        # Create license
        self.current_license = {
            "tier": tier,
            "key": key,
            "issued_date": datetime.now().isoformat(),
            "expiry_date": expiry,
            "user_id": self.user_id,
            "status": "active"
        }
        
        self._save_license()
        info("LicenseSystem", f"License generated: {tier} - {key}")
        
        return key
    
    def validate_license(self) -> Tuple[bool, str]:
        """
        Validate current license
        
        Returns:
            Tuple[bool, str]: (is_valid, reason)
        """
        if not self.current_license:
            return False, "No license found"
        
        # Check status
        if self.current_license.get("status") != "active":
            return False, "License is not active"
        
        # Check expiry
        expiry = self.current_license.get("expiry_date")
        if expiry:
            expiry_date = datetime.fromisoformat(expiry)
            if datetime.now() > expiry_date:
                self.current_license["status"] = "expired"
                self._save_license()
                return False, "License has expired"
        
        return True, "License is valid"
    
    def get_tier_info(self) -> Dict:
        """Get current tier information"""
        if not self.current_license:
            return self.TIERS["basic"]
        
        tier = self.current_license.get("tier", "basic")
        return self.TIERS.get(tier, self.TIERS["basic"])
    
    def can_use_module(self, module_index: int) -> bool:
        """
        Check if user can use a specific module
        
        Args:
            module_index: Index of module (0-9)
            
        Returns:
            bool: True if user has access
        """
        tier_info = self.get_tier_info()
        max_modules = tier_info["max_modules"]
        
        # -1 means unlimited
        if max_modules == -1:
            return True
        
        # Check if module index is within limit
        return module_index < max_modules
    
    def can_create_team(self, current_team_count: int) -> Tuple[bool, str]:
        """
        Check if user can create another team
        
        Args:
            current_team_count: Current number of teams
            
        Returns:
            Tuple[bool, str]: (can_create, reason)
        """
        tier_info = self.get_tier_info()
        max_teams = tier_info["max_teams"]
        
        # -1 means unlimited
        if max_teams == -1:
            return True, "Unlimited teams"
        
        if current_team_count >= max_teams:
            return False, f"Team limit reached ({max_teams} teams)"
        
        return True, f"Can create {max_teams - current_team_count} more teams"
    
    def can_add_member(self, team_id: int, current_member_count: int) -> Tuple[bool, str]:
        """
        Check if user can add another member to team
        
        Args:
            team_id: Team ID
            current_member_count: Current number of members
            
        Returns:
            Tuple[bool, str]: (can_add, reason)
        """
        tier_info = self.get_tier_info()
        max_members = tier_info["max_members_per_team"]
        
        # -1 means unlimited
        if max_members == -1:
            return True, "Unlimited members"
        
        if current_member_count >= max_members:
            return False, f"Member limit reached ({max_members} members)"
        
        return True, f"Can add {max_members - current_member_count} more members"
    
    def has_team_groups(self) -> bool:
        """Check if user has access to team groups feature"""
        tier_info = self.get_tier_info()
        return tier_info.get("team_groups", False)
    
    def get_module_status(self, module_index: int) -> str:
        """
        Get module status for border color
        
        Args:
            module_index: Index of module (0-9)
            
        Returns:
            str: Status (active, error, warning, disabled)
        """
        # Validate license first
        is_valid, reason = self.validate_license()
        
        if not is_valid:
            return "error"  # Red - license expired or invalid
        
        # Check if user can use this module
        if not self.can_use_module(module_index):
            return "disabled"  # Gray - no access
        
        # Module is active
        return "active"  # Green - can use
    
    def upgrade_license(self, new_tier: str, duration_days: Optional[int] = None) -> bool:
        """
        Upgrade license to new tier
        
        Args:
            new_tier: New license tier
            duration_days: License duration (None = no expiry)
            
        Returns:
            bool: Success
        """
        if new_tier not in self.TIERS:
            error("LicenseSystem", f"Invalid tier: {new_tier}")
            return False
        
        # Generate new license
        key = self.generate_license(new_tier, duration_days)
        
        info("LicenseSystem", f"License upgraded to {new_tier}")
        return True
    
    def get_license_info(self) -> Dict:
        """Get current license information"""
        if not self.current_license:
            return {
                "tier": "basic",
                "status": "active",
                "key": "NO-LICENSE",
                "expiry": "Never"
            }
        
        expiry = self.current_license.get("expiry_date")
        expiry_str = "Never"
        if expiry:
            expiry_date = datetime.fromisoformat(expiry)
            expiry_str = expiry_date.strftime("%Y-%m-%d")
        
        return {
            "tier": self.current_license.get("tier", "basic"),
            "status": self.current_license.get("status", "active"),
            "key": self.current_license.get("key", "NO-LICENSE"),
            "expiry": expiry_str,
            "tier_name": self.TIERS[self.current_license.get("tier", "basic")]["name"]
        }
    
    def revoke_license(self):
        """Revoke current license"""
        if self.current_license:
            self.current_license["status"] = "revoked"
            self._save_license()
            info("LicenseSystem", "License revoked")
    
    def get_all_tiers(self) -> Dict:
        """Get all available license tiers"""
        return self.TIERS


# Debug logging
debug("LicenseSystem", "License system module loaded")

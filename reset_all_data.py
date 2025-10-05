"""
Reset All Data - Clear all databases and test data
"""
import os
import shutil
from pathlib import Path

def reset_all_data():
    """Remove all database files and user data"""
    root_dir = Path(__file__).parent
    
    print("🗑️  Resetting all data...\n")
    
    # List of database files and directories to remove
    items_to_remove = [
        # Main data directory
        "data",
        
        # Database files
        "users.db",
        "auth.db",
        "twofa.db",
        "teams.db",
        "license_applications.db",
        
        # License files
        "licenses",
        
        # User data
        "user_data",
        
        # Logs (optional)
        # "logs",
    ]
    
    removed_count = 0
    
    for item_name in items_to_remove:
        item_path = root_dir / item_name
        
        if item_path.exists():
            try:
                if item_path.is_file():
                    item_path.unlink()
                    print(f"✅ Removed file: {item_name}")
                    removed_count += 1
                elif item_path.is_dir():
                    shutil.rmtree(item_path)
                    print(f"✅ Removed directory: {item_name}")
                    removed_count += 1
            except Exception as e:
                print(f"❌ Failed to remove {item_name}: {e}")
        else:
            print(f"⏭️  Skipped (not found): {item_name}")
    
    print(f"\n✅ Reset complete! Removed {removed_count} items.")
    print("\n📋 What was cleared:")
    print("   - All user accounts (except SuperAdmin)")
    print("   - All trial activations")
    print("   - All license applications")
    print("   - All license keys")
    print("   - All teams and team data")
    print("   - All 2FA settings")
    print("\n🔑 SuperAdmin login still works:")
    print("   Email: superadmin")
    print("   Password: superadmin")
    print("\n🚀 Run: python main.py")

if __name__ == "__main__":
    confirm = input("⚠️  This will DELETE ALL DATA! Continue? (yes/no): ")
    if confirm.lower() == "yes":
        reset_all_data()
    else:
        print("❌ Reset cancelled.")

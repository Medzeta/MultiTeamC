"""
Check License Database
Visar alla license applications i databasen
"""

import sqlite3

def check_database():
    try:
        conn = sqlite3.connect('data/license_applications.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Hämta alla applications
        cursor.execute("""
            SELECT id, name, company, email, license_key, 
                   requested_tier, status, payment_status
            FROM license_applications
        """)
        
        rows = cursor.fetchall()
        
        print("=" * 80)
        print("LICENSE APPLICATIONS DATABASE")
        print("=" * 80)
        print()
        
        if not rows:
            print("❌ Inga license applications hittades!")
        else:
            for row in rows:
                print(f"ID: {row['id']}")
                print(f"Name: {row['name']}")
                print(f"Company: {row['company']}")
                print(f"Email: {row['email']}")
                print(f"License Key: {row['license_key']}")
                print(f"Tier: {row['requested_tier']}")
                print(f"Status: {row['status']}")
                print(f"Payment: {row['payment_status']}")
                print("-" * 80)
        
        conn.close()
        
        print()
        print("TEST DATA:")
        print(f"Company: Test Company")
        print(f"License Key: STA-EC60-F921-B32B-74AF")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()

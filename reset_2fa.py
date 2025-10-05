import sqlite3
import os

db_path = 'data/multiteam.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Inaktivera 2FA för alla användare
    cursor.execute('UPDATE users SET twofa_enabled = 0, twofa_secret = NULL, twofa_backup_codes = NULL')
    rows_updated = cursor.rowcount
    
    conn.commit()
    
    # Visa alla användare efter uppdatering
    cursor.execute('SELECT email, name, twofa_enabled FROM users ORDER BY email')
    results = cursor.fetchall()
    
    conn.close()
    
    print(f'✅ 2FA inaktiverat för {rows_updated} användare')
    print()
    print('📋 Alla användare efter uppdatering:')
    print('=' * 60)
    for email, name, twofa_enabled in results:
        status = '🔐 AKTIVERAT' if twofa_enabled else '🔓 INAKTIVERAT'
        print(f'{email:30} | {name:15} | 2FA {status}')
else:
    print('❌ Databas hittades inte')

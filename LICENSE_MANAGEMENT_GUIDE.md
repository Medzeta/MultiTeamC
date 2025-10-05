# 🔑 License Management Guide

## Snabbstart

### 3 Sätt att Öppna License Management:

#### 1. **Dubbelklicka på Batch-filen** (Snabbast!)
```
📁 Multi Team -C/
   └── Open License Management.bat  ← Dubbelklicka här!
```

#### 2. **Från Terminalen**
```powershell
cd "c:\Multi Team -C"
python open_license_management.py
```

#### 3. **Från Appen (Efter Login)**
```
1. Starta appen: python main.py
2. Logga in: SuperAdmin / admin123
3. Klicka på ⚙️ Settings (höger meny)
4. Scrolla ner till "🔑 License Management"
5. Klicka på [🔑 Manage Licenses]
```

---

## Aktivera License Key

### Steg 1: Öppna License Management
- Dubbelklicka på `Open License Management.bat`

### Steg 2: Klicka "🔑 Enter License Key"

### Steg 3: Skriv in din License Key
```
Test License Key: STA-EC60-F921-B32B-74AF
```

### Steg 4: Tryck Enter eller klicka "Activate"

### Steg 5: Success!
```
✅ License Activated!
   License activated: standard
```

---

## Admin: Skapa License Keys

### 1. Starta Appen och Logga In
```powershell
python main.py
```
Login: `SuperAdmin` / `admin123`

### 2. Gå till License Management
```
Dashboard → 📜 License Management (vänster meny)
```

### 3. Godkänn Application
```
1. Se alla ansökningar
2. Dubbelklicka på en ansökan
3. Ändra Status → Approved
4. Ändra Payment → Paid
5. Klicka "Generate & Activate License"
6. Klicka "Send Email with License Key"
```

### 4. License Key Skickas via Email
```
Till: user@example.com
Subject: Your MultiTeam License Key

Your license key: PRO-1234-5678-9ABC-DEF0
```

---

## Användare: Aktivera License

### 1. Ta Emot Email
```
From: MultiTeamCommunication@gmail.com
Subject: Your MultiTeam License Key

Your license key: PRO-1234-5678-9ABC-DEF0
```

### 2. Öppna License Management
- Dubbelklicka på `Open License Management.bat`

### 3. Aktivera
```
1. Klicka "🔑 Enter License Key"
2. Klistra in: PRO-1234-5678-9ABC-DEF0
3. Tryck Enter
4. ✅ License Activated!
```

---

## Felsökning

### Problem: "License key not found or not approved"
**Lösning:**
- Kontrollera att admin har godkänt ansökan
- Status måste vara: `approved`
- Payment måste vara: `paid`

### Problem: "License key is registered to a different machine"
**Lösning:**
- License keys är kopplade till Machine ID
- Kontakta admin för migration

### Problem: Kan inte öppna License Management
**Lösning:**
```powershell
# Kör från terminalen för att se fel:
python open_license_management.py
```

---

## Database-Struktur

### license_applications
```sql
- id
- name
- company
- email
- machine_uid
- requested_tier (basic, standard, pro, enterprise, ultimate)
- status (pending, approved, rejected)
- payment_status (unpaid, paid)
- license_key (genereras när approved)
```

### active_licenses
```sql
- id
- license_key
- license_key_hash (SHA256)
- machine_uid (kopplad till maskin)
- email
- company
- tier
- activated_at
- is_active
```

---

## Test License Keys

### Standard Tier
```
STA-EC60-F921-B32B-74AF
```

### Skapa Nya Test Keys
```powershell
python main.py
# Logga in som SuperAdmin
# Gå till License Management
# Skapa ny application
# Godkänn och generera key
```

---

## Säkerhet

### License Key Format
```
[TIER]-[4HEX]-[4HEX]-[4HEX]-[4HEX]

Exempel:
- BAS-1234-5678-9ABC-DEF0  (Basic)
- STA-EC60-F921-B32B-74AF  (Standard)
- PRO-ABCD-EFGH-IJKL-MNOP  (Pro)
- ENT-1111-2222-3333-4444  (Enterprise)
- ULT-AAAA-BBBB-CCCC-DDDD  (Ultimate)
```

### Machine UID
```
Format: [UUID]-[Hostname]
Exempel: 00000000-0000-0000-0000-049226beccee-Medzeta

Genereras från:
- CPU ID
- Motherboard Serial
- Hostname
```

### Hash-Validering
```python
# License keys hashas med SHA256
import hashlib
key_hash = hashlib.sha256(license_key.encode()).hexdigest()

# Sparas i active_licenses för säker validering
```

---

## Workflow

### Ny Användare
```
1. Användare ansöker om license (Apply for License)
2. Admin ser ansökan i License Management
3. Admin godkänner (Status: approved, Payment: paid)
4. Admin genererar license key
5. Admin skickar email med key
6. Användare aktiverar key
7. ✅ Användare kan använda appen
```

### Befintlig Användare (Ny Maskin)
```
1. Användare installerar på ny maskin
2. Försöker aktivera samma license key
3. ❌ Error: "License key is registered to a different machine"
4. Kontaktar admin för migration
5. Admin skapar ny license för ny maskin
```

---

## Support

### Kontakt
- Email: MultiTeamCommunication@gmail.com
- Support: Kontakta SuperAdmin

### Logs
```
Logs finns i: C:\Multi Team -C\logs\
Senaste: multiteam_YYYYMMDD_HHMMSS.log
```

### Debug
```powershell
# Kör med debug output:
python open_license_management.py

# Eller kolla logs:
type logs\multiteam_*.log | findstr "License"
```

---

## Sammanfattning

✅ **3 sätt att öppna License Management**
✅ **Enkel aktivering med license key**
✅ **Admin kan skapa och skicka keys**
✅ **Säker machine-baserad validering**
✅ **Email-integration för distribution**

**Snabbaste sättet:**
Dubbelklicka på `Open License Management.bat` → Enter License Key → Aktivera! 🚀

# 🎨 Multi Team -C - GLOBAL DESIGN SYSTEM

**Version:** 1.0  
**Datum:** 2025-10-02  
**Status:** OBLIGATORISK STANDARD

---

## 📋 VIKTIGT - LÄS DETTA FÖRST!

Detta dokument definierar **ALLA** design-regler för Multi Team -C.  
**ALLA** nya fönster, moduler och komponenter MÅSTE följa dessa regler.  
**INGA UNDANTAG.**

---

## 🗄️ CENTRALISERAD DATABAS

**DatabaseManager (Singleton Pattern):**
- **Path:** `data/multiteam.db`
- **En databas för hela appen** - Alla moduler använder samma instans
- **Tabeller:** users, sessions, reset_tokens (med 2FA support)
- **Import:** `from core.database_manager import db`

**2FA Support:**
- **twofa_enabled:** INTEGER (0/1)
- **twofa_secret:** TEXT (TOTP secret)
- **twofa_backup_codes:** TEXT (JSON array)

**Användning:**
```python
from core.database_manager import db

# User operations
user = db.get_user_by_email(email)
success = db.authenticate_user(email, password)
db.update_user_password(email, new_password)

# 2FA operations
db.enable_2fa_for_user(user_id, secret, backup_codes)
enabled, secret, codes = db.get_user_2fa_status(user_id)
db.verify_backup_code(user_id, code)
```

---

## 🔘 KNAPPPLACERING - GLOBALA REGLER

**OBLIGATORISKA REGLER för alla knappar i appen:**

### **1. Alignment med Textfält**
```
ALLA knappar MÅSTE alignas med textfält-start (efter label):
- Label bredd: 120px
- Spacing: 8px (Theme.SPACING_MD)
- Knapp-start: 128px från vänster (120 + 8)
```

**Exempel:**
```
Email:          [Enter your email address              ]
                [Submit] [Cancel] [← Back]
                ↑
                128px från vänster
```

### **2. Spacing Före Knappar**
```python
# ALLTID lägg till spacing före knappar
layout.addSpacing(Theme.SPACING_XL)  # 15px
```

### **3. Back-Knapp Position**
```
✅ RÄTT: Back-knapp ALLTID till höger om andra knappar
❌ FEL: Back-knapp ensam centrerad
❌ FEL: Back-knapp till vänster
```

**Layout:**
```python
button_row = QHBoxLayout()
button_row.addSpacing(128)  # Aligna med textfält
button_row.addWidget(primary_btn)
button_row.addWidget(secondary_btn)  # Om finns
button_row.addWidget(back_btn)  # ALLTID sist
button_row.addStretch()  # Fyller ut höger sida
```

### **4. Knapp-Ordning**
```
[Primary Action] [Secondary Action] [← Back]
Exempel:
[Submit Application] [← Back]
[Send Reset Code] [Resend Code] [← Back to Login]
[Activate License] [← Back to Login]
```

### **5. Knapp-Spacing**
```python
button_row.setSpacing(Theme.SPACING_MD)  # 8px mellan knappar
```

---

## 🎨 GLOBALA STYLING FUNKTIONER

**Nya globala funktioner för konsistent styling:**

**Secondary Text (instruktioner, beskrivningar):**
```python
Theme.setup_secondary_text(label, size=11, margin_bottom=None)
# Automatisk: TEXT_SECONDARY färg, wordwrap, font
```

**Field Labels ("Name:", "Email:", etc.):**
```python
Theme.setup_field_label(label, width=80)
# Automatisk: 12px font, TEXT_SECONDARY färg, alignment, min-width
```

**Info Boxes (QR kod, backup codes, etc.):**
```python
Theme.setup_info_box(widget, padding=8)
# Automatisk: SURFACE bakgrund, BORDER, border-radius, padding
```

**Scroll Areas:**
```python
Theme.setup_scroll_area(scroll_area)
# Automatisk: transparent, no borders, scroll policies
```

**FÖRE (lokal styling):**
```python
label.setFont(Theme.get_font(size=11))
label.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; margin-bottom: 5px;")
label.setWordWrap(True)
```

**EFTER (global funktion):**
```python
Theme.setup_secondary_text(label, size=11, margin_bottom=5)
```

---

## 🎯 GRUNDPRINCIPER

### **1. Ett Fönster - Alla Vyer**
```
✅ RÄTT: Alla undersidor öppnas i huvudfönstret
❌ FEL: Separata OS-fönster
❌ FEL: Externa popups med OS-chrome
```

**Regel:**
- Hemskärm design = Global design för HELA appen
- Alla vyer öppnas i samma CustomWindow
- Smooth transitions mellan vyer
- Ingen OS-integration

### **2. Popup-Fönster**
```
✅ RÄTT: CustomDialog med global design
❌ FEL: QDialog med OS-chrome
❌ FEL: QMessageBox (använd CustomDialog)
```

**Regel:**
- SAMMA rundade hörn (15px)
- FRAMELESS design (ingen OS-chrome)
- GLOBAL färgschema (#2b2b2b surface, #ffffff text)
- HTML-formatering stöd (RichText)
- Centrerad på huvudfönster
- CustomDialog-klass (IMPLEMENTERAD)

**POPUP STORLEKAR (baserat på innehåll):**
- **Standard:** 400x220px (mellanstor för meddelanden med text)
- **2FA Question:** 450x280px (för 2FA-setup frågor)
- **Large:** 650x540px (för login success med achievements)
- **Automatisk centrering** på huvudfönster
- **Konsistent design** oavsett storlek

**Popup Design Specifikationer:**

**Standard Popup (400x220px):**
```
Storlek: 400x220px (fast)
Användning: Info, Error, Warning meddelanden med text
Border-radius: 15px
Padding: 20px
Title: 16px bold, centrerad
Message: 10px normal, centrerad, wordwrap
Buttons: 80px bredd, global styling
```

**2FA Question Popup (450x280px):**
```
Storlek: 450x280px (fast)
Användning: 2FA setup frågor med längre text
Border-radius: 15px
Padding: 20px
Title: 16px bold, centrerad
Message: 10px normal, centrerad, wordwrap
Buttons: 80px bredd, global styling
```

**Large Popup (650x540px):**
```
Storlek: 650x540px (fast)
Användning: Login Success med achievements och statistik
Border-radius: 15px
Padding: 20px
Title: 16px bold, centrerad
Message: 10px normal, centrerad, wordwrap, HTML support
Buttons: 80px bredd, global styling
```

**Användning:**
```python
# Standard popup
show_info(parent, "Title", "Message")
show_error(parent, "Error", "Error message")

# Large popup
show_login_success(parent, "Login Successful!", html_message)
show_info(parent, "Title", "Message", large=True)
```

**LOGIN SUCCESS POPUP:**
- Användarspecifik statistik och achievements
- Network status med färgkodning
- Separator mellan sektioner (━)
- Welcome back + email + Windows UID
- Mindre textstorlek (title 16px, message 10px)

---

## ✅ KOMPLETT AUTENTISERINGSSYSTEM

### **Färdiga Funktioner (100% Implementerade)**
```
✅ Login System - ModernLoginModule med säker autentisering
✅ Create Account - NewRegistrationModule med email-verifiering  
✅ Forgot Password - ForgotPasswordModule med säker återställning
✅ Email Verification - Automatisk verifiering vid registrering och login
✅ Login Success Popup - Stor popup (650x540px) med rik information
```

**Användargränssnitt:**
- **Modern Design** - Global UI design med Theme.* funktioner
- **Responsiv Layout** - Alla moduler använder kompakt card-design
- **Error Handling** - Tydliga felmeddelanden och användarfeedback
- **Smooth Navigation** - Smidig övergång mellan login/registrering/återställning

**Login Success Information:**
```
Network Status: Team: 3/5 online • Peers: 12/18 online
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Welcome back, [Användarnamn]!
[Email-adress]
[Datornamn] | UID: [MAC-adress]
Achievement Unlocked: [Titel och meddelande]
Your Stats: today: X • This week: Y • Total: Z
Last Login: [Datum och tid]

### **Databaskryptering**
```
✅ RÄTT: Krypterad SQLite med SecurityManager
❌ FEL: Okrypterad databas
❌ FEL: Hårdkodade nycklar
```

**Implementation:**
- **SQLCipher-kompatibel kryptering** med PRAGMA key
- **PBKDF2-SHA256** nyckelderivering (100k iterationer)
- **Maskinspecifika nycklar** baserat på COMPUTERNAME + USERNAME
- **Fernet (AES 128)** för datakryptering
- **Säker fillagring** med 0600 permissions

### **Lösenordshashing**
```
✅ RÄTT: bcrypt + global salt + SecurityManager
❌ FEL: Enkel bcrypt utan global salt
❌ FEL: SHA256 eller MD5 hashing
```

**Säkerhetsspecifikation:**
```
Lösenordshashing: bcrypt (12 rounds) + global salt (32 bytes)
Global salt: Kryptografiskt säker (secrets.token_bytes)
Per-password salt: bcrypt.gensalt() automatiskt
Verifiering: security_manager.verify_password()
```

**SecurityManager Funktioner:**
```python
# Lösenordshashing
hashed = security_manager.hash_password(password)
valid = security_manager.verify_password(password, hashed)

# Databaskryptering
db_key = security_manager.get_database_key()
conn.execute(f"PRAGMA key = '{db_key}'")

# Datakryptering
encrypted = security_manager.encrypt_data(data)
decrypted = security_manager.decrypt_data(encrypted)

# Säkra tokens
token = security_manager.generate_secure_token(32)
```

**Säkerhetsnivåer:**
- **Databas:** SQLCipher-kompatibel kryptering
- **Lösenord:** bcrypt (12 rounds) + global salt
- **Nycklar:** PBKDF2-SHA256 (100k iterationer)
- **Tokens:** Kryptografiskt säkra (secrets modul)
- **Filer:** 0600 permissions (endast ägaren)

**Nyckelhantering:**
```
Master Key: data/master.key (JSON med nyckel + salt)
Global Salt: data/salt.key (32 bytes binär)
Database Key: SHA256(master_key + "database")
Permissions: 0600 (endast ägaren kan läsa)
```

---

## 📧 2FA EMAIL SYSTEM (NYA FUNKTIONER 2025-10-04)

### **Automatisk Email vid 2FA Setup:**
```python
# Email skickas automatiskt när användaren klickar "Complete Setup"
# Ingen manuell knapp längre - allt händer automatiskt
```

**Email Innehåll:**
- **30 Backup Codes** i 3 kolumner × 10 rader (vänsterjusterad tabell)
- **QR-Kod** som inbäddad PNG-bild (vänsterjusterad, 200px)
- **Secret Key** formaterad med mellanslag (XXXX XXXX XXXX XXXX)
- **Instruktioner** för hur man använder backup codes
- **Säkerhetsvarning** med tydliga instruktioner att radera emailet

**HTML Email-Mall Design:**
```
- Gradient header: #1f6aa5 → #144870
- QR-kod border: 2px solid #1f6aa5
- Secret key box: #f9f9f9 bakgrund, #1f6aa5 border
- Säkerhetsvarning: #fff3cd bakgrund, #ff6b6b border
- Vänsterjusterad layout för QR-kod och text
- Ingen punktlista - ren vänsterjusterad text
```

**Databas-Lagring:**
```python
# Nya kolumner i users-tabellen:
twofa_qr_code BLOB              # QR-kod som PNG bytes
twofa_email_sent_at TIMESTAMP   # När emailet skickades
twofa_email_backup_codes TEXT   # 30 backup codes som JSON

# Funktioner:
db.save_2fa_email_data(user_id, qr_bytes, codes)
secret, qr_bytes, codes, sent_at = db.get_2fa_email_data(user_id)
```

**Säkerhetsvarning i Email:**
```html
🔒 SECURITY WARNING

This email contains sensitive security information...
This is a significant security risk if falls into wrong hands.

IMPORTANT ACTIONS:
1. Save backup codes in secure password manager
2. Save QR code if needed for future device setup
3. DELETE THIS EMAIL IMMEDIATELY after saving
4. Empty your email trash/deleted items folder

⚠️ Never forward this email or share its contents!
```

**Teknisk Implementation:**
- `EmailService.send_backup_codes_email()` - Skickar email med QR-kod och codes
- `MIMEMultipart('related')` - För inbäddade bilder
- `Content-ID: <qr_code>` - Referens till QR-bild i HTML
- PIL Image → PNG bytes konvertering
- Automatisk migration av databas-kolumner

---

## 📝 SECTION HEADERS (NYA GLOBALA STANDARDEN)

### **VIKTIGT: Använd ALLTID Theme.add_section_header()**

```python
# ✅ RÄTT: Global funktion
Theme.add_section_header(card_layout, "Sign In")
Theme.add_section_header(card_layout, "Create Account")
Theme.add_section_header(card_layout, "Settings")

# ❌ FEL: Lokal kod
section_label = QLabel("Sign In")
section_label.setFont(...)  # ALDRIG!
```

### **Automatisk Implementation:**
- **Storlek:** 20px, bold
- **Färg:** #ffffff (vit text)
- **Alignment:** Vänsterjusterad
- **Spacing:** 15px under header (1 enterslag)
- **Placering:** Direkt ovanför närmaste textfält/innehåll

### **Användning:**
```python
# Lägg till section header med automatisk spacing
Theme.add_section_header(layout, "Header Text")

# Lägg sedan till ditt innehåll direkt
layout.addWidget(your_content)
```

---

## 🎨 FÄRGSCHEMA (EXAKTA VÄRDEN)

### **VIKTIGT: 5 FÄRGTEMAN TILLGÄNGLIGA**
Appen har nu 5 olika färgteman som kan väljas i settings:
1. **Dark Blue** (Default/Nuvarande)
2. **Midnight Purple** (Lila tema)
3. **Forest Green** (Grön tema)
4. **Crimson Red** (Röd tema)
5. **Ocean Teal** (Cyan tema)

Alla teman finns i: `core/color_themes.py`

---

### **TEMA 1: DARK BLUE (DEFAULT)**

#### **Primära Färger:**
```python
BACKGROUND = "#1a1a1a"      # Huvudbakgrund
SURFACE = "#2b2b2b"         # Cards, containers
SURFACE_VARIANT = "#1f1f1f" # Alternativ yta
PRIMARY = "#1f6aa5"         # Primära knappar (Blå)
PRIMARY_HOVER = "#2980b9"   # Hover state
SECONDARY = "#3a3a3a"       # Sekundära element
SECONDARY_HOVER = "#4a4a4a" # Hover state
```

#### **Text Färger:**
```python
TEXT = "#ffffff"            # Primär text
TEXT_SECONDARY = "#b0b0b0"  # Sekundär text
TEXT_DISABLED = "#666666"   # Disabled text
```

#### **Status Färger:**
```python
SUCCESS = "#388e3c"         # Grön (Online)
WARNING = "#f5c542"         # Gul (Away)
ERROR = "#d32f2f"           # Röd (Offline/Error)
INFO = "#1f6aa5"            # Blå (Info)
```

#### **UI Element Färger:**
```python
BORDER = "#3a3a3a"          # Borders
HOVER = "#2a2a2a"           # Hover backgrounds
ACTIVE = "#353535"          # Active/Focus state
```

---

### **TEMA 2: MIDNIGHT PURPLE**

#### **Primära Färger:**
```python
BACKGROUND = "#1a1520"      # Mörk lila bakgrund
SURFACE = "#2a2030"         # Lila surface
SURFACE_VARIANT = "#1f1a25" # Alternativ lila
PRIMARY = "#7c3aed"         # Djup lila
PRIMARY_HOVER = "#8b5cf6"   # Ljusare lila hover
SECONDARY = "#3a2f45"       # Sekundär lila
SECONDARY_HOVER = "#4a3f55" # Hover state
```

#### **Text Färger:**
```python
TEXT = "#ffffff"            # Vit text
TEXT_SECONDARY = "#c4b5fd"  # Ljus lila tint
TEXT_DISABLED = "#6b5b7b"   # Disabled lila
```

---

### **TEMA 3: FOREST GREEN**

#### **Primära Färger:**
```python
BACKGROUND = "#161d16"      # Mörk grön bakgrund
SURFACE = "#1f2b1f"         # Grön surface
SURFACE_VARIANT = "#1a221a" # Alternativ grön
PRIMARY = "#059669"         # Smaragdgrön
PRIMARY_HOVER = "#10b981"   # Ljusare grön hover
SECONDARY = "#2d3a2d"       # Sekundär grön
SECONDARY_HOVER = "#3d4a3d" # Hover state
```

#### **Text Färger:**
```python
TEXT = "#ffffff"            # Vit text
TEXT_SECONDARY = "#a7f3d0"  # Ljus grön tint
TEXT_DISABLED = "#5a6a5a"   # Disabled grön
```

---

### **TEMA 4: CRIMSON RED**

#### **Primära Färger:**
```python
BACKGROUND = "#1d1416"      # Mörk röd bakgrund
SURFACE = "#2b1f21"         # Röd surface
SURFACE_VARIANT = "#221a1c" # Alternativ röd
PRIMARY = "#dc2626"         # Djup röd
PRIMARY_HOVER = "#ef4444"   # Ljusare röd hover
SECONDARY = "#3a2f31"       # Sekundär röd
SECONDARY_HOVER = "#4a3f41" # Hover state
```

#### **Text Färger:**
```python
TEXT = "#ffffff"            # Vit text
TEXT_SECONDARY = "#fca5a5"  # Ljus röd tint
TEXT_DISABLED = "#6a5a5c"   # Disabled röd
```

---

### **TEMA 5: OCEAN TEAL**

#### **Primära Färger:**
```python
BACKGROUND = "#14191d"      # Mörk cyan bakgrund
SURFACE = "#1e2a2f"         # Cyan surface
SURFACE_VARIANT = "#192025" # Alternativ cyan
PRIMARY = "#0891b2"         # Djup cyan/teal
PRIMARY_HOVER = "#06b6d4"   # Ljusare cyan hover
SECONDARY = "#2f3a3f"       # Sekundär cyan
SECONDARY_HOVER = "#3f4a4f" # Hover state
```

#### **Text Färger:**
```python
TEXT = "#ffffff"            # Vit text
TEXT_SECONDARY = "#a5f3fc"  # Ljus cyan tint
TEXT_DISABLED = "#5a6a6f"   # Disabled cyan
```

---

### **ANVÄNDNING AV TEMAN:**
```python
from core.color_themes import get_theme, get_available_themes

# Hämta ett tema
theme = get_theme("midnight_purple")

# Använd tema-färger
background_color = theme.BACKGROUND
primary_color = theme.PRIMARY

# Lista alla tillgängliga teman
themes = get_available_themes()
# ['dark_blue', 'midnight_purple', 'forest_green', 'crimson_red', 'ocean_teal']
```

---

## 📐 RUNDADE HÖRN (EXAKTA VÄRDEN)

```python
RADIUS_SM = 5px    # Knappar, inputs, små element
RADIUS_MD = 10px   # Cards, containers
RADIUS_LG = 15px   # Window, popups, stora element
```

**Användning:**
- **Window/Popups:** 15px (RADIUS_LG)
- **Cards/Frames:** 10px (RADIUS_MD)
- **Buttons:** 5px (RADIUS_SM)
- **Inputs:** 5px (RADIUS_SM)
- **Checkboxes:** 3px

---

## 🪟 WINDOW STANDARD

### **CustomWindow (Huvudfönster) - NY IMPLEMENTATION:**
```python
# VIKTIGT: Använd QWidget istället för QMainWindow för perfekt rundade hörn!

# Egenskaper:
- QWidget root window (INTE QMainWindow)
- Borderless (FramelessWindowHint)
- Transparent background (WA_TranslucentBackground)
- QFrame main_widget med CSS border-radius: 15px (RADIUS_LG)
- Storlek: 1400x900 (default, fixed)
- Draggable titlebar
- Färgade window controls (Grön-Gul-Röd)

# Implementation:
class CustomWindow(QWidget):  # QWidget, INTE QMainWindow!
    def __init__(self):
        # Frameless window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Main container med CSS border-radius (samma som login-kort)
        self.main_widget = QFrame()
        self.main_widget.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.BACKGROUND};
                border-radius: {Theme.RADIUS_LG}px;  # 15px - SMOOTH!
            }}
        """)

# Titlebar:
- Höjd: 75px (för 4 rader med stats)
- Background: BACKGROUND (#1a1a1a)
- Border-radius: 15px (endast top corners)
- Transparent bakgrund för child widgets

# Logout Button (under window controls):
- Placering: Under färgade cirklar (Grön-Gul-Röd)
- Funktion: Theme.setup_login_button(width=90)
- Storlek: 90x25px (exakt samma som alla globala knappar)
- Container höjd: 65px (18px cirklar + 8px spacing + 25px knapp + 10px bottom margin)
- Bottom margin: 10px (för att hela knappen ska synas)
- Alignment: AlignRight

# Content Area:
- Background: transparent (VIKTIGT!)
- Låter main_widget's rundade hörn synas igenom
- Alla child widgets måste ha transparent bakgrund

# VIKTIGT - Child Widgets:
ALLA moduler som visas i content area MÅSTE ha transparent bakgrund:
```python
# Dashboard-modul exempel:
self.setStyleSheet("""
    MainDashboardModule {
        background-color: transparent;  # VIKTIGT!
    }
""")
```

# Varför Detta Fungerar:
- QWidget root kan ha transparent bakgrund
- QFrame main_widget har CSS border-radius (smooth antialiasing)
- Transparent child widgets låter rundade hörn synas
- Samma approach som login-kort (fungerar perfekt)
```

### **CustomDialog (Popup-fönster):**
```python
# SAMMA som CustomWindow men:
- Mindre storlek (anpassas efter innehåll)
- Modal (blockerar huvudfönster)
- Centrerad över huvudfönster
- SAMMA titlebar
- SAMMA färgade knappar
- SAMMA rundade hörn (15px)
```

---

## 🎛️ TITLEBAR STANDARD

### **Layout:**
```
┌─────────────────────────────────────────────────────┐
│ Multi Team -C              [spacer]      ●●●        │
│ Användarnamn ●                                       │
│ DESKTOP-ABC | UID: aa:bb:cc:dd:ee:ff                │
└─────────────────────────────────────────────────────┘
```

### **Specifikation:**
```python
# Höjd:
60px (för 3 rader)

# Vänster Sida (Vertikal Layout):
Rad 1: App Namn (14px, #ffffff, font-weight: 500)
Rad 2: Användarnamn + Status (11px, #b0b0b0)
Rad 3: Computer | UID (10px, #b0b0b0)

# Spacing:
- Mellan rader: 1px
- Padding: 8px top/bottom, 10px left

# Höger Sida (Window Controls):
- 3 färgade cirklar (18x18px)
- Ordning: Grön → Gul → Röd
- Spacing: 12px mellan cirklar
- Position: 5px från höger kant

# Status Indikator:
● Grön (#388e3c) - Online
● Gul (#f5c542) - Away
● Röd (#d32f2f) - Offline
● Grå (#888888) - Ej inloggad
```

### **Window Controls (Färgade Cirklar):**
```python
# Grön Cirkel (Minimize):
- Färg: #388e3c
- Storlek: 18x18px
- Position: Vänster
- Funktion: Minimize window

# Gul Cirkel (Maximize):
- Färg: #f5c542
- Storlek: 18x18px
- Position: Mitten
- Funktion: Maximize/Restore window

# Röd Cirkel (Close):
- Färg: #d32f2f
- Storlek: 18x18px
- Position: Höger
- Funktion: Close window

# Hover Effect:
- Opacity: 0.7
- Smooth transition
```

---

## 🔘 BUTTON STANDARD

### **Primary Button - UPPDATERAD DESIGN:**
```python
background-color: #1f6aa5 (PRIMARY)
color: #ffffff (TEXT)
border: none
border-radius: 8px (rundare hörn för modern look)
padding: 12px 24px (mer padding)
font-size: 14px
font-weight: 600 (semi-bold)
min-height: 45px (standardhöjd)
transition: all 0.2s ease (smooth övergångar)

# Hover:
background-color: #2980b9 (PRIMARY_HOVER)
transform: translateY(-1px) (subtil lyft-effekt)
box-shadow: 0 4px 12px rgba(31, 106, 165, 0.3) (glöd-effekt)

# Pressed:
background-color: #1557a0
transform: translateY(0px)

# Disabled:
background-color: #3a3a3a (SECONDARY)
color: #666666 (TEXT_DISABLED)
```

### **Secondary Button - UPPDATERAD DESIGN:**
```python
background-color: #3a3a3a (SECONDARY)
color: #ffffff (TEXT)
border: none
border-radius: 8px (rundare hörn)
padding: 12px 24px
font-size: 14px
font-weight: 500 (medium weight)
min-height: 42px (lite lägre än primary)
transition: all 0.2s ease

# Hover:
background-color: #4a4a4a (SECONDARY_HOVER)
transform: translateY(-1px)
box-shadow: 0 2px 8px rgba(58, 58, 58, 0.4)

# Pressed:
background-color: #2a2a2a
transform: translateY(0px)
```

### **Danger Button:**
```python
background-color: #d32f2f (ERROR)
color: #ffffff (TEXT)
# Resten samma som Primary
```

### **Success Button:**
```python
background-color: #388e3c (SUCCESS)
color: #ffffff (TEXT)
# Resten samma som Primary
```

### **Tall Button - NY GLOBAL FUNKTION (2025-10-04):**
```python
# För flerrads-text som "Trial Active\n(27 days left)"
# Dubbelt så hög som vanliga knappar (25px -> 50px)

# Default storlek:
width: 90px (samma som vanliga knappar)
height: 50px (dubbelt så hög som vanliga 25px knappar)

# Styling - samma som login button:
background-color: rgba(58, 58, 58, 0.2) (20% transparent)
color: #ffffff (TEXT)
border: 1px solid rgba(58, 58, 58, 0.3)
border-radius: 8px
font-size: 14px
font-weight: 400
padding: 4px 6px (mindre padding för kompakt design)

# Hover:
background-color: #2b2b2b (SURFACE)
border: 1px solid #3a3a3a (BORDER)

# Pressed:
background-color: #1a1a1a (BACKGROUND)
border: 1px solid #3a3a3a (BORDER)

# Användning:
Theme.setup_tall_button(button)                    # 90x50px default
Theme.setup_tall_button(button, width=150)         # Custom bredd för längre text
Theme.setup_tall_button(button, width=120, height=60)  # Full custom storlek
```

**VIKTIGT:** Använd tall button endast för flerrads-text. Vanliga knappar ska använda `Theme.setup_login_button()`.

---

## 📝 INPUT FIELD STANDARD

### **QLineEdit (Text Input) - EXTREMT KOMPAKT DESIGN:**
```python
background-color: #555555 (ljusare än SURFACE för synlighet)
color: #ffffff (TEXT)
border: none
border-radius: 3px (minimal rundning för extremt kompakt look)
padding: 4px 8px (extremt minimal padding för maximal kompakthet)
font-size: 14px
min-height: 26px (extremt kompakt höjd)
max-height: 26px

# Focus:
background-color: #5f5f5f (subtil ljusare vid focus - ingen border)
border: none (ingen blå linje, bara färgändring)

# Hover:
background-color: #5a5a5a (subtil hover-effekt)

# Placeholder:
color: #888888 (bättre kontrast)

# Layout med labels:
Labels placeras till vänster om textfält med min-width: 80px
Vänster-justerade labels med 10px spacing till textfält
Labels börjar från vänster kant för naturlig läsning

# Globala spacing-inställningar:
SPACING_XS = 3px (extremt minimal)
SPACING_SM = 5px (minimal)
SPACING_MD = 8px (mellan element)
SPACING_LG = 10px (större avstånd)
SPACING_XL = 15px (maximal)

# SLUTLIG PERFEKT LAYOUT STANDARDS - ALLA FRAMTIDA MODULER:

## APP-LOGGA DESIGN (Multi Team -C) - LÅSTA MÅTT:
- Font: 40px, font-weight: 900, centrerad (LÅST)
- CSS: font-size: 40px; font-weight: 900; margin: 0px; padding: 0px;
- P2P subtitle: 14px, margin-top: -50px (ULTRA TIGHT - LÅST)
- Maximal tight logga-layout utan mellanrum
- VIKTIGT: -50px margin ger perfekt spacing mellan huvudrubrik och underrubrik

## SIGN IN HEADER POSITIONERING - LÅST:
- Vänsterjusterad med HBoxLayout
- signin_row.addSpacing(-5) för perfekt balans (LÅST)
- 5px mer åt vänster än email för optimal visuell balans
- Konsistent vänsterjustering genom hela formuläret

## CHECKBOX POSITIONERING - PERFEKT JUSTERING:
Horisontell: 98px från vänster (80px label + 10px spacing + 8px extra)
Vertikal: -5px spacing (13px uppåt från original)
Använder: remember_row.addSpacing(98) för horisontell justering
Använder: card_layout.addSpacing(-5) för vertikal justering
```

### **QTextEdit (Multi-line):**
```python
# Samma som QLineEdit men:
min-height: 100px
padding: 10px

# Använd Theme.setup_checkbox() för konsistent styling
color: #ffffff (TEXT)
font-size: 14px
spacing: 8px (kompakt spacing mellan checkbox och text)
padding: 6px 0px (mindre padding)

# Indicator (checkboxen själv):
width: 18px (mindre storlek)
height: 18px
border: 2px solid #555555 (samma som textfält)
border-radius: 3px (mindre rundning)
background-color: #555555 (samma som textfält)

# Hover:
border: 2px solid #666666
background-color: #5a5a5a

# Checked:
background-color: #888888 (tydligare grå för bättre kontrast)
border: 2px solid #999999
image: vit SVG checkmark (tydlig och skalbar)

# Checked + Hover:
background-color: #999999 (ännu ljusare för tydlig feedback)
border: 2px solid #aaaaaa

# CHECKBOX LAYOUT STANDARD FÖR ALLA MODULER:
Använd HBoxLayout med:
- addSpacing(98) för horisontell justering med textfält
- Layout före checkbox: addSpacing(-5) för 13px uppåt justering
- addStretch() efter checkbox för att fylla ut utrymmet

# SLUTLIG IMPLEMENTATION FÖR ALLA FRAMTIDA MODULER:

## APP-LOGGA IMPLEMENTATION:
```python
# CARD DIMENSIONER (LÅSTA MÅTT)
card_settings = Theme.get_compact_card_settings()
card_width = int(card_settings['width'] * 1.33)  # 560px (LÅST)
card.setFixedSize(card_width, card_settings['height'] + 120)

# Multi Team -C Title (APP-LOGGA - LÅSTA MÅTT)
title_label = QLabel("Multi Team -C")
title_label.setFont(Theme.get_font(size=40, bold=True))  # 40px LÅST
title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
title_label.setStyleSheet(f"""
    color: {Theme.TEXT};
    font-size: 40px;
    font-weight: 900;
    margin: 0px;
    padding: 0px;
""")
card_layout.addWidget(title_label)

# P2P Subtitle (ULTRA TIGHT - LÅSTA MÅTT)
subtitle_label = QLabel("P2P Team Collaboration Platform")
subtitle_label.setFont(Theme.get_font(size=14))
subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
subtitle_label.setStyleSheet(f"""
    color: {Theme.SECONDARY};
    margin-top: -50px;  # LÅST - Ultra tight spacing
    margin-bottom: 0px;
    padding: 0px;
""")
card_layout.addWidget(subtitle_label)
```

## SIGN IN HEADER IMPLEMENTATION:
```python
# Sign In Header (PERFEKT BALANS - LÅSTA MÅTT)
signin_row = QHBoxLayout()
signin_row.addSpacing(-5)  # LÅST - Perfekt balans, 5px mer vänster än email
header_label = QLabel("Sign In")
header_label.setFont(Theme.get_font(size=20, bold=True))
header_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
signin_row.addWidget(header_label)
signin_row.addStretch()
card_layout.addLayout(signin_row)
```

## CHECKBOX IMPLEMENTATION:
```python
# Checkbox Layout (PERFEKT POSITIONERING)
remember_row = QHBoxLayout()
remember_row.addSpacing(98)  # Perfekt horisontell justering
remember_row.addWidget(checkbox)
remember_row.addStretch()
card_layout.addSpacing(-5)  # Perfekt vertikal justering
card_layout.addLayout(remember_row)
```

## APP TITLE & SUBTITLE IMPLEMENTATION (GLOBAL STANDARD):
```python
# App Title & Subtitle - Använd Theme.setup_app_title()
title_label = QLabel("Multi Team -C")
subtitle_label = QLabel("P2P Team Collaboration Platform")
Theme.setup_app_title(title_label, subtitle_label)  # Automatisk styling

card_layout.addWidget(title_label)
card_layout.addSpacing(-45)  # Negativ spacing för tight layout
card_layout.addWidget(subtitle_label)

# GLOBAL STYLING (Theme.setup_app_title):
# Titel: 40px font, font-weight 900, centrerad, #ffffff, 100% opacity
# Undertitel: 17px font, italic (kursiv), #3a3a3a, 70% opacity, margin-top -30px
# Spacing: -45px mellan titel och undertitel för tight layout
# Undertitel är subtil och smälter in i bakgrunden
```

## LOGIN BUTTON IMPLEMENTATION (GLOBAL STANDARD):
```python
# Login Button - Använd Theme.setup_login_button()
login_btn = QPushButton("Sign in")
Theme.setup_login_button(login_btn)  # Automatisk styling
login_btn.clicked.connect(self._handle_login)

# GLOBAL STYLING (Theme.setup_login_button):
# Storlek: 90x25px (eller custom width)
# Font: 14px, font-weight 400
# Padding: 1px 6px
# Transparens: 20% (rgba 58,58,58,0.2)
# Border-radius: 8px
# Border: 1px solid rgba(58,58,58,0.3)
# Hover: Solid mörk (#2b2b2b)
# Pressed: Solid mörkast (#1a1a1a)
```

---

## 🚀 GITHUB AUTO-UPPDATERINGSSYSTEM (NYA FUNKTIONER 2025-10-05)

### **KOMPLETT AUTOMATISERAT RELEASE SYSTEM**

#### **FINALPUBLISH.bat - Automatisk GitHub Release:**
```batch
# Komplett automatiserad process:
1. System Check - Verifierar Python, PyInstaller, GitHub token
2. EXE Build - PyInstaller med alla dependencies
3. EXE Test - Automatisk start och verifiering
4. Git Operations - Add, commit med dynamisk version
5. GitHub Push - Automatisk push till repository
6. File Management - Flyttar EXE till RELEASE_FILES
7. Browser Opening - Öppnar GitHub release sida automatiskt
8. Version Increment - Automatisk version +0.01 för nästa release
```

#### **Centraliserat Versionsystem:**
```python
# core/version.py - Centraliserad versionshantering
APP_VERSION = "0.22"  # Synkat med GitHub
GITHUB_OWNER = "Medzeta"
GITHUB_REPO = "Multi-Team-C"

# Auto-increment funktioner:
get_version() -> str           # Hämta nuvarande version
get_next_version() -> str      # Visa nästa version (0.22 -> 0.23)
increment_version() -> str     # Uppdatera version automatiskt (+0.01)

# Versionssekvens:
v0.22 -> v0.23 -> v0.24 -> v0.25 -> v0.26 -> v0.27 -> v0.28 -> v0.29 -> v0.30
```

#### **GitHub Integration:**
```python
# Repository: https://github.com/Medzeta/Multi-Team-C
# Token: [GITHUB_TOKEN] (Konfigureras lokalt - pushas ej)
# Auto-update API: GitHub Releases API för version checking
# Release Assets: MultiTeam.exe (endast EXE, ingen ZIP)

# FINALPUBLISH Process:
1. Hämtar version dynamiskt från Python
2. Bygger EXE med korrekt version
3. Pushar till GitHub med version tag
4. Öppnar GitHub release sida automatiskt
5. Incrementar version för nästa release
```

#### **Viktiga Säkerhetskoder och Logins:**

**GitHub Repository:**
- **URL:** https://github.com/Medzeta/Multi-Team-C
- **Owner:** Medzeta
- **Token:** `[GITHUB_TOKEN]` ⚠️ PRIVAT (konfigureras lokalt)
- **Email:** medzetadesign@gmail.com

**SuperAdmin Login:**
- **Username:** superadmin
- **Password:** superadmin
- **Behörigheter:** Alla moduler + SuperAdmin Settings

**Database Säkerhet:**
- **Master Key:** data/master.key (JSON med nyckel + salt)
- **Global Salt:** data/salt.key (32 bytes binär)
- **Kryptering:** PBKDF2-SHA256 (100k iterationer)
- **Permissions:** 0600 (endast ägaren)

**Email System (2FA & Reset):**
- **SMTP:** smtp.gmail.com:587
- **Email:** medzetadesign@gmail.com
- **App Password:** [Konfigureras i EmailService]

#### **Auto-Update Funktionalitet:**
```python
# Automatisk version checking mot GitHub API
# Laddar ner nya releases automatiskt
# Säker installation med backup system
# Restart-hantering för uppdateringar

# VersionManager funktioner:
check_for_updates() -> dict    # Kollar GitHub för nya versioner
download_update() -> dict      # Laddar ner från GitHub
install_update() -> dict       # Installerar med backup
```

#### **Release Process (Automatiserad):**
```
1. Kör: .\FINALPUBLISH.bat
2. Systemet bygger EXE automatiskt
3. Pushar till GitHub med version tag
4. Öppnar release sida i browser
5. Dra och släpp MultiTeam.exe
6. Klicka "Publish release"
7. Version incrementas automatiskt för nästa gång
```

---

## 🔐 KOMPLETT LOGIN-MODUL GUIDE

### **ALLA KOMPONENTER ANVÄNDER GLOBAL DESIGN**

#### **1. Card Settings**
```python
card_settings = Theme.get_compact_card_settings()
# width: 420px → 560px (33% bredare)
# height: 520px → 640px (+120 för title)
# padding: 20px
# spacing: 8px
# border_radius: 12px
```

#### **2. Title & Subtitle**
```python
Theme.setup_app_title(title_label, subtitle_label)
card_layout.addSpacing(-45)  # Tight layout
```

#### **2.5. Section Headers**
```python
# För "Sign In", "Create Account" etc.
header_label = QLabel()
Theme.setup_section_header(header_label, "Create Account")
# 20px font, bold, vänsterjusterad, #ffffff
```

#### **3. Text Fields**
```python
Theme.setup_text_field(email_field, placeholder="text")
# Höjd: 26px, Bakgrund: #555555, Border-radius: 3px
```

#### **4. Checkbox**
```python
Theme.setup_checkbox(checkbox, "Remember me")
# Storlek: 18x18px, Bakgrund: #555555
```

#### **5. Buttons**
```python
Theme.setup_login_button(button, width=90)
# Höjd: 25px, Transparent: rgba(58,58,58,0.2)
```

#### **6. Spacing**
```python
Theme.SPACING_XS = 3   # Minimal
Theme.SPACING_LG = 10  # Normal
card_layout.addSpacing(-45)  # Negativ för tight
```

**REGEL: Använd ALLTID Theme.setup_* funktioner - INGEN lokal styling!**

---

## 🔐 REGISTRATION-MODUL DESIGN (GLOBAL STANDARD)

### **SAMMA DESIGN SOM LOGIN-MODUL**

#### **1. Card Settings**
```python
card_settings = Theme.get_compact_card_settings()
# width: 420px → 560px (33% bredare)
# height: 520px → 800px (+280 för extra fält)
# padding: 20px, spacing: 8px, border_radius: 12px
```

#### **2. Input Fields**
```python
# Name, Company, Email, Password, Confirm Password
# Alla använder Theme.setup_text_field()
name_input = QLineEdit()
Theme.setup_text_field(name_input, placeholder="Enter your full name", height=26)
```

#### **3. Verification Form**
```python
# Email icon: 📧 (48px font)
# Code input: 6-digit, centered, 20px font, bold
# Buttons: Verify Email (140px), Resend Code (120px), Back (80px)
```

#### **4. Full Debug Logging**
```python
debug("ModernRegistrationModule", "="*60)
debug("ModernRegistrationModule", "[REG CARD] Creating...")
# Alla steg loggas med [REG CARD] prefix
```

#### **5. Email Validation**
```python
# Regex: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
# SuperAdmin email check
# Existing user check
```

#### **6. Signals**
```python
registration_complete = pyqtSignal(str)  # Emits email
back_to_login = pyqtSignal()
```

**REGEL: Registration följer EXAKT samma design som Login-modul!**

---

## 🎴 CARD/FRAME STANDARD

### **QFrame (Card):**
```python
background-color: #2b2b2b (SURFACE)
border: 2px solid #3a3a3a (BORDER)
border-radius: 10px (RADIUS_MD)
padding: 20px

# Hover (om klickbar):
border-color: #4a4a4a
```

### **Login Card - GLOBAL KOMPAKT DESIGN:**
```python
# Globala card-inställningar (Theme.get_compact_card_settings())
width: 560px (EN TREDJEDEL BREDARE - LÅST STANDARD)
height: 640px (inkluderar Multi Team -C title + subtitle - LÅST STANDARD)
background-color: #2b2b2b (SURFACE - ljusare än huvudfönster)
border: none (ingen ram för ren look)
border-radius: 12px (rundare hörn)
padding: 20px (Theme.CARD_PADDING - kompakt padding)
spacing: 8px (Theme.CARD_SPACING - minimal spacing)

VIKTIGT: Dessa mått är LÅSTA och ska användas för alla framtida moduler!
Beräkning: Original 420px × 1.33 = 560px bredd (33% bredare)

# Card innehåll (uppifrån och ner) - SLUTLIG LÅST PERFEKT LAYOUT:
1. Multi Team -C (40px font, font-weight 900, APP-LOGGA - LÅST)
2. P2P Team Collaboration Platform (14px, margin-top: -50px, ULTRA TIGHT - LÅST)
3. Sign In (20px font, -5px spacing från vänster, PERFEKT BALANS - LÅST)
4. Email input (26px höjd, extremt kompakt)
5. Password input (26px höjd, extremt kompakt)
6. Remember me checkbox (PERFEKT: 98px höger, -5px upp - LÅST)
7. Sign In button (36px höjd)
8. Create New Account button (34px höjd)
9. Forgot Password button (34px höjd)

ALLA DESSA MÅTT ÄR LÅSTA OCH SKA ANVÄNDAS FÖR ALLA FRAMTIDA MODULER!

# Positioning:
position: center av huvudfönster
margin: auto

# Global design:
Använder Theme.get_compact_card_settings() för konsistens
Ljusare bakgrund (#2b2b2b) än huvudfönster (#1a1a1a)
Rundade hörn för modern känsla
Kompakt spacing mellan alla element
Perfekt checkbox-justering för alla framtida moduler
```

---

## 📜 SCROLLBAR STANDARD

### **Vertikal Scrollbar:**
```python
# FULLT OSYNLIG MEN FUNGERANDE:
QScrollBar:vertical {
    background-color: transparent;
    width: 0px;
    border: none;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: transparent;
    border: none;
    border-radius: 0px;
    min-height: 0px;
    max-height: 0px;
    width: 0px;
}

QScrollBar::handle:vertical:hover {
    background-color: transparent;
    border: none;
    width: 0px;
}

QScrollBar::add-line:vertical {
    background-color: transparent;
    border: none;
    height: 0px;
    width: 0px;
}

QScrollBar::sub-line:vertical {
    background-color: transparent;
    border: none;
    height: 0px;
    width: 0px;
}

QScrollBar::add-page:vertical {
    background-color: transparent;
    border: none;
}

QScrollBar::sub-page:vertical {
    background-color: transparent;
    border: none;
}
```

**VIKTIGT:** Alla textfält måste använda `Theme.setup_text_field()` funktionen!

**IMPLEMENTERING:**
```python
from core.pyqt_theme import Theme

# För QLineEdit (enkelt textfält)
email_input = QLineEdit()
Theme.setup_text_field(email_input, placeholder="Email", height=45)

# För QTextEdit (multi-line)
description = QTextEdit()
Theme.setup_text_field(description, placeholder="Description", height=100)
```

**Vad funktionen gör:**
1. Sätter placeholder text och fixed height
2. Applicerar exakt GLOBAL_DESIGN.md styling
3. Bakgrund: #555555, Focus: #666666, margin-bottom: -9px
4. Full debug-logging för felsökning

**VIKTIGT - Spacing mellan textfält:**
För att undvika konflikter med layout-spacing, använd DIREKT negativ spacing i layouten:

```python
# I QVBoxLayout - använd DIREKT addSpacing() istället för CSS margins
input_layout.addWidget(email_field)
input_layout.addSpacing(-20)  # Dra samman helt - motsvarar hela fältets höjd
input_layout.addWidget(password_field)
```

**Detta OVERRIDE alla CSS margins och ger pixel-perfekt kontroll!**

---

## 🎯 SPACING SYSTEM

```python
SPACING_XS = 5px        # Minimal spacing
SPACING_SM = 10px       # Små element
SPACING_MD = 20px       # Medium spacing
SPACING_LG = 30px       # Stora sektioner
SPACING_XL = 40px       # Extra stora sektioner
SPACING_COMPACT = 3px   # Kompakt spacing (login inputs, 1/4 av SM)
```

**Användning:**
- Mellan knappar: 10px (SPACING_SM)
- Mellan sektioner: 20px (SPACING_MD)
- Card padding: 20-30px (SPACING_MD/LG)
- Layout margins: 15px

---

## 🔤 TYPOGRAFI

### **Font Family:**
```python
Primary: "Segoe UI"
Fallback: "Arial", "Helvetica", sans-serif
```

### **Font Sizes:**
```python
FONT_XS = 10px      # Captions, hints
FONT_SM = 11px      # Secondary text
FONT_MD = 14px      # Body text, buttons
FONT_LG = 16px      # Headings
FONT_XL = 20px      # Large headings
FONT_XXL = 24px     # Page titles
FONT_XXXL = 28px    # Hero text
```

### **Font Weights:**
```python
Normal: 400
Medium: 500
Bold: 600
```

---

## 🎨 QSS TEMPLATE (GLOBAL)

```python
def get_stylesheet():
    return f"""
        /* Global */
        * {{
            font-family: "Segoe UI", Arial, sans-serif;
            font-size: {Theme.FONT_MD}px;
        }}
        
        /* Main Window */
        QMainWindow {{
            background-color: {Theme.BACKGROUND};
        }}
        
        /* Buttons */
        QPushButton {{
            background-color: {Theme.PRIMARY};
            color: {Theme.TEXT};
            border: none;
            border-radius: {Theme.RADIUS_SM}px;
            padding: 10px 20px;
            min-height: 40px;
        }}
        
        QPushButton:hover {{
            background-color: {Theme.PRIMARY_HOVER};
        }}
        
        QPushButton[secondary="true"] {{
            background-color: {Theme.SECONDARY};
        }}
        
        QPushButton[secondary="true"]:hover {{
            background-color: {Theme.SECONDARY_HOVER};
        }}
        
        /* Input Fields */
        QLineEdit {{
            background-color: {Theme.SURFACE};
            color: {Theme.TEXT};
            border: none;
            border-radius: {Theme.RADIUS_SM}px;
            padding: 10px;
            min-height: 40px;
        }}
        
        QLineEdit:focus {{
            background-color: {Theme.ACTIVE};
        }}
        
        /* Cards */
        QFrame {{
            background-color: {Theme.SURFACE};
            border: 2px solid {Theme.BORDER};
            border-radius: {Theme.RADIUS_MD}px;
        }}
        
        /* Scrollbars - Osynlig */
        QScrollBar:vertical {{
            width: 0px;
            background-color: transparent;
        }}
    """
```

---

## 📦 MODUL STRUKTUR

### **Alla Moduler MÅSTE:**
```python
1. Ärva från QWidget
2. Använda Theme-klassen för färger
3. Använda RADIUS-konstanter för rundade hörn
4. Följa spacing-systemet
5. Implementera _create_ui() metod
6. Använda signals för kommunikation
```

### **Mall för Ny Modul:**
```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from core.pyqt_theme import Theme

class MyModule(QWidget):
    # Signals
    back_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._create_ui()
    
    def _create_ui(self):
        """Create UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(Theme.SPACING_MD)
        
        # Ditt innehåll här
        # Använd Theme.* för alla färger och spacing
```

---

## 🚫 FÖRBJUDNA ELEMENT

### **ANVÄND ALDRIG:**
```python
❌ QDialog (använd CustomDialog)
❌ QMessageBox (använd CustomDialog)
❌ OS-fönster (använd CustomWindow)
❌ Hårdkodade färger (använd Theme.*)
❌ Hårdkodade spacing (använd Theme.SPACING_*)
❌ Hårdkodade border-radius (använd Theme.RADIUS_*)
❌ Inline styles (använd QSS)
❌ Separata fönster (använd modul-switching)
```

---

## ✅ CHECKLISTA FÖR NYA KOMPONENTER

Innan du skapar en ny komponent, kontrollera:

- [ ] Använder Theme-klassen för ALLA färger
- [ ] Använder RADIUS-konstanter för rundade hörn
- [ ] Använder SPACING-konstanter för spacing
- [ ] Följer button-standard
- [ ] Följer input-standard
- [ ] Följer card-standard
- [ ] Ingen hårdkodad styling
- [ ] QSS för all styling
- [ ] Signals för kommunikation
- [ ] Dokumenterad kod
- [ ] Testad i huvudfönster

---

## 🎯 EXEMPEL: KOMPLETT LOGIN CARD

```python
# Login card
card = QFrame()
card.setFixedSize(450, 550)
card.setStyleSheet(f"""
    QFrame {{
        background-color: {Theme.SURFACE};
        border: 2px solid {Theme.BORDER};
        border-radius: {Theme.RADIUS_MD}px;
    }}
""")

card_layout = QVBoxLayout(card)
card_layout.setSpacing(Theme.SPACING_SM)
card_layout.setContentsMargins(20, 20, 20, 20)

# Email input
email_input = QLineEdit()
email_input.setPlaceholderText("Email")
email_input.setFixedHeight(45)
card_layout.addWidget(email_input)

# Password input
password_input = QLineEdit()
password_input.setPlaceholderText("Password")
password_input.setEchoMode(QLineEdit.EchoMode.Password)
password_input.setFixedHeight(45)
card_layout.addWidget(password_input)

# Login button
login_btn = QPushButton("Login")
login_btn.setFixedHeight(45)
card_layout.addWidget(login_btn)
```

---

## 📚 REFERENS-FILER

### **Läs Dessa Filer:**
```
core/pyqt_theme.py          # Theme-klassen med alla konstanter
core/pyqt_window.py         # CustomWindow implementation
modules_pyqt/login_module.py # Exempel på korrekt modul
PYQT6_WINDOW_STANDARD.md    # Window standard dokumentation
```

---

## 🔄 UPPDATERINGSHISTORIK

**Version 1.0 (2025-10-02):**
- Initial version
- Alla design-regler definierade
- Window controls: Grön-Gul-Röd (18x18px)
- Titlebar: 60px med användarinfo
- Färgschema fastställt
- Rundade hörn: 5/10/15px

---

## ⚠️ VIKTIGT

**DENNA FIL ÄR OBLIGATORISK STANDARD!**

Alla nya komponenter MÅSTE följa dessa regler.  
Vid tveksamhet, referera till denna fil.  
Vid ändringar, uppdatera denna fil FÖRST.

**Konsistens är nyckeln till professionell design!**

---

**Skapad:** 2025-10-02  
**Av:** Cascade AI Assistant  
**För:** Multi Team -C Project  
**Status:** OBLIGATORISK STANDARD

**FÖLJ DENNA DESIGN I HELA APPEN!** 🎨✨💯


# 🚀 MultiTeam P2P Communication - Startup Guide

## Snabbstart

### 1. Installera Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Starta Applikationen
```powershell
python main.py
```

### 3. Logga in som SuperAdmin
- **Email**: `admin@multiteam.local`
- **Password**: `SuperAdmin123!`

## 📋 Funktioner

### ✅ Implementerat

#### Custom Borderless UI
- Helt egen fönsterdesign utan Windows standard-ramar
- Draggable title bar
- Custom minimize/maximize/close buttons
- Dark mode theme
- Responsive design

#### Autentisering
- **SuperAdmin**: Hårdkodat admin-konto (admin@multiteam.local)
- **User Login**: Email och lösenord
- **Registration**: Komplett registreringsflöde
- **Email Verification**: 6-siffrig kod skickas via Gmail
- **Password Security**: bcrypt hashing med salt

#### Modulärt System
- Window-in-window arkitektur
- Moduler öppnas sömlöst i huvudfönstret
- Enkel navigation mellan moduler
- Varje feature är en separat modul

#### Debug System
- Full logging på varje rad kod
- Timestampade log-filer i `logs/` mappen
- Olika log-nivåer (DEBUG, INFO, WARNING, ERROR)
- Console output för viktiga events

## 🎯 Användning

### Första Gången

1. **Starta applikationen**
   ```powershell
   python main.py
   ```

2. **Testa SuperAdmin login**
   - Email: `admin@multiteam.local`
   - Password: `SuperAdmin123!`
   - Detta konto fungerar alltid utan registrering

3. **Skapa ett vanligt användarkonto**
   - Klicka på "Create New Account"
   - Fyll i:
     - Full Name (ditt namn)
     - Company (ditt företag)
     - Email (din email)
     - Password (valfritt lösenord, inga krav)
   - Klicka "Create Account"

4. **Verifiera din email**
   - Kolla din inbox för verifieringskod
   - Ange 6-siffrig kod i appen
   - Klicka "Verify Email"

5. **Logga in**
   - Använd din email och lösenord
   - Du är nu inloggad!

### Email Verifiering

Applikationen använder Gmail SMTP för att skicka verifieringskoder:

- **Från**: MultiTeamCommunication@gmail.com
- **Format**: HTML email med 6-siffrig kod
- **Timeout**: 15 minuter
- **Resend**: Kan begära ny kod om behövs

**OBS**: Kontrollera spam-mappen om du inte ser emailet!

### Dashboard

Efter inloggning ser du:
- Välkomstmeddelande med ditt namn
- Kontoinformation (email, företag, roll, status)
- "Coming Soon" features
- Logout-knapp

## 🏗️ Projektstruktur

```
Multi Team -C/
│
├── main.py                    # Huvudapplikation - starta här
├── requirements.txt           # Python dependencies
├── ROADMAP.md                # Utvecklingsplan
├── README.md                 # Projektdokumentation
├── STARTUP_GUIDE.md          # Denna fil
├── build_exe.py              # Script för att bygga EXE
│
├── core/                     # Kärnfunktionalitet
│   ├── __init__.py
│   ├── debug_logger.py      # Debug logging system
│   ├── custom_window.py     # Borderless window system
│   ├── ui_components.py     # Globala UI komponenter
│   ├── auth_system.py       # Autentisering + SuperAdmin
│   └── email_service.py     # Email verifiering
│
├── modules/                  # Applikationsmoduler
│   ├── __init__.py
│   ├── login_module.py      # Login UI och logik
│   └── registration_module.py # Registration + verification
│
├── data/                     # Skapas automatiskt
│   └── users.db             # SQLite databas
│
└── logs/                     # Skapas automatiskt
    └── multiteam_*.log      # Debug logs med timestamp
```

## 🐛 Debugging

### Logs

Alla logs sparas i `logs/` mappen:
```
logs/multiteam_20250930_091519.log
```

Varje log-rad innehåller:
- **Timestamp**: När händelsen inträffade
- **Level**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Module**: Vilken modul som loggade
- **Message**: Vad som hände

### Exempel Log
```
2025-09-30 09:15:19 | INFO  | MultiTeam | [LoginModule] Login successful for: test@example.com
2025-09-30 09:15:19 | DEBUG | MultiTeam | [AuthSystem] User found: test@example.com (verified: True)
```

### Vanliga Problem

#### "ModuleNotFoundError: No module named 'customtkinter'"
**Lösning**: Installera dependencies
```powershell
pip install -r requirements.txt
```

#### "Failed to send verification email"
**Möjliga orsaker**:
- Ingen internetanslutning
- Gmail SMTP blockerad av firewall
- App password har ändrats

**Lösning**: Kontrollera internetanslutning och försök igen

#### "User already exists"
**Orsak**: Email redan registrerad

**Lösning**: 
- Använd en annan email
- Eller logga in med befintligt konto

#### Fönstret syns inte
**Lösning**: 
- Kolla taskbar
- Tryck Alt+Tab för att hitta fönstret
- Starta om applikationen

## 🔧 Utveckling

### Lägg till Ny Modul

1. **Skapa modul-fil** i `modules/`
```python
# modules/my_module.py
import customtkinter as ctk
from core.debug_logger import debug, info
from core.ui_components import CustomButton, CustomLabel

class MyModule(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        debug("MyModule", "Initializing...")
        super().__init__(master, fg_color="transparent", **kwargs)
        self._create_ui()
        info("MyModule", "Initialized")
    
    def _create_ui(self):
        label = CustomLabel(self, text="My Module", size=20, bold=True)
        label.pack(pady=20)
```

2. **Importera i main.py**
```python
from modules.my_module import MyModule
```

3. **Visa modulen**
```python
def _show_my_module(self):
    info("MultiTeamApp", "Showing my module")
    self._clear_content()
    self.current_module = MyModule(self.window.content_frame)
    self.current_module.pack(fill="both", expand=True)
```

### Använd Debug Logging

```python
from core.debug_logger import debug, info, warning, error, exception

# Olika nivåer
debug("ModuleName", "Detailed debug info")
info("ModuleName", "Important information")
warning("ModuleName", "Warning message")
error("ModuleName", "Error occurred")

# Med exception traceback
try:
    # kod som kan faila
    pass
except Exception as e:
    exception("ModuleName", "Error description")
```

### Custom UI Components

```python
from core.ui_components import (
    CustomButton, CustomEntry, CustomLabel,
    CustomFrame, CustomCheckbox, MessageBox
)

# Button styles: primary, secondary, success, danger, transparent
button = CustomButton(parent, text="Click", style="primary")

# Entry field
entry = CustomEntry(parent, placeholder="Enter text", width=300)
value = entry.get_value()  # Get text
entry.set_value("New text")  # Set text

# Labels
label = CustomLabel(parent, text="Hello", size=14, bold=True)

# Message boxes
MessageBox.show_info(parent, "Title", "Message")
MessageBox.show_error(parent, "Error", "Error message")
MessageBox.show_success(parent, "Success", "Success message")
MessageBox.show_confirm(parent, "Confirm", "Are you sure?", on_confirm_callback)
```

## 📦 Bygg EXE

### Installera PyInstaller
```powershell
pip install pyinstaller
```

### Kör Build Script
```powershell
python build_exe.py
```

### Resultat
EXE och alla filer finns i:
```
dist/MultiTeam_Package/
├── MultiTeam.exe
├── README.md
├── ROADMAP.md
├── QUICK_START.txt
├── data/
└── logs/
```

### Manuell Build (alternativ)
```powershell
pyinstaller --name="MultiTeam" --onefile --windowed main.py
```

## 🔐 Säkerhet

### Password Security
- **Hashing**: bcrypt med automatisk salt
- **Requirements**: Inga krav - användaren väljer fritt
- **Storage**: Endast hash sparas, aldrig plaintext

### Email Verification
- **Code**: 6 siffror, slumpmässigt genererad
- **Timeout**: 15 minuter
- **Storage**: Sparas i databas tills verifierad
- **Resend**: Ny kod kan begäras

### SuperAdmin
- **Hårdkodat**: Finns alltid, kan inte tas bort
- **Separerat**: Inte i user database
- **Access**: Full systemadministration

### Database
- **Type**: SQLite (lokal fil)
- **Location**: `data/users.db`
- **Protection**: Parametriserade queries (SQL injection safe)
- **Backup**: Rekommenderas att backup:a `data/` mappen

## 📞 Support

### Loggar
Kontrollera alltid logs först:
```powershell
type logs\multiteam_*.log
```

### Vanliga Kommandon
```powershell
# Starta app
python main.py

# Installera dependencies
pip install -r requirements.txt

# Bygg EXE
python build_exe.py

# Visa logs
type logs\multiteam_*.log

# Rensa databas (OBS: tar bort alla users!)
del data\users.db
```

## 🎨 UI Customization

### Färger
Definierade i `core/ui_components.py`:
- **Primary**: Blå (#1f6aa5)
- **Success**: Grön (#107c10)
- **Danger**: Röd (#c42b1c)
- **Secondary**: Grå (#3a3a3a)

### Fonts
- **Standard**: Segoe UI
- **Monospace**: Courier New (för koder)
- **Sizes**: 9-48px beroende på element

### Dark Mode
Applikationen använder alltid dark mode:
- **Background**: #1a1a1a / #2b2b2b
- **Text**: #ffffff
- **Borders**: #2a2a2a / #3a3a3a

## 🚀 Nästa Steg

Efter att du har testat grundfunktionaliteten, se ROADMAP.md för:
- P2P Network Implementation
- Team Management
- Direct Messaging
- File Sharing
- Voice/Video Calls
- 2FA Authentication
- Google Login

---

**Version**: 0.1.0 (Alpha)  
**Last Updated**: 2025-09-30  
**Status**: ✅ Fully Functional

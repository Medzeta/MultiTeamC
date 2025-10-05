# Build Debug Guide - MultiTeam V0.20

## Problem Identifierat
Build processen crashar eller hänger sig under PyInstaller-steget. Här är lösningar:

## Lösning 1: Enkel Build (Rekommenderat)

### Kör Minimal Build:
```bash
# Enklaste möjliga build
python -m PyInstaller --onefile --windowed main_pyqt.py

# Om det fungerar, kör full build:
python -m PyInstaller --name=MultiTeam --onefile --windowed --noconfirm main_pyqt.py
```

### Testa EXE:
```bash
# Testa om EXE fungerar
dist\main_pyqt.exe
```

## Lösning 2: Debug Build Steg-för-Steg

### Steg 1: Testa Dependencies
```bash
python -c "import PyQt6; print('PyQt6 OK')"
python -c "import PIL; print('PIL OK')"  
python -c "import requests; print('requests OK')"
python -c "import bcrypt; print('bcrypt OK')"
```

### Steg 2: Minimal PyInstaller Test
```bash
# Skapa minimal spec fil
python -m PyInstaller --onefile main_pyqt.py --log-level=DEBUG
```

### Steg 3: Kolla Output
```bash
# Kolla om EXE skapades
dir dist\
```

## Lösning 3: Använd Quick Build

### Kör Quick Build Script:
```bash
.\quick_build.bat
```

Detta script gör:
1. Minimal PyInstaller build
2. Skapar package directory  
3. Kopierar filer
4. Skapar ZIP

## Vanliga Problem & Lösningar

### Problem 1: PyInstaller Hänger
**Lösning:** Använd `--log-level=WARN` istället för DEBUG
```bash
python -m PyInstaller --name=MultiTeam --onefile --windowed --noconfirm --log-level=WARN main_pyqt.py
```

### Problem 2: Import Errors
**Lösning:** Lägg till explicit hidden imports
```bash
python -m PyInstaller --onefile --windowed --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtWidgets main_pyqt.py
```

### Problem 3: File Not Found
**Lösning:** Kör från rätt directory
```bash
cd "C:\Multi Team -C"
python -m PyInstaller main_pyqt.py
```

### Problem 4: Permission Denied
**Lösning:** Kör som Administrator eller stäng antivirus

## Snabb Test Sekvens

### 1. Minimal Test:
```bash
python main_pyqt.py
# Om detta fungerar, fortsätt till steg 2
```

### 2. PyInstaller Test:
```bash
python -m PyInstaller --onefile main_pyqt.py
# Om detta fungerar, testa EXE:
dist\main_pyqt.exe
```

### 3. Full Build:
```bash
.\quick_build.bat
# Eller:
python build_exe.py
```

## Debug Output Locations

### Build Logs:
- `build_logs\build_*.log` - Enhanced build script logs
- `logs\multiteam_*.log` - Application logs
- `build\` - PyInstaller work directory
- `dist\` - Output directory

### Viktiga Filer att Kolla:
- `dist\MultiTeam.exe` - Huvudfil
- `dist\MultiTeam_Package\` - Package directory
- `build\MultiTeam\` - PyInstaller build artifacts

## Om Allt Annat Misslyckas

### Alternativ 1: Använd Python Direkt
```bash
# Kör appen direkt utan EXE
python main_pyqt.py
```

### Alternativ 2: Skapa Enkel Launcher
Skapa `run_multiteam.bat`:
```batch
@echo off
cd /d "%~dp0"
python main_pyqt.py
pause
```

### Alternativ 3: Använd cx_Freeze
```bash
pip install cx_freeze
# Skapa setup.py för cx_Freeze istället
```

## Status Check Commands

### Kolla Build Status:
```bash
# Kolla om PyInstaller kör
tasklist | findstr python

# Kolla build directory
dir build\

# Kolla dist directory  
dir dist\

# Kolla senaste loggar
dir /od logs\*.log
```

## Rekommenderad Troubleshooting Ordning

1. **Kör `python main_pyqt.py`** - Verifiera att appen fungerar
2. **Kör `.\quick_build.bat`** - Enkel build utan progress bar
3. **Testa `dist\MultiTeam.exe`** - Kolla om EXE fungerar
4. **Om problem, kör minimal:** `python -m PyInstaller --onefile main_pyqt.py`
5. **Kolla logs** i `build_logs\` för detaljer

---

**Nästa steg:** När build fungerar, testa auto-update systemet genom att klicka Settings → Check for Updates (bör visa Development Mode).

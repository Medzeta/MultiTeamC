# Deploy Guide för MultiTeam V0.20

## Snabbstart - Publicera V0.20 Release

### 1. Förbered GitHub Authentication

**Option A: GitHub CLI (Rekommenderat)**
```bash
# Installera GitHub CLI från: https://cli.github.com/
gh auth login
# Välj: GitHub.com → HTTPS → Login with browser
gh auth status  # Verifiera
```

**Option B: Personal Access Token**
```bash
# Skapa PAT på: https://github.com/settings/tokens
# Scope: repo (full repository access)

# Sätt miljövariabler:
setx GH_OWNER Medzeta
setx GH_REPO Multi-Team-C
setx GH_TOKEN your_token_here
setx RELEASE_NOTES_FILE "C:\Multi Team -C\RELEASE_NOTES_V0.20.md"

# Starta om terminal för att ladda env vars
```

### 2. Navigera till Repo

```bash
cd "C:\Users\Medzeta\Documents\GitHub\Multi Team -C"
```

### 3. Publicera V0.20 Release

```bash
# Enkel release med default V0.20
release_github.bat

# Eller specificera version explicit
release_github.bat 0.20
```

## Vad Händer Under Release

### Steg 1: Build Process
- Kör `python build_exe.py`
- Skapar `dist/MultiTeam_Package/MultiTeam.exe`
- Kopierar README.md, ROADMAP.md, QUICK_START.txt
- Skapar data/ och logs/ mappar

### Steg 2: Package Creation
- Skapar ZIP: `dist/MultiTeam_Package_v0.20.zip`
- Innehåller hela MultiTeam_Package mappen

### Steg 3: GitHub Release
- Skapar release tag: `v0.20`
- Release titel: "MultiTeam 0.20"
- Laddar upp ZIP som asset
- Inkluderar release notes från `RELEASE_NOTES_V0.20.md`

## Verifiera Release

### 1. Kontrollera GitHub
- Gå till: https://github.com/Medzeta/Multi-Team-C/releases
- Verifiera att `v0.20` release finns
- Kontrollera att ZIP-filen är uppladdad

### 2. Testa Auto-Update
- Starta din lokala app (äldre version)
- Gå till Settings → Auto-Update
- Klicka "Check for Updates"
- Bör visa: "Update Available: v0.20"

### 3. Testa Download & Install
- Klicka "Download Update"
- Vänta på download completion
- Klicka "Install & Restart"
- Appen bör starta om med V0.20

## Felsökning

### GitHub CLI Problem
```bash
# Om gh inte är autentiserad
gh auth login

# Om gh inte hittas
# Installera från: https://cli.github.com/
```

### PAT Problem
```bash
# Kontrollera env vars
echo %GH_OWNER%
echo %GH_REPO%
echo %GH_TOKEN%

# Om tomma, sätt igen och starta om terminal
```

### Build Problem
```bash
# Kontrollera Python
python --version

# Kontrollera dependencies
pip install -r requirements.txt

# Manuell build test
python build_exe.py
```

### ZIP Problem
```bash
# Kontrollera PowerShell
powershell -Command "Get-Command Compress-Archive"

# Manuell ZIP test
powershell -Command "Compress-Archive -Path 'dist/MultiTeam_Package/*' -DestinationPath 'test.zip'"
```

## Framtida Releases

### Nästa Version (V0.21)
1. Uppdatera `core/version.py`:
   ```python
   APP_VERSION = "0.21"
   ```

2. Skapa nya release notes:
   ```bash
   copy RELEASE_NOTES_V0.20.md RELEASE_NOTES_V0.21.md
   # Redigera innehåll
   ```

3. Uppdatera env var:
   ```bash
   setx RELEASE_NOTES_FILE "C:\Multi Team -C\RELEASE_NOTES_V0.21.md"
   ```

4. Kör release:
   ```bash
   release_github.bat 0.21
   ```

## Automatisering Tips

### Batch Script för Snabb Release
Skapa `quick_release.bat`:
```batch
@echo off
set /p VERSION="Enter version (e.g. 0.21): "
echo Releasing version %VERSION%...

REM Update version in code (manual step reminder)
echo Remember to update core/version.py to %VERSION%

REM Run release
release_github.bat %VERSION%

echo Release %VERSION% completed!
pause
```

### Release Checklist
- [ ] Uppdatera `core/version.py`
- [ ] Skapa/uppdatera release notes
- [ ] Testa appen lokalt
- [ ] Kör `release_github.bat`
- [ ] Verifiera GitHub release
- [ ] Testa auto-update från äldre version

## Support

### GitHub Repository
- **URL**: https://github.com/Medzeta/Multi-Team-C
- **Issues**: https://github.com/Medzeta/Multi-Team-C/issues
- **Releases**: https://github.com/Medzeta/Multi-Team-C/releases

### Viktiga Filer
- `release_github.bat` - Huvudrelease script
- `scripts/upload_release.ps1` - API fallback
- `core/version.py` - Versionshantering
- `build_exe.py` - Build process
- `UPDATE_RELEASE_GUIDE.md` - Detaljerad guide

---

**Lycka till med V0.20 releasen! 🚀**

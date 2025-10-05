# GitHub Repository Setup Guide

## Problem: Inga Releases Än

API-felet beror på att GitHub repository `Medzeta/Multi-Team-C` antingen inte finns eller har inga releases än.

## Lösning: Skapa Repository & Första Release

### 1. Skapa GitHub Repository

**Option A: Via GitHub Web Interface**
1. Gå till: https://github.com/new
2. Repository name: `Multi-Team-C`
3. Owner: `Medzeta`
4. Visibility: Public (för auto-update att fungera)
5. Klicka "Create repository"

**Option B: Via GitHub CLI**
```bash
gh repo create Medzeta/Multi-Team-C --public --description "MultiTeam P2P Communication System"
```

### 2. Pusha Kod till Repository

```bash
# Navigera till din lokala kod
cd "C:\Users\Medzeta\Documents\GitHub\Multi Team -C"

# Initiera git (om inte redan gjort)
git init

# Lägg till remote
git remote add origin https://github.com/Medzeta/Multi-Team-C.git

# Lägg till alla filer
git add .

# Första commit
git commit -m "Initial commit - MultiTeam v0.20 with auto-update system"

# Pusha till GitHub
git push -u origin main
```

### 3. Skapa Första Release (V0.20)

**Automatiskt via Script:**
```bash
# Sätt upp GitHub authentication först
gh auth login

# Kör release script
release_github.bat 0.20
```

**Manuellt via GitHub Web:**
1. Gå till: https://github.com/Medzeta/Multi-Team-C/releases
2. Klicka "Create a new release"
3. Tag version: `v0.20`
4. Release title: `MultiTeam 0.20`
5. Beskrivning: Kopiera från `RELEASE_NOTES_V0.20.md`
6. Ladda upp: `dist/MultiTeam_Package_v0.20.zip`
7. Klicka "Publish release"

## 3. Verifiera Setup

### Testa API Access:
```bash
python test_github_api.py
```

**Förväntat resultat efter setup:**
```
✅ API call successful!
Latest release: v0.20
Release name: MultiTeam 0.20
Published: 2025-10-05T...

```
Development Mode
No GitHub releases found yet. This is normal during development.

Next Steps:
1. Push code to GitHub repository
2. Run release_github.bat 0.20 to create first release
3. Auto-update will then work normally
```

## 5. Framtida Releases

Efter första release är setup:

```bash
# Uppdatera version
# Redigera core/version.py → APP_VERSION = "0.21"

# Skapa ny release
release_github.bat 0.21
```

## Troubleshooting

### Repository Access Problem
- Kontrollera att repository är **public**
- Verifiera URL: https://github.com/Medzeta/Multi-Team-C

### Authentication Problem
```bash
# GitHub CLI
gh auth status
gh auth login

# PAT (Personal Access Token)
setx GH_OWNER Medzeta
setx GH_REPO Multi-Team-C
setx GH_TOKEN your_token_here
```

### Build Problem
```bash
# Testa build
python build_exe.py

# Kontrollera output
dir dist\MultiTeam_Package\
```

## Status

- ❌ **Repository:** Behöver skapas
- ❌ **Första Release:** Behöver skapas  
- ✅ **Auto-Update Code:** Redo och fungerar
- ✅ **Release Scripts:** Redo att använda
- ✅ **Development Mode:** Fungerar som fallback

**Nästa steg:** Skapa GitHub repository och kör första release!

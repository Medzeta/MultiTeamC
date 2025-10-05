# 🔐 SNABBGUIDE: GITHUB TOKEN & REPOSITORY

## ✅ DU ÄR HÄR NU (Personal Access Token sida)

### STEG 1: Fyll i Token-information

**Token name:** `MultiTeam-Releases`

**Expiration:** `No expiration`

**Select scopes (VIKTIGT - kryssa i dessa):**
- ✅ **repo** (hela sektionen - expandera och kryssa i ALLA)

### STEG 2: Skapa Token
1. Scrolla ner
2. Klicka **"Generate token"**
3. **KOPIERA TOKEN DIREKT!** (visas bara EN gång)
   - Ser ut som: `ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXX`

---

## 📝 EFTER DU FÅR TOKEN:

### STEG 3: Skapa Repository
```
1. Gå till: https://github.com/new
2. Repository name: Multi-Team-C
3. Description: MultiTeam Auto-Update Releases
4. Visibility: Public
5. Klicka "Create repository"
```

### STEG 4: Uppdatera Git Remote
```bash
cd "C:\Multi Team -C"

# Ta bort gammal remote
git remote remove origin

# Lägg till ny med din token
git remote add origin https://Medzeta:DIN_NYA_TOKEN@github.com/Medzeta/Multi-Team-C.git
```

### STEG 5: Pusha Kod (ENDAST RELEASE FILES)
```bash
# Skapa .gitignore för att INTE pusha känsliga filer
echo data/ >> .gitignore
echo logs/ >> .gitignore
echo __pycache__/ >> .gitignore
echo *.pyc >> .gitignore
echo .venv/ >> .gitignore
echo build/ >> .gitignore
echo updates/ >> .gitignore

# Lägg till och committa
git add .
git commit -m "Initial commit - Release system only"
git push -u origin main
```

### STEG 6: Skapa Första Release
```
1. Bygg EXE:
   python build_exe.py

2. Gå till: https://github.com/Medzeta/Multi-Team-C/releases/new

3. Fyll i:
   - Tag: v0.32
   - Title: MultiTeam v0.32
   - Description: First release with auto-update

4. Dra och släpp: dist\MultiTeam.exe

5. Klicka "Publish release"
```

---

## 🎯 KLART!

Nu kan auto-update systemet:
- ✅ Hitta releases på GitHub
- ✅ Ladda ner MultiTeam.exe
- ✅ Uppdatera klienter automatiskt

---

## 🔒 SÄKERHET:

**VAD SOM PUSHAS:**
- ✅ Python kod (*.py)
- ✅ README, ROADMAP
- ✅ requirements.txt

**VAD SOM INTE PUSHAS:**
- ❌ data/ (databas med lösenord)
- ❌ logs/ (logfiler)
- ❌ .venv/ (Python environment)
- ❌ build/ (build-filer)
- ❌ EXE-filer (läggs endast i Releases)

**Endast EXE-filen läggs upp i Releases, inte i repository!**

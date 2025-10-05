@echo off
title GitHub Connection Test
echo ============================================
echo  GitHub Connection Test för MultiTeam
echo  Testar koppling till GitHub
echo ============================================

echo.
echo STEG 1: Testar internetanslutning...
ping github.com -n 2 >nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Internetanslutning fungerar
) else (
    echo ❌ Ingen internetanslutning till GitHub
    pause
    exit /b 1
)

echo.
echo STEG 2: Testar Git installation...
git --version
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Git inte installerat
    echo Ladda ner från: https://git-scm.com/
    pause
    exit /b 1
) else (
    echo ✅ Git installerat
)

echo.
echo STEG 3: Kontrollerar Git konfiguration...
echo Nuvarande Git config:
git config --global user.name
git config --global user.email

echo.
echo STEG 4: Testar repository access...
echo Testar om repository finns och är tillgängligt...
git ls-remote https://github.com/Medzeta/Multi-Team-C.git
if %ERRORLEVEL% EQU 0 (
    echo ✅ Repository tillgängligt
) else (
    echo ❌ Kan inte komma åt repository
    echo.
    echo MÖJLIGA ORSAKER:
    echo 1. Repository finns inte på GitHub
    echo 2. Repository är privat och kräver authentication
    echo 3. GitHub credentials saknas
)

echo.
echo STEG 5: Testar push med credentials...
echo Försöker pusha till GitHub...
git push https://github.com/Medzeta/Multi-Team-C.git main --dry-run
if %ERRORLEVEL% EQU 0 (
    echo ✅ Push skulle fungera
) else (
    echo ❌ Push misslyckades - credentials problem
)

echo.
echo ============================================
echo  GITHUB SETUP INSTRUKTIONER
echo ============================================
echo.
echo Om push misslyckades behöver du:
echo.
echo 📋 ALTERNATIV 1 - Personal Access Token (Rekommenderat):
echo 1. Gå till: https://github.com/settings/tokens
echo 2. Klicka "Generate new token" → "Generate new token (classic)"
echo 3. Ge token ett namn: "MultiTeam-Deploy"
echo 4. Välj scopes: "repo" (full repository access)
echo 5. Klicka "Generate token"
echo 6. KOPIERA TOKEN (visas bara en gång!)
echo 7. Använd token som lösenord när Git frågar
echo.
echo 📋 ALTERNATIV 2 - SSH Keys:
echo 1. Generera SSH key: ssh-keygen -t ed25519 -C "medzetadesign@gmail.com"
echo 2. Lägg till på GitHub: https://github.com/settings/keys
echo 3. Ändra remote URL till SSH
echo.
echo 📋 ALTERNATIV 3 - GitHub CLI:
echo 1. Installera GitHub CLI: https://cli.github.com/
echo 2. Kör: gh auth login
echo 3. Följ instruktionerna
echo.
echo ============================================
echo  SNABB LÖSNING MED TOKEN
echo ============================================
echo.
echo 1. Skapa Personal Access Token (se ovan)
echo 2. Kör detta kommando med ditt token:
echo.
echo git remote set-url origin https://Medzeta:DIN_TOKEN@github.com/Medzeta/Multi-Team-C.git
echo.
echo Ersätt "DIN_TOKEN" med ditt riktiga token
echo.
echo ============================================
echo  REPOSITORY STATUS
echo ============================================

echo Kontrollerar om repository finns på GitHub...
curl -s -o nul -w "%%{http_code}" https://github.com/Medzeta/Multi-Team-C > temp_status.txt
set /p http_status=<temp_status.txt
del temp_status.txt

if "%http_status%"=="200" (
    echo ✅ Repository finns på GitHub: https://github.com/Medzeta/Multi-Team-C
) else if "%http_status%"=="404" (
    echo ❌ Repository finns INTE på GitHub
    echo.
    echo Du behöver skapa repository först:
    echo 1. Gå till: https://github.com/new
    echo 2. Repository name: Multi-Team-C
    echo 3. Välj Public eller Private
    echo 4. Klicka "Create repository"
) else (
    echo ⚠️  Okänd status: %http_status%
)

echo.
pause

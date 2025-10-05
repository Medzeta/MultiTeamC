@echo off
title GitHub Credentials Setup
echo ============================================
echo  GitHub Credentials Setup för MultiTeam
echo  Hjälper dig konfigurera GitHub access
echo ============================================

echo.
echo Välj autentiseringsmetod:
echo.
echo 1. Personal Access Token (Rekommenderat)
echo 2. Kontrollera nuvarande inställningar
echo 3. Testa GitHub koppling
echo 4. Avsluta
echo.
set /p choice="Välj (1-4): "

if "%choice%"=="1" goto :setup_token
if "%choice%"=="2" goto :check_current
if "%choice%"=="3" goto :test_connection
if "%choice%"=="4" goto :end
echo Ogiltigt val
pause
goto :end

:setup_token
echo.
echo ============================================
echo  Personal Access Token Setup
echo ============================================
echo.
echo STEG 1: Skapa token på GitHub
echo 1. Öppna: https://github.com/settings/tokens
echo 2. Klicka "Generate new token" → "Generate new token (classic)"
echo 3. Token name: MultiTeam-Deploy
echo 4. Expiration: No expiration (eller välj längre tid)
echo 5. Scopes: Kryssa i "repo" (ger full repository access)
echo 6. Klicka "Generate token"
echo 7. KOPIERA TOKEN (visas bara en gång!)
echo.
pause
echo.
echo STEG 2: Konfigurera Git med token
echo.
set /p token="Klistra in ditt GitHub token här: "
if "%token%"=="" (
    echo Ingen token angiven
    pause
    goto :end
)

echo.
echo Konfigurerar Git med token...
git config --global user.name "Medzeta"
git config --global user.email "medzetadesign@gmail.com"

echo Sätter remote URL med token...
git remote set-url origin https://Medzeta:%token%@github.com/Medzeta/Multi-Team-C.git

echo.
echo ✅ GitHub credentials konfigurerade!
echo.
echo Testar push...
git push origin main --dry-run
if %ERRORLEVEL% EQU 0 (
    echo ✅ Push test lyckades! Du kan nu pusha till GitHub.
) else (
    echo ❌ Push test misslyckades. Kontrollera token.
)
pause
goto :end

:check_current
echo.
echo ============================================
echo  Nuvarande Git Konfiguration
echo ============================================
echo.
echo Git user:
git config --global user.name
echo.
echo Git email:
git config --global user.email
echo.
echo Remote URLs:
git remote -v
echo.
echo Repository status:
git status --porcelain
echo.
pause
goto :end

:test_connection
echo.
echo ============================================
echo  Testar GitHub Koppling
echo ============================================
echo.
echo Testar repository access...
git ls-remote origin
if %ERRORLEVEL% EQU 0 (
    echo ✅ GitHub koppling fungerar!
) else (
    echo ❌ GitHub koppling misslyckades
    echo Kör setup_token för att konfigurera credentials
)
echo.
pause
goto :end

:end
echo.
echo ============================================
echo  GitHub Credentials Setup Komplett
echo ============================================
echo.
echo Efter att du har konfigurerat credentials kan du köra:
echo .\force_push_github.bat
echo.
pause

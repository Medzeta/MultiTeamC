@echo off
title MultiTeam GitHub Push Debug V0.20
color 0A
echo ============================================
echo  MultiTeam GitHub Push DEBUG V0.20
echo  Detaljerad Debug Information
echo ============================================

REM Set variables
set VERSION=0.20
set REPO_URL=https://github.com/Medzeta/Multi-Team-C
set BRANCH=main
set GIT_USER=Medzeta
set GIT_EMAIL=medzetadesign@gmail.com

echo.
echo DEBUG: Startar GitHub push process...
echo DEBUG: Current directory: %CD%
echo DEBUG: Date/Time: %DATE% %TIME%
echo DEBUG: User: %USERNAME%
echo.

echo ============================================
echo  STEG 1: Git Version Check
echo ============================================
echo DEBUG: Kontrollerar Git installation...
git --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git inte installerat eller inte i PATH
    echo Installera Git från: https://git-scm.com/
    pause
    exit /b 1
)
echo DEBUG: Git version OK

echo.
echo ============================================
echo  STEG 2: Git Configuration
echo ============================================
echo DEBUG: Konfigurerar Git med användaruppgifter...
echo DEBUG: User: %GIT_USER%
echo DEBUG: Email: %GIT_EMAIL%

git config --global user.name "%GIT_USER%"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Kunde inte sätta Git user.name
    pause
    exit /b 1
)

git config --global user.email "%GIT_EMAIL%"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Kunde inte sätta Git user.email
    pause
    exit /b 1
)

git config --global init.defaultBranch main
echo DEBUG: Git konfiguration komplett

echo.
echo ============================================
echo  STEG 3: Repository Status
echo ============================================
echo DEBUG: Kontrollerar repository status...

if not exist ".git" (
    echo DEBUG: .git mapp finns inte, initialiserar repository...
    git init
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Git init misslyckades
        pause
        exit /b 1
    )
    echo DEBUG: Repository initialiserat
) else (
    echo DEBUG: Git repository finns redan
)

echo DEBUG: Kontrollerar remote...
git remote -v
if %ERRORLEVEL% NEQ 0 (
    echo DEBUG: Inga remotes finns
)

echo DEBUG: Lägger till/uppdaterar remote origin...
git remote remove origin 2>nul
git remote add origin %REPO_URL%
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Kunde inte lägga till remote origin
    pause
    exit /b 1
)
echo DEBUG: Remote origin tillagd: %REPO_URL%

echo.
echo ============================================
echo  STEG 4: Working Directory Status
echo ============================================
echo DEBUG: Kontrollerar working directory...
git status
echo DEBUG: Working directory status visad ovan

echo.
echo ============================================
echo  STEG 5: Adding Files
echo ============================================
echo DEBUG: Lägger till alla filer...
git add .
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git add misslyckades
    pause
    exit /b 1
)
echo DEBUG: Alla filer tillagda

echo DEBUG: Status efter add:
git status --short

echo.
echo ============================================
echo  STEG 6: Creating Commit
echo ============================================
set commit_message=MultiTeam v%VERSION% - Complete PyQt6 application with working EXE and dashboard assets - Debug push
echo DEBUG: Commit message: %commit_message%

git commit -m "%commit_message%"
if %ERRORLEVEL% NEQ 0 (
    echo DEBUG: Inget att committa eller commit misslyckades
    echo DEBUG: Detta kan vara normalt om inga ändringar finns
) else (
    echo DEBUG: Commit skapat framgångsrikt
)

echo.
echo ============================================
echo  STEG 7: Branch Setup
echo ============================================
echo DEBUG: Säkerställer main branch...
git branch -M main
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Kunde inte sätta main branch
    pause
    exit /b 1
)
echo DEBUG: Main branch satt

echo DEBUG: Aktuella branches:
git branch -a

echo.
echo ============================================
echo  STEG 8: Remote Fetch
echo ============================================
echo DEBUG: Försöker hämta remote data...
git fetch origin main
if %ERRORLEVEL% NEQ 0 (
    echo DEBUG: Fetch misslyckades (kan vara normalt för första push)
) else (
    echo DEBUG: Remote data hämtad
)

echo.
echo ============================================
echo  STEG 9: Push Attempt 1 - Normal
echo ============================================
echo DEBUG: Försöker normal push...
git push -u origin main
if %ERRORLEVEL% EQU 0 (
    echo DEBUG: Normal push lyckades!
    goto :success
) else (
    echo DEBUG: Normal push misslyckades, försöker force push...
)

echo.
echo ============================================
echo  STEG 10: Push Attempt 2 - Force
echo ============================================
echo DEBUG: Försöker force push...
git push -f origin main
if %ERRORLEVEL% EQU 0 (
    echo DEBUG: Force push lyckades!
    goto :success
) else (
    echo DEBUG: Force push misslyckades också
)

echo.
echo ============================================
echo  STEG 11: Push Attempt 3 - Alternative
echo ============================================
echo DEBUG: Försöker alternativ push metod...
git push --set-upstream origin main --force
if %ERRORLEVEL% EQU 0 (
    echo DEBUG: Alternativ push lyckades!
    goto :success
) else (
    echo ERROR: Alla push-försök misslyckades
    goto :error
)

:success
echo.
echo ============================================
echo  🎉 SUCCESS - PUSH LYCKADES!
echo ============================================
echo DEBUG: Verifierar slutresultat...
echo.
echo Remote status:
git remote -v
echo.
echo Branch status:
git branch -a
echo.
echo Senaste commits:
git log --oneline -5
echo.
echo ============================================
echo  GitHub Repository: %REPO_URL%
echo  Branch: main
echo  Status: ✅ PUSH KOMPLETT
echo ============================================
goto :end

:error
echo.
echo ============================================
echo  ❌ ERROR - PUSH MISSLYCKADES
echo ============================================
echo DEBUG: Felsökningsinformation:
echo.
echo Git config:
git config --list | findstr user
echo.
echo Remote config:
git remote -v
echo.
echo Branch info:
git branch -a
echo.
echo Möjliga orsaker:
echo 1. GitHub credentials saknas eller felaktiga
echo 2. Repository finns inte på GitHub
echo 3. Ingen internetanslutning
echo 4. GitHub access token krävs
echo.
echo Lösningar:
echo 1. Kontrollera GitHub credentials
echo 2. Skapa Personal Access Token på GitHub
echo 3. Kontrollera internetanslutning
echo 4. Verifiera repository URL: %REPO_URL%

:end
echo.
echo ============================================
echo Debug session komplett
echo ============================================
echo Tryck valfri tangent för att stänga...
pause >nul

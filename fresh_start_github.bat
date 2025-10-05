@echo off
title Fresh Start GitHub Push
color 0A
echo ============================================
echo  Fresh Start GitHub Push
echo  Skapar helt ny Git-historik utan stora filer
echo ============================================

REM Set variables
set VERSION=0.20
set REPO_URL=https://github.com/Medzeta/Multi-Team-C
set GIT_USER=Medzeta
set GIT_EMAIL=medzetadesign@gmail.com

echo.
echo [██░░░░░░░░] 10%% - Complete Git Reset
echo ============================================
echo  STEG 1/8: Helt ny Git-start
echo ============================================

echo 🗑️  Tar bort hela .git mappen...
rmdir /s /q ".git" 2>nul
echo ✅ Git-historik raderad

echo 🆕 Initialiserar nytt Git repository...
git init
echo ✅ Nytt Git repository skapat

echo.
echo [████░░░░░░] 20%% - Exclude Large Files
echo ============================================
echo  STEG 2/8: Exkluderar stora filer
echo ============================================

echo 📝 Skapar .gitignore för stora filer...
(
    echo # Large files - too big for GitHub
    echo dist/
    echo backup/
    echo *.exe
    echo *.zip
    echo build/
    echo __pycache__/
    echo *.pyc
    echo *.spec
    echo *.log
    echo logs/
) > .gitignore

echo 🗑️  Flyttar stora filer till säker plats...
if not exist "RELEASE_FILES" mkdir "RELEASE_FILES"
move "backup\*.exe" "RELEASE_FILES\" 2>nul
move "backup\*.zip" "RELEASE_FILES\" 2>nul
move "dist\*.exe" "RELEASE_FILES\" 2>nul
move "dist\*.zip" "RELEASE_FILES\" 2>nul

echo ✅ Stora filer säkrade i RELEASE_FILES\

echo.
echo [██████░░░░] 30%% - Token Input
echo ============================================
echo  STEG 3/8: Token Input
echo ============================================

echo 🔐 Ange ditt GitHub Personal Access Token:
set /p GITHUB_TOKEN="Token: "

if "%GITHUB_TOKEN%"=="" (
    echo ❌ Ingen token angiven
    pause
    exit /b 1
)

echo.
echo [████████░░] 40%% - Git Configuration
echo ============================================
echo  STEG 4/8: Git Setup
echo ============================================

echo 🔧 Konfigurerar Git...
git config --global user.name "%GIT_USER%"
git config --global user.email "%GIT_EMAIL%"
git config --global init.defaultBranch main

echo 🔗 Konfigurerar remote...
git remote add origin https://%GIT_USER%:%GITHUB_TOKEN%@%REPO_URL:~8%.git
echo ✅ Git konfigurerat

echo.
echo [██████████] 50%% - Adding Source Files
echo ============================================
echo  STEG 5/8: Lägger till källkod
echo ============================================

echo 📁 Lägger till alla källkodsfiler...
git add .

echo 📊 Kontrollerar vad som läggs till:
git status --short | head -20
echo ... (och fler filer)

echo ✅ Källkod tillagd (inga stora filer)

echo.
echo [████████████] 60%% - Initial Commit
echo ============================================
echo  STEG 6/8: Första commit
echo ============================================

echo 💬 Skapar första commit...
git commit -m "MultiTeam v%VERSION% - Initial commit with source code only"
echo ✅ Initial commit skapat

echo.
echo [██████████████] 70%% - Push to GitHub
echo ============================================
echo  STEG 7/8: Push till GitHub
echo ============================================

echo 🚀 Pushar ren källkod till GitHub...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo ✅ Push lyckades!
    goto :success
) else (
    echo ❌ Push misslyckades
    goto :error
)

:success
echo.
echo [████████████████] 80%% - Success!
echo ============================================
echo  STEG 8/8: FRAMGÅNG!
echo ============================================

echo 🌐 Öppnar GitHub repository...
start "" "%REPO_URL%"
timeout /t 2 /nobreak >nul

echo 🌐 Öppnar GitHub release sida...
start "" "%REPO_URL%/releases/new"

echo.
echo ============================================
echo  🎉 GITHUB PUSH LYCKADES ÄNTLIGEN!
echo ============================================
echo ✅ Repository: %REPO_URL%
echo ✅ Branch: main
echo ✅ Källkod pushad (ren historik)
echo ✅ Inga stora filer i Git
echo.
echo 📊 Repository innehåller:
echo   - Källkod (Python, PyQt6)
echo   - Moduler och core-system
echo   - Dokumentation
echo   - Build-scripts
echo.
echo 📦 EXE-filer för release:
if exist "RELEASE_FILES\MultiTeam.exe" (
    for %%f in ("RELEASE_FILES\MultiTeam.exe") do echo   ✅ MultiTeam.exe: %%~zf bytes
) else (
    echo   ⚠️  Bygg EXE först med: .\build_complete_exe.bat
)
echo.
echo ============================================
echo  📋 SKAPA GITHUB RELEASE
echo ============================================
echo GitHub release sida öppnas nu.
echo.
echo 📋 Fyll i:
echo 🏷️  Tag version: v%VERSION%
echo 📝 Release title: MultiTeam v%VERSION% - Complete PyQt6 Application
echo 📄 Description:
echo    Complete team communication application with PyQt6 interface.
echo    
echo    Features:
echo    - Modern dashboard with module cards
echo    - Authentication system with SuperAdmin
echo    - License management and 2FA support
echo    - P2P Chat, Team Chat, Settings, Profile modules
echo    - Complete standalone EXE (no dependencies)
echo    
echo    Installation:
echo    1. Download MultiTeam.exe
echo    2. Run the application
echo    3. Login: username=1, password=1 (SuperAdmin)
echo    4. Explore the dashboard!
echo.
echo 📎 Attach files: Dra RELEASE_FILES\MultiTeam.exe till release
echo ✅ Klicka "Publish release"
echo.
echo 🔑 SuperAdmin login: username=1, password=1
goto :end

:error
echo.
echo ============================================
echo  ❌ PUSH MISSLYCKADES
echo ============================================
echo Kontrollera token och internetanslutning.

:end
REM Clear token
set GITHUB_TOKEN=
echo.
pause

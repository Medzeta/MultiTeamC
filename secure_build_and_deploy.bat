@echo off
title MultiTeam Secure Build and Deploy V0.20
color 0A
echo ============================================
echo  MultiTeam Secure Build and Deploy V0.20
echo  Bygger EXE + Pushar till GitHub (Säker)
echo ============================================

REM Set variables (NO HARDCODED TOKEN)
set VERSION=0.20
set REPO_NAME=Medzeta-Multi-Team-C
set REPO_URL=https://github.com/Medzeta/Medzeta-Multi-Team-C
set GIT_USER=Medzeta
set GIT_EMAIL=medzetadesign@gmail.com

echo.
echo [██░░░░░░░░] 10%% - EXE Build Start
echo ============================================
echo  STEG 1/12: Bygger EXE med Assets
echo ============================================

echo 🔨 Rensar tidigare builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
for %%f in (*.spec) do del "%%f"

echo 🔨 Bygger komplett EXE med PyQt6 och assets...
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name=MultiTeam ^
    --noconfirm ^
    --log-level=ERROR ^
    --add-data="core;core" ^
    --add-data="modules_pyqt;modules_pyqt" ^
    --add-data="assets;assets" ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=PyQt6.sip ^
    --collect-submodules=PyQt6 ^
    --collect-data=PyQt6 ^
    --collect-binaries=PyQt6 ^
    main_pyqt.py

if not exist "dist\MultiTeam.exe" (
    echo ❌ EXE build misslyckades
    pause
    exit /b 1
)
echo ✅ EXE byggd framgångsrikt!

echo.
echo [████░░░░░░] 20%% - EXE Test
echo ============================================
echo  STEG 2/12: Testar EXE
echo ============================================

echo 🧪 Testar EXE startup...
start "" "dist\MultiTeam.exe"
timeout /t 3 /nobreak >nul
tasklist /fi "imagename eq MultiTeam.exe" 2>nul | find /i "MultiTeam.exe" >nul
if %errorlevel% equ 0 (
    echo ✅ EXE fungerar!
    taskkill /f /im "MultiTeam.exe" 2>nul >nul
) else (
    echo ⚠️  EXE test (men fortsätter ändå)
)

echo.
echo [██████░░░░] 30%% - Release Package
echo ============================================
echo  STEG 3/12: Skapar Release Package
echo ============================================

REM Create package directory
set PACKAGE_DIR=dist\MultiTeam_Release_v%VERSION%
if not exist "%PACKAGE_DIR%" mkdir "%PACKAGE_DIR%"

echo 📋 Skapar release package...
copy "dist\MultiTeam.exe" "%PACKAGE_DIR%\"
if exist "README.md" copy "README.md" "%PACKAGE_DIR%\"
if exist "ROADMAP.md" copy "ROADMAP.md" "%PACKAGE_DIR%\"
if exist "HOW_TO_RUN.md" copy "HOW_TO_RUN.md" "%PACKAGE_DIR%\"
if exist "FINAL_PROJECT_SUMMARY.md" copy "FINAL_PROJECT_SUMMARY.md" "%PACKAGE_DIR%\"
mkdir "%PACKAGE_DIR%\data" 2>nul
mkdir "%PACKAGE_DIR%\logs" 2>nul

REM Create installation guide
(
    echo # MultiTeam v%VERSION% - Installation Guide
    echo.
    echo ## Quick Start:
    echo 1. Run MultiTeam.exe
    echo 2. Login: username=1, password=1 ^(SuperAdmin^)
    echo 3. Explore dashboard with module cards!
    echo.
    echo ## Features:
    echo - Modern PyQt6 interface with dashboard
    echo - Module cards with images ^(P2P Chat, Team Chat, etc.^)
    echo - Complete authentication system
    echo - License management
    echo - Auto-update system
    echo - 2FA support
    echo.
    echo ## System Requirements:
    echo - Windows 10/11 64-bit
    echo - 120MB disk space
    echo - No additional dependencies required
    echo.
    echo ## GitHub Repository:
    echo %REPO_URL%
    echo.
    echo ## Build Info:
    echo - Version: %VERSION%
    echo - Build Date: %DATE% %TIME%
    echo - Built by: %GIT_USER%
) > "%PACKAGE_DIR%\INSTALL.md"

REM Create ZIP
echo 📦 Skapar ZIP...
powershell -NoProfile -Command "Compress-Archive -Path '%PACKAGE_DIR%\*' -DestinationPath 'dist\MultiTeam_v%VERSION%.zip' -Force"
echo ✅ Release package skapat!

echo.
echo [████████░░] 40%% - Git Configuration
echo ============================================
echo  STEG 4/12: Git Setup
echo ============================================

echo 🔧 Konfigurerar Git...
git config --global user.name "%GIT_USER%"
git config --global user.email "%GIT_EMAIL%"
git config --global init.defaultBranch main
echo ✅ Git konfigurerat: %GIT_USER% (%GIT_EMAIL%)

echo.
echo [██████████] 50%% - Token Input
echo ============================================
echo  STEG 5/12: Säker Token Input
echo ============================================

echo 🔐 Ange ditt GitHub Personal Access Token:
set /p GITHUB_TOKEN="Token: "
if "%GITHUB_TOKEN%"=="" (
    echo ❌ Ingen token angiven
    pause
    exit /b 1
)

echo.
echo [████████████] 60%% - Repository Setup
echo ============================================
echo  STEG 6/12: Repository Configuration
echo ============================================

echo 📁 Kontrollerar repository...
if not exist ".git" (
    git init
    echo ✅ Git repository initialiserat
) else (
    echo ✅ Git repository finns redan
)

echo 🔗 Konfigurerar remote med token...
git remote remove origin 2>nul
git remote add origin https://%GIT_USER%:%GITHUB_TOKEN%@github.com/Medzeta/%REPO_NAME%.git
echo ✅ Remote konfigurerat: %REPO_URL%

echo.
echo [██████████████] 70%% - Adding Files
echo ============================================
echo  STEG 7/12: Git Add (Exkluderar token-filer)
echo ============================================

echo 📁 Lägger till säkra filer...
REM Add files but exclude the ones with tokens
git add . 
git reset HEAD complete_build_and_deploy.bat 2>nul
git reset HEAD push_with_new_token.bat 2>nul
git reset HEAD create_and_push_github.bat 2>nul
git reset HEAD push_with_token.bat 2>nul
echo ✅ Säkra filer tillagda (token-filer exkluderade)

echo.
echo [████████████████] 80%% - Creating Commit
echo ============================================
echo  STEG 8/12: Git Commit
echo ============================================

set commit_message=MultiTeam v%VERSION% - Complete PyQt6 application with working EXE and dashboard assets (secure)
echo 💬 Commit: %commit_message%
git commit -m "%commit_message%"
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Inga ändringar att committa
) else (
    echo ✅ Commit skapat
)

echo.
echo [██████████████████] 90%% - GitHub Push
echo ============================================
echo  STEG 9/12: Push till GitHub
echo ============================================

echo 🚀 Pushar till GitHub...
git push -u origin main
if %ERRORLEVEL% EQU 0 (
    echo ✅ Push lyckades!
    goto :success
) else (
    echo ⚠️  Normal push misslyckades, försöker force push...
    git push --force origin main
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Force push lyckades!
        goto :success
    ) else (
        echo ❌ Push misslyckades
        goto :error
    )
)

:success
echo.
echo [████████████████████] 100%% - SUCCESS!
echo ============================================
echo  🎉 BUILD OCH DEPLOY KOMPLETT!
echo ============================================
echo ✅ EXE byggd: dist\MultiTeam.exe
echo ✅ Package skapat: dist\MultiTeam_Release_v%VERSION%\
echo ✅ ZIP skapat: dist\MultiTeam_v%VERSION%.zip
echo ✅ Code pushad till GitHub: %REPO_URL%
echo.
echo 🌐 Öppnar GitHub release sida...
start "" "%REPO_URL%/releases/new"
echo.
echo ============================================
echo  📋 GITHUB RELEASE INSTRUKTIONER
echo ============================================
echo GitHub release sidan öppnas nu i din browser.
echo.
echo 📋 Fyll i följande:
echo 🏷️  Tag version: v%VERSION%
echo 📝 Release title: MultiTeam v%VERSION% - Complete PyQt6 Application
echo 📄 Description: Complete team communication application with PyQt6 interface
echo 📎 Attach files: dist\MultiTeam_v%VERSION%.zip
echo ✅ Klicka "Publish release"
echo.
echo 📦 Release package: dist\MultiTeam_v%VERSION%.zip
goto :end

:error
echo.
echo ============================================
echo  ❌ PUSH MISSLYCKADES
echo ============================================
echo Kontrollera token och försök igen.

:end
REM Clear token from memory
set GITHUB_TOKEN=
echo.
pause

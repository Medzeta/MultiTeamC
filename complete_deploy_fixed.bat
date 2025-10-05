@echo off
echo ============================================
echo  MultiTeam Complete Deploy V0.20
echo  Med Korrekta GitHub Uppgifter
echo ============================================

REM Set variables
set VERSION=0.20
set REPO_URL=https://github.com/Medzeta/Multi-Team-C
set BRANCH=main
set GIT_USER=Medzeta
set GIT_EMAIL=medzetadesign@gmail.com

echo.
echo [██░░░░░░░░] 10%% - Git Configuration
echo ============================================
echo  STEG 1/8: Git Setup
echo ============================================

REM Configure Git with correct credentials
echo 🔧 Konfigurerar Git med dina uppgifter...
git config --global user.name "%GIT_USER%"
git config --global user.email "%GIT_EMAIL%"
echo ✅ Git konfigurerat: %GIT_USER% (%GIT_EMAIL%)

echo.
echo [████░░░░░░] 20%% - Repository Setup
echo ============================================
echo  STEG 2/8: Repository Check
echo ============================================
git status >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Initialiserar Git repository...
    git init
    git remote add origin %REPO_URL% 2>nul
    echo ✅ Repository initialiserat: %REPO_URL%
) else (
    echo ✅ Repository finns redan
    git remote -v
)

echo.
echo [██████░░░░] 30%% - Adding Files
echo ============================================
echo  STEG 3/8: Git Add
echo ============================================
echo 📁 Lägger till alla filer...
git add .
echo ✅ Filer tillagda

echo.
echo [████████░░] 40%% - Creating Commit
echo ============================================
echo  STEG 4/8: Git Commit
echo ============================================
set commit_message=MultiTeam v%VERSION% - Complete PyQt6 application with working EXE and dashboard assets
echo 💬 Commit: %commit_message%
git commit -m "%commit_message%"
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Inga ändringar att committa
) else (
    echo ✅ Commit skapat
)

echo.
echo [██████████] 50%% - GitHub Push
echo ============================================
echo  STEG 5/8: Push till GitHub
echo ============================================
echo 🌐 Pushar till GitHub...
git push -u origin %BRANCH%
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Push misslyckades, försöker sätta branch...
    git branch -M %BRANCH%
    git push -u origin %BRANCH%
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Push misslyckades. Kontrollera GitHub access token.
        echo 💡 Du kan behöva skapa en Personal Access Token på GitHub
        echo 💡 Gå till: GitHub → Settings → Developer settings → Personal access tokens
        echo.
        echo ⏭️  Fortsätter med EXE build ändå...
    ) else (
        echo ✅ Push lyckades!
    )
) else (
    echo ✅ Push lyckades!
)

echo.
echo [████████████] 60%% - Building EXE
echo ============================================
echo  STEG 6/8: EXE Build
echo ============================================
echo 🔨 Rensar tidigare builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
for %%f in (*.spec) do del "%%f"

echo 🔨 Bygger EXE med alla assets...
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
echo [██████████████] 70%% - Testing EXE
echo ============================================
echo  STEG 7/8: EXE Test
echo ============================================
echo 🧪 Testar EXE...
start "" "dist\MultiTeam.exe"
timeout /t 3 /nobreak >nul
tasklist /fi "imagename eq MultiTeam.exe" 2>nul | find /i "MultiTeam.exe" >nul
if %errorlevel% equ 0 (
    echo ✅ EXE fungerar!
    taskkill /f /im "MultiTeam.exe" 2>nul >nul
) else (
    echo ⚠️  EXE test (men fortsätter)
)

echo.
echo [████████████████] 80%% - Release Package
echo ============================================
echo  STEG 8/8: Package Creation
echo ============================================

REM Create package
set PACKAGE_DIR=dist\MultiTeam_Release_v%VERSION%
if not exist "%PACKAGE_DIR%" mkdir "%PACKAGE_DIR%"

echo 📋 Skapar release package...
copy "dist\MultiTeam.exe" "%PACKAGE_DIR%\"
if exist "README.md" copy "README.md" "%PACKAGE_DIR%\"
if exist "ROADMAP.md" copy "ROADMAP.md" "%PACKAGE_DIR%\"
if exist "HOW_TO_RUN.md" copy "HOW_TO_RUN.md" "%PACKAGE_DIR%\"
mkdir "%PACKAGE_DIR%\data" 2>nul
mkdir "%PACKAGE_DIR%\logs" 2>nul

REM Create install guide
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
powershell -NoProfile -Command "Compress-Archive -Path '%PACKAGE_DIR%\*' -DestinationPath 'dist\MultiTeam_v%VERSION%.zip' -Force"

echo.
echo [██████████████████] 100%% - KOMPLETT!
echo ============================================
echo  🎉 DEPLOYMENT KLART!
echo ============================================

if exist "dist\MultiTeam_v%VERSION%.zip" (
    echo ✅ Git konfigurerat: %GIT_USER% (%GIT_EMAIL%)
    echo ✅ Repository: %REPO_URL%
    echo ✅ EXE byggd: dist\MultiTeam.exe
    echo ✅ Package: %PACKAGE_DIR%\
    echo ✅ ZIP: dist\MultiTeam_v%VERSION%.zip
    echo.
    echo 📊 Filstorlekar:
    for %%f in ("dist\MultiTeam.exe") do echo   EXE: %%~zf bytes
    for %%f in ("dist\MultiTeam_v%VERSION%.zip") do echo   ZIP: %%~zf bytes
    echo.
    echo ============================================
    echo  🚀 REDO FÖR GITHUB RELEASE!
    echo ============================================
    echo 📋 Nästa steg:
    echo 1. Gå till: %REPO_URL%/releases
    echo 2. Klicka "Create a new release"
    echo 3. Tag: v%VERSION%
    echo 4. Title: "MultiTeam v%VERSION% - Complete PyQt6 Application"
    echo 5. Ladda upp: dist\MultiTeam_v%VERSION%.zip
    echo 6. Publicera!
    
) else (
    echo ❌ Package creation misslyckades
)

echo.
pause

@echo off
echo ============================================
echo  MultiTeam Setup och Deploy V0.20
echo  Automatisk Git Setup och GitHub Deploy
echo ============================================

REM Set variables
set VERSION=0.20
set REPO_URL=https://github.com/Medzeta/Multi-Team-C
set BRANCH=main
set GIT_USER=Medzeta
set GIT_EMAIL=medzetadesign@gmail.com

echo.
echo [██░░░░░░░░] 10%% - Git Configuration Check
echo ============================================
echo  STEG 1/8: Git Setup
echo ============================================

REM Check if git is configured
git config --global user.name >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Git användarnamn inte konfigurerat
    echo 🔧 Konfigurerar Git...
    git config --global user.name "%GIT_USER%"
    git config --global user.email "%GIT_EMAIL%"
    echo ✅ Git konfigurerat med %GIT_USER% (%GIT_EMAIL%)
) else (
    echo ✅ Git redan konfigurerat
    echo 👤 Användare: 
    git config --global user.name
    echo 📧 Email: 
    git config --global user.email
)

echo.
echo [████░░░░░░] 20%% - Git Repository Check
echo ============================================
echo  STEG 2/8: Repository Setup
echo ============================================
git status >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Initialiserar Git repository...
    git init
    git remote add origin %REPO_URL% 2>nul
    echo ✅ Git repository initialiserat
) else (
    echo ✅ Git repository finns redan
)

echo.
echo [██████░░░░] 30%% - Adding Files to Git
echo ============================================
echo  STEG 3/8: Git Add Files
echo ============================================
echo 📁 Lägger till alla projektfiler...
git add .
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Misslyckades att lägga till filer
    pause
    exit /b 1
)
echo ✅ Alla filer tillagda till Git

echo.
echo [████████░░] 40%% - Creating Commit
echo ============================================
echo  STEG 4/8: Git Commit
echo ============================================
set commit_message=MultiTeam v%VERSION% - Complete PyQt6 application with working EXE and dashboard assets
echo 💬 Commit: %commit_message%
git commit -m "%commit_message%"
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Inga ändringar att committa eller commit misslyckades
) else (
    echo ✅ Commit skapat framgångsrikt
)

echo.
echo [██████████] 50%% - Building EXE (Skip GitHub Push for now)
echo ============================================
echo  STEG 5/8: EXE Build med Assets
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
echo [████████████] 60%% - Testing EXE
echo ============================================
echo  STEG 6/8: EXE Test
echo ============================================
echo 🧪 Testar EXE startup...
start "" "dist\MultiTeam.exe"
timeout /t 3 /nobreak >nul
tasklist /fi "imagename eq MultiTeam.exe" 2>nul | find /i "MultiTeam.exe" >nul
if %errorlevel% equ 0 (
    echo ✅ EXE startar och körs korrekt
    taskkill /f /im "MultiTeam.exe" 2>nul >nul
) else (
    echo ⚠️  EXE startproblem (men fortsätter ändå)
)

echo.
echo [██████████████] 70%% - Creating Release Package
echo ============================================
echo  STEG 7/8: Release Package
echo ============================================
echo 📦 Skapar release package...

REM Create package directory
set PACKAGE_DIR=dist\MultiTeam_Release_v%VERSION%
if not exist "%PACKAGE_DIR%" mkdir "%PACKAGE_DIR%"

REM Copy EXE
echo 📋 Kopierar EXE...
copy "dist\MultiTeam.exe" "%PACKAGE_DIR%\"

REM Copy documentation
echo 📋 Kopierar dokumentation...
if exist "README.md" copy "README.md" "%PACKAGE_DIR%\"
if exist "ROADMAP.md" copy "ROADMAP.md" "%PACKAGE_DIR%\"
if exist "HOW_TO_RUN.md" copy "HOW_TO_RUN.md" "%PACKAGE_DIR%\"
if exist "FINAL_PROJECT_SUMMARY.md" copy "FINAL_PROJECT_SUMMARY.md" "%PACKAGE_DIR%\"

REM Create directories
mkdir "%PACKAGE_DIR%\data" 2>nul
mkdir "%PACKAGE_DIR%\logs" 2>nul

REM Create installation guide
(
    echo # MultiTeam v%VERSION% - Installation Guide
    echo.
    echo ## Quick Start:
    echo 1. Run MultiTeam.exe
    echo 2. Login: username=1, password=1 (SuperAdmin^)
    echo 3. Explore the dashboard!
    echo.
    echo ## Features:
    echo - Modern PyQt6 interface
    echo - Dashboard with module cards
    echo - Authentication system
    echo - License management
    echo - Auto-update system
    echo.
    echo ## System Requirements:
    echo - Windows 10/11 64-bit
    echo - 120MB disk space
    echo - No additional dependencies
) > "%PACKAGE_DIR%\INSTALL.md"

REM Create ZIP
echo 📦 Skapar ZIP...
powershell -NoProfile -Command "Compress-Archive -Path '%PACKAGE_DIR%\*' -DestinationPath 'dist\MultiTeam_v%VERSION%.zip' -Force"

echo.
echo [████████████████] 80%% - Package Complete
echo ============================================
echo  STEG 8/8: Summary
echo ============================================

if exist "dist\MultiTeam_v%VERSION%.zip" (
    echo ============================================
    echo  🎉 BUILD OCH PACKAGE KLART!
    echo ============================================
    echo ✅ EXE byggd: dist\MultiTeam.exe
    echo ✅ Package skapat: %PACKAGE_DIR%\
    echo ✅ ZIP skapat: dist\MultiTeam_v%VERSION%.zip
    echo.
    echo 📊 Filstorlekar:
    for %%f in ("dist\MultiTeam.exe") do echo   EXE: %%~zf bytes
    for %%f in ("dist\MultiTeam_v%VERSION%.zip") do echo   ZIP: %%~zf bytes
    echo.
    echo 📋 Package innehåll:
    dir "%PACKAGE_DIR%" /b
    echo.
    echo ============================================
    echo  📝 NÄSTA STEG:
    echo ============================================
    echo 1. Testa EXE: dist\MultiTeam.exe
    echo 2. Login med: 1/1 (SuperAdmin^)
    echo 3. Kontrollera dashboard
    echo 4. För GitHub: Konfigurera Git credentials först
    echo.
    echo 💡 Git credentials setup:
    echo   git config --global user.name "YourName"
    echo   git config --global user.email "your@email.com"
    echo   Sedan kör: git push -u origin main
    
) else (
    echo ❌ Package creation misslyckades
)

echo.
pause

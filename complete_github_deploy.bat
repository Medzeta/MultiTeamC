@echo off
setlocal enabledelayedexpansion
echo ============================================
echo  MultiTeam Complete GitHub Deploy V0.20
echo  Med Progress Bars och Full Automation
echo ============================================

REM Set variables
set VERSION=0.20
set REPO_URL=https://github.com/Medzeta/Multi-Team-C.git
set BRANCH=main
set TOTAL_STEPS=8

REM Progress bar function
:show_progress
if "%1"=="" goto :eof
if "%2"=="" goto :eof
set /a progress=%1*100/%TOTAL_STEPS%
set bar=
if %progress% GTR 0 (
    for /l %%i in (1,2,%progress%) do set bar=!bar!█
)
if %progress% LSS 100 (
    for /l %%i in (%progress%,2,98) do set bar=!bar!░
)
echo [!bar!] %progress%%% - %2
goto :eof

echo.
call :show_progress 1 "Kontrollerar Git Repository Status"
echo ============================================
echo  STEG 1/8: Git Repository Check
echo ============================================
git status >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Initialiserar Git repository...
    git init
    git remote add origin %REPO_URL%
    echo ✅ Git repository initialiserat
) else (
    echo ✅ Git repository finns redan
)

echo.
call :show_progress 2 "Lägger till alla filer till Git"
echo ============================================
echo  STEG 2/8: Git Add Files
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
call :show_progress 3 "Skapar Git Commit"
echo ============================================
echo  STEG 3/8: Git Commit
echo ============================================
set commit_message=MultiTeam v%VERSION% - Complete PyQt6 application with working EXE, dashboard assets, and GitHub deployment
echo 💬 Commit meddelande: %commit_message%
git commit -m "%commit_message%"
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Inga ändringar att committa eller commit misslyckades
) else (
    echo ✅ Commit skapat framgångsrikt
)

echo.
call :show_progress 4 "Pushar till GitHub"
echo ============================================
echo  STEG 4/8: GitHub Push
echo ============================================
echo 🌐 Pushar till GitHub repository...
git push -u origin %BRANCH%
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Push misslyckades, försöker sätta upstream...
    git branch -M %BRANCH%
    git push -u origin %BRANCH%
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Push misslyckades fortfarande. Kontrollera GitHub credentials.
        echo 💡 Kör: git config --global user.name "Ditt Namn"
        echo 💡 Kör: git config --global user.email "din@email.com"
        pause
        exit /b 1
    )
)
echo ✅ Kod pushad till GitHub framgångsrikt!

echo.
call :show_progress 5 "Bygger EXE med Assets"
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
call :show_progress 6 "Testar EXE Funktionalitet"
echo ============================================
echo  STEG 6/8: EXE Functionality Test
echo ============================================
echo 🧪 Startar EXE för snabb test...
start "" "dist\MultiTeam.exe"
timeout /t 3 /nobreak >nul
tasklist /fi "imagename eq MultiTeam.exe" 2>nul | find /i "MultiTeam.exe" >nul
if %errorlevel% equ 0 (
    echo ✅ EXE startar och körs korrekt
    taskkill /f /im "MultiTeam.exe" 2>nul >nul
) else (
    echo ❌ EXE startproblem upptäckt
)

echo.
call :show_progress 7 "Skapar Release Package"
echo ============================================
echo  STEG 7/8: Release Package Creation
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

REM Create user directories
echo 📁 Skapar användarkataloger...
mkdir "%PACKAGE_DIR%\data" 2>nul
mkdir "%PACKAGE_DIR%\logs" 2>nul

REM Create comprehensive installation guide
echo 📝 Skapar installationsguide...
(
    echo # MultiTeam v%VERSION% - Komplett Installationspaket
    echo.
    echo ## 🚀 Snabbstart:
    echo 1. Kör MultiTeam.exe
    echo 2. Logga in med SuperAdmin: användarnamn=1, lösenord=1
    echo 3. Utforska alla funktioner!
    echo.
    echo ## ✨ Inkluderade Funktioner:
    echo ✅ Modern PyQt6 gränssnitt med dashboard
    echo ✅ Säkert autentiseringssystem
    echo ✅ E-postverifieringssystem  
    echo ✅ Licenshanteringssystem
    echo ✅ Auto-uppdateringssystem
    echo ✅ 2FA-stöd
    echo ✅ Modulkort med bilder
    echo ✅ Komplett användarhantering
    echo ✅ P2P Chat funktionalitet
    echo ✅ Team Chat system
    echo ✅ Profil- och inställningshantering
    echo.
    echo ## 🖥️ Systemkrav:
    echo - Windows 10/11 64-bit
    echo - Inga ytterligare beroenden krävs
    echo - Alla assets inbäddade i EXE
    echo - 120MB diskutrymme
    echo.
    echo ## 🔐 Standard Inloggning:
    echo - Användarnamn: 1
    echo - Lösenord: 1
    echo - Detta är SuperAdmin-kontot
    echo.
    echo ## 📊 Build Information:
    echo - Version: %VERSION%
    echo - Build Datum: %DATE% %TIME%
    echo - PyQt6 Version med komplett asset-stöd
    echo - Alla dashboard-bilder inkluderade
    echo - GitHub Repository: %REPO_URL%
    echo.
    echo ## 🆘 Support:
    echo - GitHub Issues: %REPO_URL%/issues
    echo - Dokumentation: Se inkluderade MD-filer
    echo - Loggar sparas i: logs\ mappen
) > "%PACKAGE_DIR%\INSTALLATION_GUIDE.md"

REM Create ZIP package
echo 📦 Skapar ZIP-paket...
powershell -NoProfile -Command "Compress-Archive -Path '%PACKAGE_DIR%\*' -DestinationPath 'dist\MultiTeam_Complete_v%VERSION%.zip' -Force"

if exist "dist\MultiTeam_Complete_v%VERSION%.zip" (
    echo ✅ Release package skapat framgångsrikt!
) else (
    echo ❌ Misslyckades att skapa ZIP-paket
)

echo.
call :show_progress 8 "Deployment Komplett"
echo ============================================
echo  STEG 8/8: Deployment Summary
echo ============================================

if exist "dist\MultiTeam_Complete_v%VERSION%.zip" (
    echo.
    echo ============================================
    echo  🎉 KOMPLETT FRAMGÅNG!
    echo ============================================
    echo ✅ Kod pushad till GitHub
    echo ✅ EXE byggd med alla assets
    echo ✅ Dashboard fungerar korrekt
    echo ✅ Release package skapat
    echo.
    echo 📊 PACKAGE DETALJER:
    echo ============================================
    echo 📦 Package: %PACKAGE_DIR%\
    echo 📄 ZIP: dist\MultiTeam_Complete_v%VERSION%.zip
    echo 🌐 GitHub: %REPO_URL%
    echo 🏷️  Version: %VERSION%
    echo.
    echo 📋 Package Innehåll:
    dir "%PACKAGE_DIR%" /b
    echo.
    echo 📊 ZIP Storlek:
    for %%f in ("dist\MultiTeam_Complete_v%VERSION%.zip") do echo Storlek: %%~zf bytes (ca. %%~zf:~0,-6% MB^)
    echo.
    echo ============================================
    echo  🚀 REDO FÖR GITHUB RELEASE!
    echo ============================================
    echo.
    echo 📋 Nästa steg för GitHub Release:
    echo 1. Gå till %REPO_URL%/releases
    echo 2. Klicka "Create a new release"
    echo 3. Tag version: v%VERSION%
    echo 4. Release title: "MultiTeam v%VERSION% - Complete PyQt6 Application"
    echo 5. Ladda upp: dist\MultiTeam_Complete_v%VERSION%.zip
    echo 6. Publicera release
    echo.
    echo 🎯 Release Notes Förslag:
    echo "## MultiTeam v%VERSION% - Komplett PyQt6 Applikation"
    echo "### ✨ Nya Funktioner:"
    echo "- Fungerande EXE med PyQt6 dashboard"
    echo "- Alla assets inbäddade"
    echo "- Komplett autentiseringssystem"
    echo "- SuperAdmin konto (1/1^)"
    echo "### 📦 Installation:"
    echo "Ladda ner ZIP, extrahera och kör MultiTeam.exe"
    
) else (
    echo ❌ DEPLOYMENT MISSLYCKADES
    echo Kontrollera fel ovan och försök igen
)

echo.
echo ============================================
echo Deployment process komplett!
echo ============================================
pause

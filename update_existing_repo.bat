@echo off
title Update Existing Repository - Direct Release
echo ============================================
echo  Update Existing Repository
echo  Direkt till befintlig repository
echo ============================================

set REPO_URL=https://github.com/Medzeta/Multi-Team-C
set VERSION=0.20

echo.
echo 🔍 Repository existerar redan: %REPO_URL%
echo.

echo 🗑️ Rensar token-filer för säker push...
del "auto_publish_with_debug.bat" 2>nul
del "debug_to_file.bat" 2>nul
del "final_working_github_push.bat" 2>nul
del "fixed_auto_publish.bat" 2>nul
del "quick_github_test.bat" 2>nul
del "simple_github_push.bat" 2>nul
del "clean_tokens_and_push.bat" 2>nul
echo ✅ Token-filer rensade

echo.
echo 🔧 Git setup...
git config --global user.name "Medzeta"
git config --global user.email "medzetadesign@gmail.com"

echo.
echo 📁 Lägger till uppdaterade filer...
git add .

echo.
echo 💬 Skapar commit för uppdatering...
git commit -m "MultiTeam v%VERSION% - Updated release with working EXE and clean code"

echo.
echo 🔐 Ange GitHub token för push:
set /p GITHUB_TOKEN="Token: "

echo.
echo 🔗 Konfigurerar remote...
git remote remove origin 2>nul
git remote add origin https://Medzeta:%GITHUB_TOKEN%@%REPO_URL:~8%.git

echo.
echo 🚀 Pushar uppdatering till befintlig repository...
git push --force origin main

if %ERRORLEVEL% EQU 0 (
    echo ✅ Push lyckades!
    goto :success
) else (
    echo ❌ Push misslyckades
    goto :error
)

:success
echo.
echo ============================================
echo  🎉 UPPDATERING LYCKADES!
echo ============================================
echo ✅ Repository uppdaterat: %REPO_URL%
echo ✅ EXE klar för release: RELEASE_FILES\MultiTeam.exe
echo ✅ ZIP package klar: RELEASE_FILES\MultiTeam_v%VERSION%.zip
echo.

echo 🌐 Öppnar befintlig repository...
start "" "%REPO_URL%"
timeout /t 2 /nobreak >nul

echo 🌐 Öppnar release sida för ny release...
start "" "%REPO_URL%/releases/new"
timeout /t 2 /nobreak >nul

echo 📁 Öppnar release files mapp...
start "" "RELEASE_FILES"

echo.
echo ============================================
echo  📋 SKAPA NY RELEASE:
echo ============================================
echo 1. Tag version: v%VERSION%
echo 2. Release title: MultiTeam v%VERSION% - Complete PyQt6 Application Update
echo 3. Description:
echo    🚀 Updated Features:
echo    - Working EXE with all assets embedded
echo    - Dashboard with 19 module cards
echo    - Complete authentication system
echo    - License management and 2FA support
echo    - Clean codebase without tokens
echo.
echo    📥 Installation:
echo    1. Download MultiTeam.exe
echo    2. Run the application
echo    3. Login: username=1, password=1 (SuperAdmin)
echo    4. Explore dashboard with module cards!
echo.
echo 4. Dra och släpp från RELEASE_FILES:
if exist "RELEASE_FILES\MultiTeam.exe" (
    for %%f in ("RELEASE_FILES\MultiTeam.exe") do echo    ✅ MultiTeam.exe (%%~zf bytes)
)
if exist "RELEASE_FILES\MultiTeam_v%VERSION%.zip" (
    for %%f in ("RELEASE_FILES\MultiTeam_v%VERSION%.zip") do echo    ✅ MultiTeam_v%VERSION%.zip (%%~zf bytes)
)
echo.
echo 5. Klicka "Publish release"
echo.
echo 🔑 Login credentials: username=1, password=1 (SuperAdmin)
goto :end

:error
echo.
echo ============================================
echo  ❌ UPPDATERING MISSLYCKADES
echo ============================================
echo Kontrollera token och försök igen.

:end
echo.
REM Clear token
set GITHUB_TOKEN=
pause

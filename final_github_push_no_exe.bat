@echo off
title Final GitHub Push - No Large Files
color 0A
echo ============================================
echo  Final GitHub Push - No Large Files
echo  Pushar kod utan stora EXE-filer
echo ============================================

REM Set variables
set VERSION=0.20
set REPO_URL=https://github.com/Medzeta/Multi-Team-C
set GIT_USER=Medzeta
set GIT_EMAIL=medzetadesign@gmail.com

echo.
echo [██░░░░░░░░] 10%% - Removing Large Files
echo ============================================
echo  STEG 1/8: Ta bort stora filer från Git
echo ============================================

echo 🗑️  Tar bort stora filer från Git tracking...
git rm --cached backup/MultiTeam.exe 2>nul
git rm --cached dist/MultiTeam.exe 2>nul
git rm --cached backup/MultiTeam_Complete_v0.20.zip 2>nul
git rm --cached dist/MultiTeam_Complete_v0.20.zip 2>nul
git rm --cached dist/MultiTeam_Final_v0.20/ -r 2>nul

echo 📝 Uppdaterar .gitignore...
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
) >> .gitignore

echo ✅ Stora filer exkluderade

echo.
echo [████░░░░░░] 20%% - Token Input
echo ============================================
echo  STEG 2/8: Token Input
echo ============================================

echo 🔐 Ange ditt GitHub Personal Access Token:
set /p GITHUB_TOKEN="Token: "

if "%GITHUB_TOKEN%"=="" (
    echo ❌ Ingen token angiven
    pause
    exit /b 1
)

echo.
echo [██████░░░░] 30%% - Git Configuration
echo ============================================
echo  STEG 3/8: Git Setup
echo ============================================

echo 🔧 Konfigurerar Git...
git config --global user.name "%GIT_USER%"
git config --global user.email "%GIT_EMAIL%"

echo 🔗 Konfigurerar remote...
git remote remove origin 2>nul
git remote add origin https://%GIT_USER%:%GITHUB_TOKEN%@%REPO_URL:~8%.git
echo ✅ Git konfigurerat

echo.
echo [████████░░] 40%% - Adding Clean Files
echo ============================================
echo  STEG 4/8: Lägger till rena filer
echo ============================================

echo 📁 Lägger till alla filer utom stora...
git add .
echo ✅ Rena filer tillagda

echo 📊 Kontrollerar vad som läggs till:
git status --short

echo.
echo [██████████] 50%% - Creating Commit
echo ============================================
echo  STEG 5/8: Skapar commit
echo ============================================

echo 💬 Skapar commit utan stora filer...
git commit -m "MultiTeam v%VERSION% - Source code only (EXE available as GitHub release)"
echo ✅ Commit skapat

echo.
echo [████████████] 60%% - Connection Test
echo ============================================
echo  STEG 6/8: Testar koppling
echo ============================================

echo 🔍 Testar GitHub koppling...
git ls-remote origin HEAD
if %ERRORLEVEL% EQU 0 (
    echo ✅ GitHub koppling fungerar!
) else (
    echo ❌ GitHub koppling misslyckades
    pause
    exit /b 1
)

echo.
echo [██████████████] 70%% - Push to GitHub
echo ============================================
echo  STEG 7/8: Push till GitHub
echo ============================================

echo 🚀 Pushar källkod till GitHub...
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
echo [████████████████] 80%% - Opening GitHub
echo ============================================
echo  STEG 8/8: Öppnar GitHub
echo ============================================

echo 🌐 Öppnar GitHub repository...
start "" "%REPO_URL%"
timeout /t 2 /nobreak >nul

echo 🌐 Öppnar GitHub release sida...
start "" "%REPO_URL%/releases/new"

echo.
echo ============================================
echo  🎉 GITHUB PUSH LYCKADES!
echo ============================================
echo ✅ Repository: %REPO_URL%
echo ✅ Branch: main
echo ✅ Källkod pushad (utan stora filer)
echo ✅ EXE finns lokalt för release
echo.
echo 📊 Senaste commit:
git log --oneline -1
echo.
echo ============================================
echo  📋 SKAPA GITHUB RELEASE MED EXE
echo ============================================
echo GitHub release sida öppnas nu.
echo.
echo 📋 Fyll i på release sidan:
echo 🏷️  Tag version: v%VERSION%
echo 📝 Release title: MultiTeam v%VERSION% - Complete PyQt6 Application
echo 📄 Description: 
echo    Complete team communication application with PyQt6 interface.
echo    Features: Dashboard with module cards, authentication system, 
echo    license management, 2FA support, and more.
echo.
echo 📎 Attach files (dra och släpp):
if exist "backup\MultiTeam.exe" (
    echo    ✅ backup\MultiTeam.exe (138MB)
) else if exist "dist\MultiTeam.exe" (
    echo    ✅ dist\MultiTeam.exe (138MB)
) else (
    echo    ⚠️  Bygg EXE först med: .\build_complete_exe.bat
)
echo.
echo 📋 Installation instructions för users:
echo    1. Download MultiTeam.exe from release
echo    2. Run MultiTeam.exe
echo    3. Login: username=1, password=1 (SuperAdmin)
echo    4. Explore dashboard with module cards!
echo.
echo ✅ Klicka "Publish release"
echo.
echo 🔑 Login credentials: username=1, password=1 (SuperAdmin)
goto :end

:error
echo.
echo ============================================
echo  ❌ PUSH MISSLYCKADES
echo ============================================
echo Kontrollera token och försök igen.

:end
REM Clear token
set GITHUB_TOKEN=
echo.
pause

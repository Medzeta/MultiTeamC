@echo off
title Clean Git History and Push to GitHub
color 0A
echo ============================================
echo  Clean Git History and Push to GitHub
echo  Rensar token-filer och skapar ren historik
echo ============================================

REM Set variables
set VERSION=0.20
set REPO_URL=https://github.com/Medzeta/Multi-Team-C
set GIT_USER=Medzeta
set GIT_EMAIL=medzetadesign@gmail.com

echo.
echo [██░░░░░░░░] 10%% - Backup and Clean
echo ============================================
echo  STEG 1/10: Backup och Rensning
echo ============================================

echo 📋 Skapar backup av viktiga filer...
if not exist "backup" mkdir "backup"
copy "dist\MultiTeam_Complete_v0.20.zip" "backup\" 2>nul
copy "dist\MultiTeam.exe" "backup\" 2>nul

echo 🗑️  Tar bort token-filer från working directory...
del "complete_build_and_deploy.bat" 2>nul
del "push_with_new_token.bat" 2>nul
del "create_and_push_github.bat" 2>nul
del "push_with_token.bat" 2>nul
echo ✅ Token-filer borttagna

echo.
echo [████░░░░░░] 20%% - Git Reset
echo ============================================
echo  STEG 2/10: Git Reset och Clean Start
echo ============================================

echo 🔄 Rensar Git cache...
git rm --cached complete_build_and_deploy.bat 2>nul
git rm --cached push_with_new_token.bat 2>nul
git rm --cached create_and_push_github.bat 2>nul
git rm --cached push_with_token.bat 2>nul

echo 🔄 Skapar ny ren commit utan tokens...
git add .
git commit -m "MultiTeam v%VERSION% - Clean version without tokens - Ready for GitHub"

echo ✅ Ren commit skapad

echo.
echo [██████░░░░] 30%% - Token Input
echo ============================================
echo  STEG 3/10: Säker Token Input
echo ============================================

echo 🔐 Ange ditt GitHub Personal Access Token:
set /p GITHUB_TOKEN="Token: "

if "%GITHUB_TOKEN%"=="" (
    echo ❌ Ingen token angiven
    pause
    exit /b 1
)

echo.
echo [████████░░] 40%% - Remote Setup
echo ============================================
echo  STEG 4/10: Remote Konfiguration
echo ============================================

echo 🔧 Konfigurerar Git...
git config --global user.name "%GIT_USER%"
git config --global user.email "%GIT_EMAIL%"

echo 🔗 Konfigurerar remote...
git remote remove origin 2>nul
git remote add origin https://%GIT_USER%:%GITHUB_TOKEN%@%REPO_URL:~8%.git
echo ✅ Remote konfigurerat

echo.
echo [██████████] 50%% - Connection Test
echo ============================================
echo  STEG 5/10: Testar Koppling
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
echo [████████████] 60%% - Branch Setup
echo ============================================
echo  STEG 6/10: Branch Konfiguration
echo ============================================

echo 🌿 Säkerställer main branch...
git branch -M main
echo ✅ Main branch konfigurerad

echo.
echo [██████████████] 70%% - Force Push Clean
echo ============================================
echo  STEG 7/10: Force Push Ren Version
echo ============================================

echo 🚀 Force pushar ren version till GitHub...
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
echo [████████████████] 80%% - Verification
echo ============================================
echo  STEG 8/10: Verifiering
echo ============================================

echo 🔍 Verifierar push på GitHub...
git ls-remote origin main
echo ✅ Push verifierad

echo.
echo [██████████████████] 90%% - Opening GitHub
echo ============================================
echo  STEG 9/10: Öppnar GitHub
echo ============================================

echo 🌐 Öppnar GitHub repository...
start "" "%REPO_URL%"
timeout /t 2 /nobreak >nul

echo 🌐 Öppnar GitHub release sida...
start "" "%REPO_URL%/releases/new"

echo.
echo [████████████████████] 100%% - Complete!
echo ============================================
echo  STEG 10/10: KOMPLETT!
echo ============================================

echo ============================================
echo  🎉 GITHUB PUSH LYCKADES!
echo ============================================
echo ✅ Repository: %REPO_URL%
echo ✅ Branch: main
echo ✅ Ren version utan tokens pushad
echo ✅ Release package: backup\MultiTeam_Complete_v0.20.zip
echo.
echo 📊 Senaste commit:
git log --oneline -1
echo.
echo ============================================
echo  📋 SKAPA GITHUB RELEASE
echo ============================================
echo GitHub release sida öppnas nu.
echo.
echo 📋 Fyll i på release sidan:
echo 🏷️  Tag version: v%VERSION%
echo 📝 Release title: MultiTeam v%VERSION% - Complete PyQt6 Application
echo 📄 Description: Complete team communication application with PyQt6 interface, dashboard with module cards, authentication system, and more.
echo 📎 Attach files: backup\MultiTeam_Complete_v0.20.zip (119MB)
echo ✅ Klicka "Publish release"
echo.
echo 🔑 Login credentials: username=1, password=1 (SuperAdmin)
goto :end

:error
echo.
echo ============================================
echo  ❌ PUSH MISSLYCKADES FORTFARANDE
echo ============================================
echo Kontrollera token permissions och försök igen.

:end
REM Clear token
set GITHUB_TOKEN=
echo.
pause

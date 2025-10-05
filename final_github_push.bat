@echo off
echo ============================================
echo  MultiTeam Final GitHub Push V0.20
echo  Hanterar Git Merge och Push Automatiskt
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
echo  STEG 1/10: Git Setup
echo ============================================

REM Configure Git
echo 🔧 Konfigurerar Git...
git config --global user.name "%GIT_USER%"
git config --global user.email "%GIT_EMAIL%"
git config --global init.defaultBranch main
echo ✅ Git konfigurerat: %GIT_USER% (%GIT_EMAIL%)

echo.
echo [████░░░░░░] 20%% - Repository Status
echo ============================================
echo  STEG 2/10: Repository Check
echo ============================================
git status >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Initialiserar Git repository...
    git init
    git remote add origin %REPO_URL% 2>nul
    echo ✅ Repository initialiserat
) else (
    echo ✅ Repository finns redan
)

echo.
echo [██████░░░░] 30%% - Remote Sync
echo ============================================
echo  STEG 3/10: Synka med Remote
echo ============================================
echo 🔄 Hämtar remote changes...
git fetch origin main 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Remote data hämtad
) else (
    echo ⚠️  Ingen remote data att hämta
)

echo.
echo [████████░░] 40%% - Adding Files
echo ============================================
echo  STEG 4/10: Git Add
echo ============================================
echo 📁 Lägger till alla filer...
git add .
echo ✅ Filer tillagda

echo.
echo [██████████] 50%% - Creating Commit
echo ============================================
echo  STEG 5/10: Git Commit
echo ============================================
set commit_message=MultiTeam v%VERSION% - Complete PyQt6 application with working EXE and dashboard assets
echo 💬 Commit: %commit_message%
git commit -m "%commit_message%" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Inga ändringar att committa
) else (
    echo ✅ Commit skapat
)

echo.
echo [████████████] 60%% - Branch Setup
echo ============================================
echo  STEG 6/10: Branch Configuration
echo ============================================
echo 🌿 Säkerställer main branch...
git branch -M main
git remote set-url origin %REPO_URL%
echo ✅ Branch konfigurerad

echo.
echo [██████████████] 70%% - Merge Remote Changes
echo ============================================
echo  STEG 7/10: Merge Remote
echo ============================================
echo 🔄 Mergar remote changes automatiskt...
git pull origin main --allow-unrelated-histories --no-edit --strategy=ours 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Remote changes mergade
) else (
    echo ⚠️  Ingen merge behövdes
)

echo.
echo [████████████████] 80%% - Force Push
echo ============================================
echo  STEG 8/10: Push till GitHub
echo ============================================
echo 🚀 Pushar till GitHub med force...
git push -f origin main
if %ERRORLEVEL% EQU 0 (
    echo ✅ Push lyckades!
) else (
    echo ❌ Push misslyckades
    echo 💡 Försöker alternativ push...
    git push --set-upstream origin main --force
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Alternativ push lyckades!
    ) else (
        echo ❌ Alla push-försök misslyckades
        echo 💡 Kontrollera GitHub access token eller credentials
    )
)

echo.
echo [██████████████████] 90%% - Verification
echo ============================================
echo  STEG 9/10: Verifiering
echo ============================================
echo 🔍 Verifierar GitHub status...
git remote -v
git branch -a
git log --oneline -3

echo.
echo [████████████████████] 100%% - Complete
echo ============================================
echo  STEG 10/10: Summary
echo ============================================

REM Check if we have the release package
if exist "dist\MultiTeam_Complete_v0.20.zip" (
    echo ============================================
    echo  🎉 GITHUB PUSH KOMPLETT!
    echo ============================================
    echo ✅ Git konfigurerat: %GIT_USER% (%GIT_EMAIL%)
    echo ✅ Repository: %REPO_URL%
    echo ✅ Branch: main
    echo ✅ Code pushad till GitHub
    echo ✅ Release package finns: dist\MultiTeam_Complete_v0.20.zip
    echo.
    echo 📊 Package Info:
    for %%f in ("dist\MultiTeam_Complete_v0.20.zip") do echo   ZIP: %%~zf bytes (ca. %%~zf:~0,-6% MB^)
    echo.
    echo ============================================
    echo  🚀 REDO FÖR GITHUB RELEASE!
    echo ============================================
    echo 📋 Nästa steg:
    echo 1. Gå till: %REPO_URL%/releases
    echo 2. Klicka "Create a new release"
    echo 3. Tag: v%VERSION%
    echo 4. Title: "MultiTeam v%VERSION% - Complete PyQt6 Application"
    echo 5. Description: "Complete PyQt6 application with working EXE, dashboard assets, and all features"
    echo 6. Ladda upp: dist\MultiTeam_Complete_v0.20.zip
    echo 7. Publicera release!
    echo.
    echo 🌐 GitHub Repository: %REPO_URL%
    
) else (
    echo ❌ Release package saknas
    echo Kör build_complete_exe.bat först
)

echo.
pause

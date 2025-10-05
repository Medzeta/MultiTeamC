@echo off
title MultiTeam Force Push to GitHub
echo ============================================
echo  MultiTeam Force Push till GitHub V0.20
echo  Löser alla Git merge-problem
echo ============================================

REM Exit any ongoing Git operations
taskkill /f /im git.exe 2>nul >nul

REM Remove any merge state
if exist ".git\MERGE_HEAD" del ".git\MERGE_HEAD"
if exist ".git\MERGE_MSG" del ".git\MERGE_MSG"

echo 🔧 Konfigurerar Git...
git config --global user.name "Medzeta"
git config --global user.email "medzetadesign@gmail.com"
git config --global init.defaultBranch main

echo 🔄 Återställer Git state...
git reset --hard HEAD 2>nul
git clean -fd 2>nul

echo 📁 Lägger till alla filer...
git add .

echo 💬 Skapar ny commit...
git commit -m "MultiTeam v0.20 - Complete PyQt6 application with working EXE and dashboard - Force push"

echo 🌿 Säkerställer main branch...
git branch -M main

echo 🚀 Force pushar till GitHub...
git push --force origin main

if %ERRORLEVEL% EQU 0 (
    echo ============================================
    echo  🎉 SUCCESS - PUSH LYCKADES!
    echo ============================================
    echo ✅ Kod pushad till GitHub
    echo ✅ Repository: https://github.com/Medzeta/Multi-Team-C
    echo ✅ Branch: main
    echo.
    echo 📋 Nästa steg:
    echo 1. Gå till: https://github.com/Medzeta/Multi-Team-C/releases
    echo 2. Klicka "Create a new release"
    echo 3. Tag: v0.20
    echo 4. Title: "MultiTeam v0.20 - Complete PyQt6 Application"
    echo 5. Ladda upp: dist\MultiTeam_Complete_v0.20.zip
    echo 6. Publicera release!
    
) else (
    echo ============================================
    echo  ❌ PUSH MISSLYCKADES FORTFARANDE
    echo ============================================
    echo Möjliga orsaker:
    echo 1. GitHub credentials saknas
    echo 2. Ingen internetanslutning
    echo 3. Repository permissions
    echo.
    echo Lösningar:
    echo 1. Kontrollera GitHub login
    echo 2. Skapa Personal Access Token
    echo 3. Kontrollera repository URL
)

echo.
echo ============================================
echo Du har redan ett fungerande release package:
echo dist\MultiTeam_Complete_v0.20.zip (119MB)
echo ============================================
pause

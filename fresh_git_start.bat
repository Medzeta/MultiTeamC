@echo off
title Fresh Git Start - No Token History
echo ============================================
echo  Fresh Git Start - No Token History
echo  Skapar helt ny Git-historik
echo ============================================

echo 🗑️ Tar bort hela .git mappen...
rmdir /s /q ".git" 2>nul

echo 🆕 Initialiserar nytt Git repository...
git init

echo 🔧 Git konfiguration...
git config --global user.name "Medzeta"
git config --global user.email "medzetadesign@gmail.com"

echo 📝 Skapar .gitignore...
(
    echo # Large files
    echo dist/
    echo build/
    echo *.exe
    echo *.zip
    echo __pycache__/
    echo *.pyc
    echo *.spec
    echo logs/
    echo backup/
    echo RELEASE_FILES/
) > .gitignore

echo 📁 Lägger till alla filer...
git add .

echo 💬 Skapar första commit...
git commit -m "MultiTeam v0.20 - Initial commit without tokens"

echo 🔐 Ange GitHub token:
set /p GITHUB_TOKEN="Token: "

echo 🔗 Lägger till remote...
git remote add origin https://Medzeta:%GITHUB_TOKEN%@github.com/Medzeta/Multi-Team-C.git

echo 🚀 Pushar till GitHub...
git push --force origin main

if %ERRORLEVEL% EQU 0 (
    echo ✅ Push lyckades!
    echo 🌐 Öppnar GitHub...
    start "" "https://github.com/Medzeta/Multi-Team-C"
    start "" "https://github.com/Medzeta/Multi-Team-C/releases/new"
    start "" "RELEASE_FILES"
) else (
    echo ❌ Push misslyckades fortfarande
)

pause

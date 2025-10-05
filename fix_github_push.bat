@echo off
title Fix GitHub Push Problem
echo ============================================
echo  Fix GitHub Push Problem
echo  Löser remote repository konflikter
echo ============================================

echo STEG 1: Kontrollerar nuvarande remote...
git remote -v

echo.
echo STEG 2: Fixar remote URL till rätt repository...
git remote remove origin 2>nul
git remote add origin https://github.com/Medzeta/Multi-Team-C.git

echo.
echo STEG 3: Kontrollerar branch...
git branch -a

echo.
echo STEG 4: Säkerställer main branch...
git branch -M main

echo.
echo STEG 5: Försöker pusha med force (säkert eftersom vi äger repo)...
echo Ange ditt GitHub Personal Access Token:
set /p GITHUB_TOKEN="Token: "

if "%GITHUB_TOKEN%"=="" (
    echo Ingen token angiven
    pause
    exit /b 1
)

echo.
echo Uppdaterar remote med token...
git remote set-url origin https://Medzeta:%GITHUB_TOKEN%@github.com/Medzeta/Multi-Team-C.git

echo.
echo Pushar med force...
git push --force origin main

if %ERRORLEVEL% EQU 0 (
    echo ✅ Push lyckades!
    echo.
    echo Öppnar GitHub repository...
    start "" "https://github.com/Medzeta/Multi-Team-C"
) else (
    echo ❌ Push misslyckades fortfarande
    echo Kontrollera token och repository URL
)

REM Clear token
set GITHUB_TOKEN=
pause

@echo off
title Safe GitHub Push
echo ============================================
echo  Safe GitHub Push - Med felhantering
echo  Säker version som inte kraschar
echo ============================================

REM Set variables
set VERSION=0.20
set REPO_URL=https://github.com/Medzeta/Multi-Team-C
set GIT_USER=Medzeta
set GIT_EMAIL=medzetadesign@gmail.com

echo.
echo STEG 1: Token input...
echo Ange ditt GitHub Personal Access Token:
set /p GITHUB_TOKEN="Token: "

if "%GITHUB_TOKEN%"=="" (
    echo ERROR: Ingen token angiven
    pause
    exit /b 1
)

echo DEBUG: Token mottaget (längd: %GITHUB_TOKEN:~0,10%...)
echo.

echo STEG 2: Git konfiguration...
git config --global user.name "%GIT_USER%"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git config user.name misslyckades
    pause
    exit /b 1
)

git config --global user.email "%GIT_EMAIL%"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git config user.email misslyckades
    pause
    exit /b 1
)

echo DEBUG: Git config OK
echo.

echo STEG 3: Kontrollerar .git mapp...
if exist ".git" (
    echo DEBUG: .git mapp finns, tar bort den...
    rmdir /s /q ".git"
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Kunde inte ta bort .git mapp
        pause
        exit /b 1
    )
)

echo DEBUG: Initialiserar nytt Git repo...
git init
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git init misslyckades
    pause
    exit /b 1
)

echo DEBUG: Git init OK
echo.

echo STEG 4: Skapar .gitignore...
(
    echo dist/
    echo backup/
    echo *.exe
    echo *.zip
    echo build/
    echo __pycache__/
    echo *.pyc
    echo *.spec
    echo logs/
    echo RELEASE_FILES/
) > .gitignore

echo DEBUG: .gitignore skapad
echo.

echo STEG 5: Flyttar stora filer...
if not exist "RELEASE_FILES" mkdir "RELEASE_FILES"

if exist "backup\MultiTeam.exe" (
    echo DEBUG: Flyttar backup\MultiTeam.exe...
    move "backup\MultiTeam.exe" "RELEASE_FILES\" >nul 2>&1
)

if exist "dist\MultiTeam.exe" (
    echo DEBUG: Flyttar dist\MultiTeam.exe...
    move "dist\MultiTeam.exe" "RELEASE_FILES\" >nul 2>&1
)

echo DEBUG: Stora filer flyttade
echo.

echo STEG 6: Lägger till remote...
git remote add origin https://%GIT_USER%:%GITHUB_TOKEN%@github.com/Medzeta/Multi-Team-C.git
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Kunde inte lägga till remote
    pause
    exit /b 1
)

echo DEBUG: Remote tillagd
echo.

echo STEG 7: Git add...
git add .
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git add misslyckades
    pause
    exit /b 1
)

echo DEBUG: Filer tillagda
echo.

echo STEG 8: Git commit...
git commit -m "MultiTeam v%VERSION% - Source code only"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git commit misslyckades
    pause
    exit /b 1
)

echo DEBUG: Commit skapat
echo.

echo STEG 9: Testar GitHub koppling...
git ls-remote origin HEAD >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Kan inte ansluta till GitHub
    echo Kontrollera token och internetanslutning
    pause
    exit /b 1
)

echo DEBUG: GitHub koppling OK
echo.

echo STEG 10: Push till GitHub...
git push -u origin main
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Push misslyckades
    echo Försöker med force push...
    git push --force origin main
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Force push misslyckades också
        pause
        exit /b 1
    )
)

echo.
echo ============================================
echo  SUCCESS! PUSH LYCKADES!
echo ============================================
echo Repository: %REPO_URL%
echo.
echo Öppnar GitHub...
start "" "%REPO_URL%"
start "" "%REPO_URL%/releases/new"

echo.
echo EXE-fil för release finns i: RELEASE_FILES\
dir "RELEASE_FILES\" 2>nul

REM Clear token
set GITHUB_TOKEN=
echo.
pause

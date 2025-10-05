@echo off
title Debug Fresh Start GitHub Push
echo ============================================
echo  Debug Fresh Start GitHub Push
echo  Visar detaljerad debug-information
echo ============================================

echo DEBUG: Current directory: %CD%
echo DEBUG: Date/Time: %DATE% %TIME%
echo.

echo STEG 1: Kontrollerar nuvarande Git status...
if exist ".git" (
    echo DEBUG: .git mapp finns
    git status 2>&1
) else (
    echo DEBUG: Ingen .git mapp finns
)

echo.
echo STEG 2: Kontrollerar stora filer...
echo DEBUG: Letar efter EXE-filer:
dir *.exe /s 2>nul
echo.
echo DEBUG: Letar efter ZIP-filer:
dir *.zip /s 2>nul

echo.
echo STEG 3: Kontrollerar disk space...
dir | find "bytes free"

echo.
echo STEG 4: Kontrollerar Git installation...
git --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git inte installerat eller inte i PATH
    pause
    exit /b 1
)

echo.
echo STEG 5: Testar internetanslutning...
ping github.com -n 2
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Ingen internetanslutning till GitHub
    pause
    exit /b 1
)

echo.
echo STEG 6: Kontrollerar permissions...
echo DEBUG: Försöker skapa testfil...
echo test > test_permissions.txt
if exist "test_permissions.txt" (
    echo DEBUG: Write permissions OK
    del "test_permissions.txt"
) else (
    echo ERROR: Inga write permissions
    pause
    exit /b 1
)

echo.
echo ============================================
echo  DEBUG INFORMATION KOMPLETT
echo ============================================
echo Allt ser OK ut. Vill du fortsätta med fresh start? (Y/N)
set /p continue="Fortsätt: "

if /i "%continue%"=="Y" (
    echo.
    echo Startar fresh start process...
    call fresh_start_github.bat
) else (
    echo Avbryter.
)

pause

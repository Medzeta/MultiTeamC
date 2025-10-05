@echo off
title Läs Debug Loggar
echo ============================================
echo  Läser Debug Loggar
echo  Kontrollerar vad som gick fel
echo ============================================

echo.
echo KONTROLLERAR BEFINTLIGA LOGGAR:
echo ============================================

echo.
echo 1. Git loggar (om de finns):
if exist ".git\logs\HEAD" (
    echo Git HEAD log:
    type ".git\logs\HEAD" 2>nul
) else (
    echo Inga Git HEAD loggar
)

echo.
echo 2. Windows Event loggar för Git:
echo Senaste Git-relaterade fel:
wevtutil qe Application /c:5 /f:text /q:"*[System[Provider[@Name='Git']]]" 2>nul

echo.
echo 3. Kontrollerar Git konfiguration:
echo Git version:
git --version 2>&1

echo.
echo Git global config:
git config --global --list 2>&1

echo.
echo 4. Kontrollerar remote (om det finns):
if exist ".git" (
    echo Git remote:
    git remote -v 2>&1
    echo.
    echo Git status:
    git status 2>&1
) else (
    echo Ingen .git mapp finns
)

echo.
echo 5. Kontrollerar stora filer:
echo EXE-filer:
dir *.exe /s 2>nul | find ".exe"
echo.
echo ZIP-filer:
dir *.zip /s 2>nul | find ".zip"

echo.
echo 6. Kontrollerar internetanslutning:
echo Ping GitHub:
ping github.com -n 2 2>&1

echo.
echo 7. Kontrollerar permissions:
echo Skapar testfil...
echo test > test_write.tmp
if exist "test_write.tmp" (
    echo Write permissions: OK
    del "test_write.tmp"
) else (
    echo Write permissions: PROBLEM
)

echo.
echo ============================================
echo  REKOMMENDATIONER:
echo ============================================
echo.
echo Om Git kraschar:
echo 1. Kör: .\debug_to_file.bat (sparar allt till fil)
echo 2. Kontrollera debug_log.txt efter krasch
echo 3. Skicka innehållet i debug_log.txt
echo.
echo Om token-problem:
echo 1. Kontrollera att token är giltigt på GitHub
echo 2. Kontrollera att token har 'repo' permissions
echo 3. Testa token manuellt: git ls-remote https://token@github.com/repo
echo.
pause

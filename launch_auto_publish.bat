@echo off
echo ============================================
echo  MultiTeam Auto Publish Launcher
echo  Startar i eget fönster med debug
echo ============================================
echo.
echo Startar auto publish system i nytt fönster...
echo.
echo Detta kommer att:
echo - Bygga ny EXE automatiskt
echo - Pusha källkod till GitHub
echo - Öppna GitHub release sida
echo - Skapa release information
echo - Hantera alla fel automatiskt
echo.
echo Tryck valfri tangent för att starta...
pause >nul

start "MultiTeam Auto Publish System" cmd /k "cd /d "%~dp0" && auto_publish_with_debug.bat"

echo.
echo ✅ Auto publish system startat i nytt fönster!
echo.
echo Om något går fel kommer debug-informationen att visas
echo i det nya fönstret och sparas i auto_publish_debug.log
echo.
pause

@echo off
echo Startar GitHub Push Debug i nytt fönster...
start "MultiTeam GitHub Push Debug" cmd /k "cd /d "%~dp0" && debug_github_push.bat"
echo Debug fönster öppnat!
pause

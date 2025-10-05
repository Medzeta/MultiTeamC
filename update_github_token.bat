@echo off
echo ========================================
echo   UPPDATERA GITHUB TOKEN
echo ========================================
echo.

set /p TOKEN="Klistra in din nya GitHub token: "

echo.
echo Uppdaterar git remote...
git remote remove origin 2>nul
git remote add origin https://Medzeta:%TOKEN%@github.com/Medzeta/Multi-Team-C.git

echo.
echo ✅ Token uppdaterad!
echo.
echo Testa med: git remote -v
echo.
pause

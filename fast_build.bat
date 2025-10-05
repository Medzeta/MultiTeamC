@echo off
echo ============================================
echo  MultiTeam Fast Build - Minimal EXE
echo ============================================

echo Step 1: Cleaning...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
for %%f in (*.spec) do del "%%f"

echo Step 2: Fast PyInstaller build...
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name=MultiTeam ^
    --noconfirm ^
    --log-level=WARN ^
    main_pyqt.py

if exist "dist\MultiTeam.exe" (
    echo ============================================
    echo  ✅ BUILD SUCCESS!
    echo ============================================
    echo EXE: dist\MultiTeam.exe
    dir "dist\MultiTeam.exe"
    echo.
    echo Testing EXE...
    echo Starting MultiTeam.exe for 3 seconds...
    start /B "Test" "dist\MultiTeam.exe"
    timeout /t 3 /nobreak >nul
    taskkill /f /im "MultiTeam.exe" 2>nul >nul
    echo Test completed.
    echo.
    echo ============================================
    echo Ready to run: dist\MultiTeam.exe
    echo ============================================
) else (
    echo ❌ Build failed - EXE not created
    echo Check for errors above
)

pause

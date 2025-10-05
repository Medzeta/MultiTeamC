@echo off
echo ============================================
echo  Quick EXE Test - Fix High DPI Error
echo ============================================

echo Step 1: Cleaning...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
for %%f in (*.spec) do del "%%f"

echo Step 2: Fast build with error handling...
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name=MultiTeam ^
    --noconfirm ^
    --log-level=ERROR ^
    main_pyqt.py

if exist "dist\MultiTeam.exe" (
    echo ============================================
    echo  ✅ BUILD SUCCESS!
    echo ============================================
    echo Testing EXE startup...
    
    REM Test EXE startup
    echo Starting MultiTeam.exe...
    start "" "dist\MultiTeam.exe"
    
    REM Wait a moment for startup
    timeout /t 5 /nobreak >nul
    
    REM Check if process is running
    tasklist /fi "imagename eq MultiTeam.exe" 2>nul | find /i "MultiTeam.exe" >nul
    if %errorlevel% equ 0 (
        echo ✅ EXE is running!
        echo Check if login window is visible...
        
        REM Kill the process for clean exit
        taskkill /f /im "MultiTeam.exe" 2>nul >nul
        
        echo.
        echo ============================================
        echo SUCCESS! EXE starts without crashing
        echo ============================================
    ) else (
        echo ❌ EXE crashed or failed to start
        echo Check logs for errors...
        if exist "logs" (
            echo Latest log:
            dir /o:d "logs\*.log" | findstr /v "Directory" | findstr /v "File(s)" | tail -1
        )
    )
    
) else (
    echo ❌ Build failed
)

pause

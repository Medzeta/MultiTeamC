@echo off
echo ============================================
echo  MultiTeam Fixed EXE Builder V0.20
echo  Fixing PyQt6 Window Display Issues
echo ============================================

echo Step 1: Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
for %%f in (*.spec) do del "%%f"

echo Step 2: Building EXE with PyQt6 window fixes...
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name=MultiTeam ^
    --noconfirm ^
    --log-level=WARN ^
    --add-data="core;core" ^
    --add-data="modules_pyqt;modules_pyqt" ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=PyQt6.sip ^
    --collect-submodules=PyQt6 ^
    --collect-data=PyQt6 ^
    --collect-binaries=PyQt6 ^
    main_pyqt.py

if exist "dist\MultiTeam.exe" (
    echo ============================================
    echo  ✅ BUILD SUCCESS!
    echo ============================================
    echo EXE: dist\MultiTeam.exe
    dir "dist\MultiTeam.exe"
    echo.
    
    echo Step 3: Testing EXE window display...
    echo Starting MultiTeam.exe - CHECK IF LOGIN WINDOW APPEARS!
    echo.
    echo ⚠️  IMPORTANT: Look for the login window to appear
    echo    If no window appears, there's still a PyQt6 issue
    echo.
    
    REM Start EXE and wait for user confirmation
    start "" "dist\MultiTeam.exe"
    
    echo.
    echo ============================================
    echo  Did the login window appear? (Y/N)
    echo ============================================
    set /p window_appeared="Window appeared (Y/N): "
    
    if /i "%window_appeared%"=="Y" (
        echo ✅ SUCCESS! Window display fixed!
        echo.
        echo Creating release package...
        
        REM Create package directory
        if not exist "dist\MultiTeam_Package" mkdir "dist\MultiTeam_Package"
        
        REM Copy EXE
        copy "dist\MultiTeam.exe" "dist\MultiTeam_Package\"
        
        REM Copy docs
        if exist "README.md" copy "README.md" "dist\MultiTeam_Package\"
        if exist "ROADMAP.md" copy "ROADMAP.md" "dist\MultiTeam_Package\"
        if exist "HOW_TO_RUN.md" copy "HOW_TO_RUN.md" "dist\MultiTeam_Package\"
        
        REM Create directories
        mkdir "dist\MultiTeam_Package\data" 2>nul
        mkdir "dist\MultiTeam_Package\logs" 2>nul
        
        REM Create ZIP
        powershell -NoProfile -Command "Compress-Archive -Path 'dist/MultiTeam_Package/*' -DestinationPath 'dist/MultiTeam_Package_v0.20.zip' -Force"
        
        echo ============================================
        echo  📦 RELEASE PACKAGE READY!
        echo ============================================
        echo • EXE: dist\MultiTeam_Package\MultiTeam.exe
        echo • ZIP: dist\MultiTeam_Package_v0.20.zip
        echo.
        echo Package contents:
        dir "dist\MultiTeam_Package"
        echo.
        echo ZIP file:
        dir "dist\MultiTeam_Package_v0.20.zip"
        
    ) else (
        echo ❌ Window display still not working
        echo Need to investigate PyQt6 EXE issues further
        echo.
        echo Checking for error logs...
        if exist "logs" (
            echo Latest log files:
            dir /o:d "logs\*.log" | findstr /v "Directory"
        )
    )
    
) else (
    echo ❌ Build failed - EXE not created
    echo Check for errors above
)

echo.
echo ============================================
echo Build process completed
echo ============================================
pause

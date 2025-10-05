@echo off
echo ============================================
echo  MultiTeam Complete EXE Builder V0.20
echo  Including Assets and All Dependencies
echo ============================================

echo Step 1: Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
for %%f in (*.spec) do del "%%f"

echo Step 2: Building complete EXE with assets...
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name=MultiTeam ^
    --noconfirm ^
    --log-level=WARN ^
    --add-data="core;core" ^
    --add-data="modules_pyqt;modules_pyqt" ^
    --add-data="assets;assets" ^
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
    echo  ✅ BUILD SUCCESS WITH ASSETS!
    echo ============================================
    echo EXE: dist\MultiTeam.exe
    dir "dist\MultiTeam.exe"
    echo.
    
    echo Step 3: Testing EXE with dashboard data...
    echo Starting MultiTeam.exe - CHECK DASHBOARD IMAGES!
    echo.
    echo ⚠️  IMPORTANT: 
    echo    1. Login with SuperAdmin (1/1)
    echo    2. Check if dashboard shows module cards with images
    echo    3. Verify all data displays correctly
    echo.
    
    REM Start EXE for testing
    start "" "dist\MultiTeam.exe"
    
    echo.
    echo ============================================
    echo  Dashboard Test Instructions:
    echo ============================================
    echo 1. Login with username: 1, password: 1
    echo 2. Look for dashboard module cards
    echo 3. Check if images load (P2P Chat, Team Chat, etc.)
    echo 4. Verify all UI elements display correctly
    echo.
    set /p dashboard_works="Does dashboard show data correctly? (Y/N): "
    
    if /i "%dashboard_works%"=="Y" (
        echo ✅ SUCCESS! Dashboard data working in EXE!
        echo.
        echo Creating final release package...
        
        REM Create package directory
        if not exist "dist\MultiTeam_Final_v0.20" mkdir "dist\MultiTeam_Final_v0.20"
        
        REM Copy EXE
        copy "dist\MultiTeam.exe" "dist\MultiTeam_Final_v0.20\"
        
        REM Copy documentation
        if exist "README.md" copy "README.md" "dist\MultiTeam_Final_v0.20\"
        if exist "ROADMAP.md" copy "ROADMAP.md" "dist\MultiTeam_Final_v0.20\"
        if exist "HOW_TO_RUN.md" copy "HOW_TO_RUN.md" "dist\MultiTeam_Final_v0.20\"
        if exist "FINAL_PROJECT_SUMMARY.md" copy "FINAL_PROJECT_SUMMARY.md" "dist\MultiTeam_Final_v0.20\"
        
        REM Create user directories
        mkdir "dist\MultiTeam_Final_v0.20\data" 2>nul
        mkdir "dist\MultiTeam_Final_v0.20\logs" 2>nul
        
        REM Create installation guide
        (
            echo # MultiTeam v0.20 - Complete Installation Package
            echo.
            echo ## Quick Start:
            echo 1. Run MultiTeam.exe
            echo 2. Login with SuperAdmin: username=1, password=1
            echo 3. Explore all features!
            echo.
            echo ## Features Included:
            echo ✅ Modern PyQt6 interface with dashboard
            echo ✅ Secure authentication system
            echo ✅ Email verification system
            echo ✅ License management system
            echo ✅ Auto-update system
            echo ✅ 2FA support
            echo ✅ Module cards with images
            echo ✅ Complete user management
            echo.
            echo ## System Requirements:
            echo - Windows 10/11 64-bit
            echo - No additional dependencies required
            echo - All assets embedded in EXE
            echo.
            echo ## Default Login:
            echo - Username: 1
            echo - Password: 1
            echo - This is the SuperAdmin account
            echo.
            echo ## Build Information:
            echo - Version: 0.20
            echo - Build Date: %DATE% %TIME%
            echo - PyQt6 Version with complete asset support
            echo - All dashboard images included
        ) > "dist\MultiTeam_Final_v0.20\README_INSTALL.md"
        
        REM Create ZIP package
        powershell -NoProfile -Command "Compress-Archive -Path 'dist/MultiTeam_Final_v0.20/*' -DestinationPath 'dist/MultiTeam_Complete_v0.20.zip' -Force"
        
        echo ============================================
        echo  🎉 COMPLETE PACKAGE READY!
        echo ============================================
        echo 📦 Folder: dist\MultiTeam_Final_v0.20\
        echo 📄 ZIP: dist\MultiTeam_Complete_v0.20.zip
        echo.
        echo Package contents:
        dir "dist\MultiTeam_Final_v0.20"
        echo.
        echo ZIP file size:
        dir "dist\MultiTeam_Complete_v0.20.zip"
        echo.
        echo ============================================
        echo READY FOR GITHUB RELEASE!
        echo ============================================
        
    ) else (
        echo ❌ Dashboard data not working correctly
        echo Need to investigate asset loading issues
        echo.
        echo Checking latest log for errors...
        if exist "logs" (
            echo Latest log files:
            dir /o:d "logs\*.log" | findstr /v "Directory" | tail -3
        )
    )
    
) else (
    echo ❌ Build failed - EXE not created
    echo Check for errors above
)

echo.
pause

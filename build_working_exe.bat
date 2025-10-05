@echo off
echo ============================================
echo  MultiTeam Working EXE Builder V0.20
echo ============================================

echo Step 1: Cleaning...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
for %%f in (*.spec) do del "%%f"

echo Step 2: Building EXE with PyQt6 fixes...
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
    --collect-all=PyQt6 ^
    main_pyqt.py

if exist "dist\MultiTeam.exe" (
    echo ============================================
    echo  ✅ BUILD SUCCESS!
    echo ============================================
    echo EXE: dist\MultiTeam.exe
    dir "dist\MultiTeam.exe"
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
    echo Testing EXE with window display...
    echo Starting MultiTeam.exe...
    start "" "dist\MultiTeam_Package\MultiTeam.exe"
    echo.
    echo ============================================
    echo Check if the login window appears!
    echo ============================================
    
) else (
    echo ❌ Build failed - EXE not created
    echo Check for errors above
)

pause

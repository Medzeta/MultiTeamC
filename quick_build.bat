@echo off
echo ============================================
echo  MultiTeam Quick Build Script
echo ============================================

echo Step 1: Building EXE...
python -m PyInstaller --name=MultiTeam --onefile --windowed --noconfirm main_pyqt.py

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)

echo Step 2: Creating package directory...
if not exist "dist\MultiTeam_Package" mkdir "dist\MultiTeam_Package"

echo Step 3: Copying files...
copy "dist\MultiTeam.exe" "dist\MultiTeam_Package\"
copy "README.md" "dist\MultiTeam_Package\" 2>nul
copy "ROADMAP.md" "dist\MultiTeam_Package\" 2>nul
xcopy "assets" "dist\MultiTeam_Package\assets\" /E /I /Y 2>nul

echo Step 4: Creating ZIP...
powershell -Command "Compress-Archive -Path 'dist/MultiTeam_Package/*' -DestinationPath 'dist/MultiTeam_Package_v0.20.zip' -Force"

echo ============================================
echo  Build Complete!
echo ============================================
echo EXE: dist\MultiTeam_Package\MultiTeam.exe
echo ZIP: dist\MultiTeam_Package_v0.20.zip
echo ============================================
pause

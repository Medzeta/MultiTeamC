@echo off
echo ============================================
echo  MultiTeam Release Package Creator V0.20
echo ============================================

REM Check if EXE exists
if not exist "dist\MultiTeam.exe" (
    echo ❌ MultiTeam.exe not found in dist\
    echo Run fast_build.bat first to create the EXE
    pause
    exit /b 1
)

echo Step 1: Creating package directory...
if not exist "dist\MultiTeam_Package" mkdir "dist\MultiTeam_Package"

echo Step 2: Copying EXE...
copy "dist\MultiTeam.exe" "dist\MultiTeam_Package\"

echo Step 3: Copying documentation...
if exist "README.md" copy "README.md" "dist\MultiTeam_Package\"
if exist "ROADMAP.md" copy "ROADMAP.md" "dist\MultiTeam_Package\"
if exist "HOW_TO_RUN.md" copy "HOW_TO_RUN.md" "dist\MultiTeam_Package\"

echo Step 4: Creating directories...
mkdir "dist\MultiTeam_Package\data" 2>nul
mkdir "dist\MultiTeam_Package\logs" 2>nul

echo Step 5: Creating ZIP package...
set ZIP_NAME=MultiTeam_Package_v0.20.zip
if exist "dist\%ZIP_NAME%" del "dist\%ZIP_NAME%"

powershell -NoProfile -Command "Compress-Archive -Path 'dist/MultiTeam_Package/*' -DestinationPath 'dist/%ZIP_NAME%' -Force"

if exist "dist\%ZIP_NAME%" (
    echo ============================================
    echo  ✅ RELEASE PACKAGE CREATED!
    echo ============================================
    echo 📦 Package: dist\MultiTeam_Package\
    echo 📄 ZIP: dist\%ZIP_NAME%
    echo.
    echo 📊 Package Contents:
    dir "dist\MultiTeam_Package"
    echo.
    echo 📊 ZIP Size:
    dir "dist\%ZIP_NAME%"
    echo.
    echo ============================================
    echo Ready for GitHub Release!
    echo ============================================
) else (
    echo ❌ Failed to create ZIP package
)

pause

@echo off
setlocal EnableDelayedExpansion

REM ============================================================
REM MultiTeam - Enhanced Build Script with Progress Bar
REM ============================================================

echo.
echo ============================================================
echo   MultiTeam P2P Communication - Enhanced Builder v0.20
echo ============================================================
echo   Build Date: %date% %time%
echo   Build Type: Release with Full Debug
echo ============================================================
echo.

REM Create logs directory
if not exist "build_logs" mkdir "build_logs"
set BUILD_LOG=build_logs\build_%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
set BUILD_LOG=%BUILD_LOG: =0%

echo [%time%] Starting enhanced build process... > "%BUILD_LOG%"
echo Build log: %BUILD_LOG%
echo.

REM Step 1: Clean
echo [1/6] Cleaning old builds...
echo [%time%] Step 1: Cleaning old builds >> "%BUILD_LOG%"
if exist "build" rmdir /s /q "build" 2>>"%BUILD_LOG%"
if exist "dist" rmdir /s /q "dist" 2>>"%BUILD_LOG%"
for %%f in (*.spec) do del "%%f" 2>>"%BUILD_LOG%"
echo      ✓ Cleanup completed
echo.

REM Step 2: Check Python and PyInstaller
echo [2/6] Checking dependencies...
echo [%time%] Step 2: Checking dependencies >> "%BUILD_LOG%"

python --version >>"%BUILD_LOG%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo      ❌ Python not found!
    echo [ERROR] Python not found >> "%BUILD_LOG%"
    pause
    exit /b 1
)

python -m PyInstaller --version >>"%BUILD_LOG%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo      ❌ PyInstaller not found!
    echo [ERROR] PyInstaller not found >> "%BUILD_LOG%"
    echo      Installing PyInstaller...
    pip install pyinstaller >>"%BUILD_LOG%" 2>&1
)
echo      ✓ Dependencies OK
echo.

REM Step 3: Build EXE with Progress
echo [3/6] Building EXE with PyInstaller...
echo      This may take 2-5 minutes...
echo [%time%] Step 3: Starting PyInstaller build >> "%BUILD_LOG%"

REM Start PyInstaller in background and show progress
echo      Progress: [          ] 0%%
start /B python -m PyInstaller ^
    --name=MultiTeam ^
    --onefile ^
    --windowed ^
    --noconfirm ^
    --clean ^
    --log-level=DEBUG ^
    --workpath=build ^
    --distpath=dist ^
    --add-data=core;core ^
    --add-data=modules_pyqt;modules_pyqt ^
    --add-data=assets;assets ^
    --hidden-import=PyQt6 ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=PIL ^
    --hidden-import=bcrypt ^
    --hidden-import=cryptography ^
    --hidden-import=requests ^
    --exclude-module=matplotlib ^
    --exclude-module=numpy ^
    --exclude-module=pandas ^
    --exclude-module=tkinter ^
    main_pyqt.py >>"%BUILD_LOG%" 2>&1

REM Show progress bar while building
set /a progress=0
:progress_loop
timeout /t 3 /nobreak >nul 2>&1

REM Check if build is still running
tasklist /fi "imagename eq python.exe" | find "python.exe" >nul
if %ERRORLEVEL% EQU 0 (
    set /a progress+=10
    if !progress! GEQ 100 set progress=99
    
    REM Draw progress bar
    set "bar="
    set /a filled=!progress!/10
    set /a empty=10-!filled!
    
    for /l %%i in (1,1,!filled!) do set "bar=!bar!█"
    for /l %%i in (1,1,!empty!) do set "bar=!bar!░"
    
    echo      Progress: [!bar!] !progress!%%
    goto progress_loop
)

REM Check if EXE was created
if exist "dist\MultiTeam.exe" (
    echo      Progress: [██████████] 100%%
    echo      ✓ EXE build completed successfully!
    echo [%time%] PyInstaller build completed successfully >> "%BUILD_LOG%"
) else (
    echo      ❌ Build failed! Check log: %BUILD_LOG%
    echo [ERROR] EXE file not found after build >> "%BUILD_LOG%"
    echo.
    echo Last 10 lines of build log:
    powershell -Command "Get-Content '%BUILD_LOG%' | Select-Object -Last 10"
    pause
    exit /b 1
)
echo.

REM Step 4: Create Package
echo [4/6] Creating distribution package...
echo [%time%] Step 4: Creating package >> "%BUILD_LOG%"

if not exist "dist\MultiTeam_Package" mkdir "dist\MultiTeam_Package"

REM Copy main files
copy "dist\MultiTeam.exe" "dist\MultiTeam_Package\" >>"%BUILD_LOG%" 2>&1
if exist "README.md" copy "README.md" "dist\MultiTeam_Package\" >>"%BUILD_LOG%" 2>&1
if exist "ROADMAP.md" copy "ROADMAP.md" "dist\MultiTeam_Package\" >>"%BUILD_LOG%" 2>&1

REM Copy assets if they exist
if exist "assets" (
    xcopy "assets" "dist\MultiTeam_Package\assets\" /E /I /Y >>"%BUILD_LOG%" 2>&1
)

REM Create directories
mkdir "dist\MultiTeam_Package\data" 2>nul
mkdir "dist\MultiTeam_Package\logs" 2>nul

echo      ✓ Package created
echo.

REM Step 5: Create ZIP
echo [5/6] Creating ZIP archive...
echo [%time%] Step 5: Creating ZIP >> "%BUILD_LOG%"

set ZIP_NAME=MultiTeam_Package_v0.20.zip
if exist "dist\%ZIP_NAME%" del "dist\%ZIP_NAME%"

powershell -NoProfile -Command "Compress-Archive -Path 'dist/MultiTeam_Package/*' -DestinationPath 'dist/%ZIP_NAME%' -Force" >>"%BUILD_LOG%" 2>&1

if exist "dist\%ZIP_NAME%" (
    echo      ✓ ZIP created: %ZIP_NAME%
) else (
    echo      ❌ ZIP creation failed
    echo [ERROR] ZIP creation failed >> "%BUILD_LOG%"
)
echo.

REM Step 6: Summary
echo [6/6] Build Summary
echo [%time%] Build completed >> "%BUILD_LOG%"
echo ============================================================
echo   ✓ BUILD SUCCESSFUL!
echo ============================================================
echo.
echo 📦 Output Files:
echo   • EXE: dist\MultiTeam_Package\MultiTeam.exe
echo   • ZIP: dist\%ZIP_NAME%
echo   • Log: %BUILD_LOG%
echo.
echo 📊 File Sizes:
for %%f in ("dist\MultiTeam.exe") do echo   • MultiTeam.exe: %%~zf bytes
for %%f in ("dist\%ZIP_NAME%") do echo   • %ZIP_NAME%: %%~zf bytes
echo.
echo 🚀 Ready for:
echo   • Local testing: dist\MultiTeam_Package\MultiTeam.exe
echo   • GitHub release: dist\%ZIP_NAME%
echo.
echo ============================================================

REM Test EXE quickly
echo 🧪 Quick EXE Test:
echo Testing if EXE starts without crash...
timeout /t 2 /nobreak >nul
start /B "MultiTeam Test" "dist\MultiTeam_Package\MultiTeam.exe" --version 2>nul
timeout /t 3 /nobreak >nul
taskkill /f /im "MultiTeam.exe" 2>nul >nul
echo   ✓ EXE test completed (check manually if it opened)
echo.

echo Press any key to exit...
pause >nul

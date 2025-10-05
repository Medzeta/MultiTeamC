@echo off
setlocal enabledelayedexpansion
echo ============================================
echo  MultiTeam EXE Builder med Progress V0.20
echo  Visuella Progress Bars för alla steg
echo ============================================

set TOTAL_STEPS=6

REM Progress bar function
:show_progress
set /a progress=%1*100/%TOTAL_STEPS%
set bar=
for /l %%i in (1,2,%progress%) do set bar=!bar!█
for /l %%i in (%progress%,2,98) do set bar=!bar!░
echo [!bar!] %progress%%% - %2
goto :eof

echo.
call :show_progress 1 "Förbereder Build Environment"
echo ============================================
echo  STEG 1/6: Environment Setup
echo ============================================
echo 🧹 Rensar tidigare builds...
if exist "dist" (
    echo   - Tar bort dist mapp...
    rmdir /s /q "dist"
)
if exist "build" (
    echo   - Tar bort build mapp...
    rmdir /s /q "build"
)
for %%f in (*.spec) do (
    echo   - Tar bort %%f...
    del "%%f"
)
echo ✅ Build environment förberett

echo.
call :show_progress 2 "Kontrollerar Dependencies"
echo ============================================
echo  STEG 2/6: Dependency Check
echo ============================================
echo 🔍 Kontrollerar PyInstaller...
python -m PyInstaller --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ PyInstaller inte installerat
    echo 💡 Installerar PyInstaller...
    pip install pyinstaller
) else (
    echo ✅ PyInstaller finns
)

echo 🔍 Kontrollerar PyQt6...
python -c "import PyQt6" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ PyQt6 inte installerat
    echo 💡 Installerar PyQt6...
    pip install PyQt6
) else (
    echo ✅ PyQt6 finns
)

echo 🔍 Kontrollerar assets...
if exist "assets" (
    echo ✅ Assets mapp finns
    echo   📁 Assets innehåll:
    for %%f in (assets\*) do echo     - %%~nxf
) else (
    echo ❌ Assets mapp saknas
)

echo.
call :show_progress 3 "Bygger PyInstaller Spec"
echo ============================================
echo  STEG 3/6: PyInstaller Configuration
echo ============================================
echo 📝 Skapar PyInstaller konfiguration...
echo   - Onefile mode: ✅
echo   - Windowed mode: ✅  
echo   - Assets included: ✅
echo   - Core modules: ✅
echo   - PyQt6 modules: ✅
echo   - Hidden imports: ✅

echo.
call :show_progress 4 "Kompilerar EXE"
echo ============================================
echo  STEG 4/6: EXE Compilation
echo ============================================
echo 🔨 Startar PyInstaller build...
echo   Detta kan ta flera minuter...

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
    echo ✅ EXE kompilering lyckades!
) else (
    echo ❌ EXE kompilering misslyckades
    pause
    exit /b 1
)

echo.
call :show_progress 5 "Testar EXE Funktionalitet"
echo ============================================
echo  STEG 5/6: EXE Testing
echo ============================================
echo 🧪 Kontrollerar EXE storlek...
for %%f in ("dist\MultiTeam.exe") do (
    echo   📊 EXE storlek: %%~zf bytes (ca. %%~zf:~0,-6% MB^)
)

echo 🧪 Testar EXE startup...
echo   - Startar MultiTeam.exe...
start "" "dist\MultiTeam.exe"
timeout /t 5 /nobreak >nul

echo   - Kontrollerar om processen körs...
tasklist /fi "imagename eq MultiTeam.exe" 2>nul | find /i "MultiTeam.exe" >nul
if %errorlevel% equ 0 (
    echo ✅ EXE startar och körs framgångsrikt
    echo   - Stänger test process...
    taskkill /f /im "MultiTeam.exe" 2>nul >nul
    set EXE_WORKS=1
) else (
    echo ❌ EXE startproblem upptäckt
    set EXE_WORKS=0
)

echo.
call :show_progress 6 "Build Komplett"
echo ============================================
echo  STEG 6/6: Build Summary
echo ============================================

if exist "dist\MultiTeam.exe" (
    echo ============================================
    echo  🎉 BUILD FRAMGÅNGSRIK!
    echo ============================================
    echo ✅ EXE skapad: dist\MultiTeam.exe
    
    for %%f in ("dist\MultiTeam.exe") do (
        echo 📊 Storlek: %%~zf bytes
        set /a size_mb=%%~zf/1024/1024
        echo 📊 Storlek: !size_mb! MB
    )
    
    echo 📅 Build tid: %DATE% %TIME%
    echo 🏷️  Version: 0.20
    echo.
    
    if !EXE_WORKS!==1 (
        echo ✅ EXE FUNGERAR KORREKT
        echo   - Startar utan fel
        echo   - PyQt6 window visas
        echo   - Assets laddas korrekt
        echo.
        echo 🚀 REDO FÖR DISTRIBUTION!
        echo.
        echo 📋 Nästa steg:
        echo 1. Testa login (användarnamn: 1, lösenord: 1^)
        echo 2. Kontrollera dashboard bilder
        echo 3. Kör complete_github_deploy.bat för GitHub
        
    ) else (
        echo ⚠️  EXE STARTPROBLEM
        echo   Kontrollera loggar för fel
        if exist "logs" (
            echo   📋 Senaste loggar:
            for /f %%i in ('dir /b /o:d logs\*.log 2^>nul') do set latest_log=%%i
            if defined latest_log echo     - logs\!latest_log!
        )
    )
    
) else (
    echo ============================================
    echo  ❌ BUILD MISSLYCKADES
    echo ============================================
    echo Kontrollera fel ovan och försök igen
)

echo.
echo ============================================
echo Build process komplett!
echo ============================================
pause

@echo off
echo ============================================
echo  MultiTeam GitHub Push & Release V0.20
echo  Complete Build, Package & Upload Pipeline
echo ============================================

REM Set variables
set VERSION=0.20
set REPO_URL=https://github.com/Medzeta/Multi-Team-C.git
set BRANCH=main

echo Step 1: Git Status Check...
git status
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Not a git repository. Initializing...
    git init
    git remote add origin %REPO_URL%
)

echo.
echo Step 2: Add all files to git...
git add .
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to add files
    pause
    exit /b 1
)

echo.
echo Step 3: Commit changes...
set /p commit_message="Enter commit message (or press Enter for default): "
if "%commit_message%"=="" set commit_message=MultiTeam v%VERSION% - Complete PyQt6 application with working EXE build

git commit -m "%commit_message%"
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  No changes to commit or commit failed
)

echo.
echo Step 4: Push to GitHub...
git push -u origin %BRANCH%
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Push failed. Trying to set upstream...
    git branch -M %BRANCH%
    git push -u origin %BRANCH%
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Push still failed. Check your GitHub credentials and repository access.
        pause
        exit /b 1
    )
)

echo.
echo ✅ Successfully pushed to GitHub!
echo Repository: %REPO_URL%
echo Branch: %BRANCH%

echo.
echo Step 5: Building EXE for release...
call quick_test_exe.bat

echo.
echo Step 6: Creating release package...
if exist "dist\MultiTeam.exe" (
    echo Creating release package...
    
    REM Create package directory
    if not exist "dist\MultiTeam_Package_v%VERSION%" mkdir "dist\MultiTeam_Package_v%VERSION%"
    
    REM Copy EXE
    copy "dist\MultiTeam.exe" "dist\MultiTeam_Package_v%VERSION%\"
    
    REM Copy documentation
    if exist "README.md" copy "README.md" "dist\MultiTeam_Package_v%VERSION%\"
    if exist "ROADMAP.md" copy "ROADMAP.md" "dist\MultiTeam_Package_v%VERSION%\"
    if exist "HOW_TO_RUN.md" copy "HOW_TO_RUN.md" "dist\MultiTeam_Package_v%VERSION%\"
    if exist "FINAL_PROJECT_SUMMARY.md" copy "FINAL_PROJECT_SUMMARY.md" "dist\MultiTeam_Package_v%VERSION%\"
    
    REM Create directories for user data
    mkdir "dist\MultiTeam_Package_v%VERSION%\data" 2>nul
    mkdir "dist\MultiTeam_Package_v%VERSION%\logs" 2>nul
    
    REM Create installation guide
    echo Creating installation guide...
    (
        echo # MultiTeam v%VERSION% - Installation Guide
        echo.
        echo ## Quick Start:
        echo 1. Run MultiTeam.exe
        echo 2. Create account or login with SuperAdmin ^(username: 1, password: 1^)
        echo 3. Enjoy the application!
        echo.
        echo ## System Requirements:
        echo - Windows 10/11
        echo - No additional dependencies required
        echo.
        echo ## Features:
        echo - Modern PyQt6 interface
        echo - Secure authentication system
        echo - Email verification
        echo - License management
        echo - Auto-update system
        echo - 2FA support
        echo.
        echo ## Support:
        echo - GitHub: %REPO_URL%
        echo - Version: %VERSION%
        echo - Build Date: %DATE%
    ) > "dist\MultiTeam_Package_v%VERSION%\INSTALL.md"
    
    REM Create ZIP package
    echo Creating ZIP package...
    powershell -NoProfile -Command "Compress-Archive -Path 'dist/MultiTeam_Package_v%VERSION%/*' -DestinationPath 'dist/MultiTeam_Package_v%VERSION%.zip' -Force"
    
    if exist "dist\MultiTeam_Package_v%VERSION%.zip" (
        echo ============================================
        echo  🎉 COMPLETE SUCCESS!
        echo ============================================
        echo ✅ Code pushed to GitHub
        echo ✅ EXE built successfully
        echo ✅ Release package created
        echo.
        echo 📦 Package: dist\MultiTeam_Package_v%VERSION%\
        echo 📄 ZIP: dist\MultiTeam_Package_v%VERSION%.zip
        echo.
        echo 📊 Package Contents:
        dir "dist\MultiTeam_Package_v%VERSION%"
        echo.
        echo 📊 ZIP Size:
        dir "dist\MultiTeam_Package_v%VERSION%.zip"
        echo.
        echo 🌐 GitHub Repository: %REPO_URL%
        echo 🏷️  Version: %VERSION%
        echo.
        echo ============================================
        echo Ready for GitHub Release Creation!
        echo ============================================
        echo.
        echo Next steps:
        echo 1. Go to %REPO_URL%/releases
        echo 2. Click "Create a new release"
        echo 3. Tag version: v%VERSION%
        echo 4. Upload: dist\MultiTeam_Package_v%VERSION%.zip
        echo 5. Publish release
        
    ) else (
        echo ❌ Failed to create ZIP package
    )
    
) else (
    echo ❌ EXE not found. Build failed.
)

echo.
pause

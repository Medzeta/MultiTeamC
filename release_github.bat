@echo off
setlocal ENABLEDELAYEDEXPANSION

REM ============================================================
REM MultiTeam - Release Publisher (Windows Batch)
REM Builds, packages, and publishes a GitHub release with assets
REM ============================================================

REM 1) CONFIG: You can pass VERSION as first arg or set env VAR VERSION
REM Required env vars if using API fallback (no gh): GH_OWNER, GH_REPO, GH_TOKEN
REM Optional: RELEASE_NAME, RELEASE_NOTES_FILE

if not "%~1"=="" set VERSION=%~1%
if "%VERSION%"=="" set VERSION=0.20

set ZIP_NAME=MultiTeam_Package_v%VERSION%.zip
set ZIP_PATH=dist\%ZIP_NAME%

set RELEASE_TAG=v%VERSION%
if "%RELEASE_NAME%"=="" set RELEASE_NAME=MultiTeam %VERSION%

REM 2) Pre-flight checks
where python >nul 2>&1 || (
  echo [ERROR] Python not found in PATH. Install Python 3.x and try again.
  exit /b 1
)

REM 3) Build EXE and Package
python build_exe.py || (
  echo [ERROR] Build failed.
  exit /b 1
)

if not exist dist\MultiTeam_Package (
  echo [ERROR] dist\MultiTeam_Package not found after build.
  exit /b 1
)

REM 4) Create ZIP artifact
if exist "%ZIP_PATH%" del /q "%ZIP_PATH%"

powershell -NoLogo -NoProfile -Command "Compress-Archive -Path 'dist/MultiTeam_Package/*' -DestinationPath '%ZIP_PATH%' -Force" || (
  echo [ERROR] Failed to create ZIP archive.
  exit /b 1
)

echo [INFO] ZIP created: %ZIP_PATH%

REM 5) Try with GitHub CLI first if available and authenticated
where gh >nul 2>&1
if %ERRORLEVEL%==0 (
  echo [INFO] gh CLI found. Checking auth...
  gh auth status >nul 2>&1
  if %ERRORLEVEL%==0 (
    echo [INFO] Publishing release with gh CLI...
    if exist "%RELEASE_NOTES_FILE%" (
      gh release create %RELEASE_TAG% "%ZIP_PATH%" --title "%RELEASE_NAME%" --notes-file "%RELEASE_NOTES_FILE%" || goto :gh_fail
    ) else (
      gh release create %RELEASE_TAG% "%ZIP_PATH%" --title "%RELEASE_NAME%" --notes "Automated release %RELEASE_TAG%" || goto :gh_fail
    )
    echo [SUCCESS] Release published: %RELEASE_TAG%
    goto :done
  ) else (
    echo [WARN] gh CLI not authenticated. Falling back to API...
  )
) else (
  echo [WARN] gh CLI not found. Falling back to API...
)

REM 6) Fallback: Use PowerShell GitHub API
if "%GH_OWNER%"=="" (
  echo [ERROR] GH_OWNER is not set. Example: set GH_OWNER=your-org-or-username
  exit /b 1
)
if "%GH_REPO%"=="" (
  echo [ERROR] GH_REPO is not set. Example: set GH_REPO=your-repo
  exit /b 1
)
if "%GH_TOKEN%"=="" (
  echo [ERROR] GH_TOKEN is not set. Create a PAT with repo scope and set GH_TOKEN.
  exit /b 1
)

powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File "scripts\\upload_release.ps1" -Owner "%GH_OWNER%" -Repo "%GH_REPO%" -Token "%GH_TOKEN%" -Tag "%RELEASE_TAG%" -Title "%RELEASE_NAME%" -ZipPath "%ZIP_PATH%" -NotesFile "%RELEASE_NOTES_FILE%"
if %ERRORLEVEL% NEQ 0 (
  echo [ERROR] API upload failed.
  exit /b 1
)

goto :done

:gh_fail
echo [ERROR] gh CLI failed to publish the release.
echo         Falling back to API or fix gh auth via: gh auth login
exit /b 1

:done
echo.
echo ==============================================
echo   Release complete: %RELEASE_TAG%
echo   Asset: %ZIP_PATH%
echo ==============================================
exit /b 0

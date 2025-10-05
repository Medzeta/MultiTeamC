# MultiTeam – GitHub Release & Auto-Update Push Guide

This guide explains how to publish new versions to GitHub so client updaters can fetch and install them.

## Overview
- Build and package with `build_exe.py` (PyInstaller + package folder).
- Zip the package and publish a GitHub Release with `release_github.bat`.
- Clients can check GitHub Releases API to detect new versions (client-side integration described below).

## Prerequisites
- Windows 10/11 with PowerShell and Python 3.x in PATH
- GitHub account and repository for MultiTeam
- Option A (recommended): GitHub CLI (`gh`) installed and authenticated
- Option B: GitHub Personal Access Token (PAT) with `repo` scope for API upload

## Repository Setup
1. Create/choose a repository, e.g. `https://github.com/<owner>/<repo>`
2. Push your codebase to the repo (including these scripts):
   - `build_exe.py`
   - `release_github.bat`
   - `scripts/upload_release.ps1`

## Authentication Options
### A) GitHub CLI (gh)
- Install: https://cli.github.com/
- Login: `gh auth login` and follow prompts (HTTPS auth is fine)
- Verify: `gh auth status`

### B) GitHub Personal Access Token (PAT)
- Create PAT: https://github.com/settings/tokens (Fine-grained or classic)
- Scope: `repo` (read/write to releases)
- Save the token as an environment variable: `setx GH_TOKEN <YOUR_TOKEN>`
- Also set:
  - `setx GH_OWNER <your-username-or-org>`
  - `setx GH_REPO <your-repo>`
  - (Optional) `setx RELEASE_NOTES_FILE C:\path\to\notes.md`

Re-open your terminal to load new env vars.

## How to Publish a Release
1. Open a Developer Command Prompt or PowerShell in the repo root.
2. Optionally set a semantic version (recommended):
   - Example: `set VERSION=1.0.0`
3. Run the release script:
   - If passing version as an argument: `release_github.bat 1.0.0`
   - Or rely on env var VERSION: `release_github.bat`
4. The script will:
   - Run `python build_exe.py` (clean, build exe, build package)
   - Zip `dist/MultiTeam_Package` → `dist/MultiTeam_Package_v<version>.zip`
   - Create a GitHub Release tagged `v<version>` and upload the asset
     - With gh CLI if available, otherwise with PowerShell GitHub API using PAT

Artifacts:
- Executable: `dist/MultiTeam_Package/MultiTeam.exe`
- ZIP for release: `dist/MultiTeam_Package_v<version>.zip`

## Script Reference
- `release_github.bat` accepts:
  - Arg1: `VERSION` (optional). If missing, auto-generates timestamped version.
  - Env: `RELEASE_NAME`, `RELEASE_NOTES_FILE` (optional)
  - Fallback API env: `GH_OWNER`, `GH_REPO`, `GH_TOKEN`
- `scripts/upload_release.ps1` (API fallback) parameters:
  - `-Owner`, `-Repo`, `-Token`, `-Tag`, `-Title`, `-ZipPath`, `-NotesFile`

## Recommended Versioning
- Use Semantic Versioning: `MAJOR.MINOR.PATCH` (e.g. 1.2.3)
- Tag format: `v<version>` (script does this automatically)

## Client Auto-Update Integration (Next Step)
To make clients automatically detect and download new releases:
1. Store current app version in code (e.g. `core/version.py` → `APP_VERSION = "1.0.0"`).
2. Check latest release via GitHub API:
   - `GET https://api.github.com/repos/<owner>/<repo>/releases/latest`
3. Compare `tag_name` (e.g. `v1.0.1`) vs local `APP_VERSION`.
4. If newer, download the ZIP asset URL from `assets[0].browser_download_url`.
5. Verify checksum/signature (optional but recommended).
6. Extract and run an in-app updater/installer, or prompt the user.

(We can implement a Python auto-updater module that does steps 2–6.)

## Security Notes
- Never hardcode tokens in code. Use env vars or GitHub CLI auth.
- PAT should be least-privilege and rotated regularly.
- For enterprise, consider signed releases and checksum verification.

## Troubleshooting
- gh not found: install GitHub CLI or use PAT fallback
- Auth failed with gh: run `gh auth login`
- 401/403 in API fallback: verify `GH_TOKEN` scope and repo access
- ZIP missing: ensure `build_exe.py` succeeds and creates `dist/MultiTeam_Package`

## Quick Commands
- `gh auth login`
- `setx GH_OWNER your-username`
- `setx GH_REPO your-repo`
- `setx GH_TOKEN your_pat_here`
- `release_github.bat 1.0.0`

---

© 2025 MultiTeam. All rights reserved.

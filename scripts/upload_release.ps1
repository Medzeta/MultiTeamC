param(
    [Parameter(Mandatory=$true)] [string]$Owner,
    [Parameter(Mandatory=$true)] [string]$Repo,
    [Parameter(Mandatory=$true)] [string]$Token,
    [Parameter(Mandatory=$true)] [string]$Tag,
    [Parameter(Mandatory=$true)] [string]$Title,
    [Parameter(Mandatory=$true)] [string]$ZipPath,
    [Parameter(Mandatory=$false)] [string]$NotesFile
)

# Fail on error
$ErrorActionPreference = 'Stop'

Write-Host "[INFO] Using GitHub API fallback to create release $Tag on $Owner/$Repo" -ForegroundColor Cyan

if (!(Test-Path -Path $ZipPath)) {
    Write-Error "ZIP not found: $ZipPath"
}

$notes = "Automated release $Tag"
if ($NotesFile -and (Test-Path -Path $NotesFile)) {
    $notes = Get-Content -Path $NotesFile -Raw
}

$headers = @{
    Authorization = "Bearer $Token"
    'User-Agent'  = 'MultiTeam-Release-Script'
    Accept        = 'application/vnd.github+json'
}

# 1) Create or get release
$releaseBody = @{ tag_name = $Tag; name = $Title; body = $notes; draft = $false; prerelease = $false } | ConvertTo-Json
$createUri = "https://api.github.com/repos/$Owner/$Repo/releases"

try {
    $release = Invoke-RestMethod -Method POST -Uri $createUri -Headers $headers -Body $releaseBody
} catch {
    # If already exists, GET it
    Write-Warning "Create failed, trying to fetch existing release (maybe tag exists). $_"
    $getUri = "https://api.github.com/repos/$Owner/$Repo/releases/tags/$Tag"
    $release = Invoke-RestMethod -Method GET -Uri $getUri -Headers $headers
}

if (-not $release.upload_url) { Write-Error "Upload URL not found in release response" }

# 2) Upload asset
$uploadUrl = $release.upload_url -replace '{\?name,label}', ''
$assetName = [System.IO.Path]::GetFileName($ZipPath)
$uploadWithParams = "$uploadUrl?name=$([uri]::EscapeDataString($assetName))"

Write-Host "[INFO] Uploading asset: $assetName" -ForegroundColor Cyan

$bin = [System.IO.File]::ReadAllBytes((Resolve-Path $ZipPath))
$uploadHeaders = @{
    Authorization = "Bearer $Token"
    'User-Agent'  = 'MultiTeam-Release-Script'
    Accept        = 'application/vnd.github+json'
    'Content-Type' = 'application/zip'
}

$asset = Invoke-RestMethod -Method POST -Uri $uploadWithParams -Headers $uploadHeaders -Body $bin

Write-Host "[SUCCESS] Release published and asset uploaded: $assetName" -ForegroundColor Green

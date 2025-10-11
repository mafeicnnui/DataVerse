Param(
  [int]$Port = 8001,
  [string]$AppDir = 'backend',
  [string]$DatabaseUrl = ''
)

$ErrorActionPreference = 'Stop'

if ($DatabaseUrl) {
  $env:DATABASE_URL = $DatabaseUrl
}

Write-Host "[start_backend.ps1] Using port: $Port, app dir: $AppDir"

$cmd = "uvicorn app.main:app --reload --host 0.0.0.0 --port $Port --app-dir $AppDir"
Write-Host "[start_backend.ps1] Starting: $cmd"
& cmd /c $cmd

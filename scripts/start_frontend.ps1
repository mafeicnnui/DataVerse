param(
  [int]$DevPort = 5173,
  [int]$BackendPort,
  [switch]$Force,
  [string]$ListenHost = '0.0.0.0'
)

$ErrorActionPreference = 'SilentlyContinue'

function Write-Log($msg) { Write-Host "[start_frontend] $msg" }

# Resolve paths
$root = Split-Path -Parent $PSScriptRoot
$frontendDir = Join-Path $root 'frontend'
$scanPs1 = Join-Path $PSScriptRoot 'scan_port.ps1'

if (-not (Test-Path $frontendDir)) {
  Write-Log "[ERROR] frontend directory not found: $frontendDir"
  exit 1
}

Write-Host '================================'
Write-Log ("Target dev port: {0}" -f $DevPort)
Write-Log ("Listen host: {0}" -f $ListenHost)
if ($Force) { Write-Log "[WARN] --force enabled: will kill any process on :$DevPort" }
Write-Host '================================'

# 1) Scan listeners
Write-Log ("Scanning listeners on port {0} ..." -f $DevPort)
try {
  & powershell -NoProfile -ExecutionPolicy Bypass -File $scanPs1 -Port $DevPort -Format | Write-Output
} catch {}

# 2) Safe release
$kmode = if ($Force) { 'all' } else { 'safe' }
Write-Log ("Releasing port {0} ({1} mode)..." -f $DevPort, $kmode)
try {
  if ($Force) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File $scanPs1 -Port $DevPort -Kill all -Format | Write-Output
  } else {
    & powershell -NoProfile -ExecutionPolicy Bypass -File $scanPs1 -Port $DevPort -Kill safe -Whitelist 'node.exe' -OnlyCurrentUser -Format | Write-Output
  }
} catch {}

# 3) Optionally update Vite proxy target
Set-Location $frontendDir
if ($BackendPort) {
  $vite = Join-Path $frontendDir 'vite.config.js'
  if (Test-Path $vite) {
    if (-not (Test-Path "$vite.bak")) { Copy-Item $vite "$vite.bak" -Force }
    # 若 ListenHost 为具体 IP（且不是 0.0.0.0），优先使用该 IP 作为代理目标主机；否则使用 127.0.0.1
    $ipRegex = '^(?:\d{1,3}\.){3}\d{1,3}$'
    $proxyHost = if ($ListenHost -and $ListenHost -ne '0.0.0.0' -and ($ListenHost -match $ipRegex)) { $ListenHost } else { '127.0.0.1' }
    Write-Log ("Updating proxy target to http://{0}:{1}" -f $proxyHost, $BackendPort)
    try {
      $c = Get-Content $vite -Raw
      # 统一替换 127.0.0.1 或任何已有 http://x.x.x.x:port
      $n = $c -replace "target:\s*'http://[^']+'", ("target: 'http://{0}:{1}'" -f $proxyHost, $BackendPort)
      if ($c -ne $n) {
        Set-Content -Path $vite -Value $n -NoNewline
        Write-Log 'vite.config.js updated.'
      } else {
        Write-Log 'proxy target unchanged.'
      }
    } catch {
      Write-Log "[WARN] failed to update vite.config.js: $($_.Exception.Message)"
    }
  } else {
    Write-Log 'vite.config.js not found; skip proxy update.'
  }
}

# 4) Install dependencies if node_modules missing (quiet unless error)
if (-not (Test-Path 'node_modules')) {
  Write-Log 'Installing npm dependencies ...'
  $log = Join-Path $env:TEMP ("npm_install_{0}.log" -f (Get-Random))
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = 'cmd.exe'
  $psi.Arguments = '/c npm install --silent --no-fund --no-audit'
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError = $true
  $psi.UseShellExecute = $false
  $p = [System.Diagnostics.Process]::Start($psi)
  $out = $p.StandardOutput.ReadToEnd() + $p.StandardError.ReadToEnd()
  $p.WaitForExit()
  if ($p.ExitCode -ne 0) {
    Write-Log '[ERROR] npm install failed. See log below:'
    $out | Tee-Object -FilePath $log | Write-Host
    exit 1
  }
}

# 5) Start Vite dev server
Write-Log ("Starting: npm run dev -- --host {0} --port {1}" -f $ListenHost, $DevPort)
$env:PORT = $DevPort
& cmd.exe /c "npm run dev -- --host $ListenHost --port $DevPort"

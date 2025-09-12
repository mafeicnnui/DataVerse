param(
    [Parameter(Mandatory=$true)][int]$Port,
    [switch]$Format,
    [ValidateSet('none','safe','all')][string]$Kill = 'none',
    [string[]]$Whitelist = @(),
    [switch]$OnlyCurrentUser
)

$ErrorActionPreference = 'SilentlyContinue'

# Try modern API first
$pids = @()
try {
    $pids = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction Stop | Select-Object -ExpandProperty OwningProcess
} catch {
    $pids = @()
}

if (-not $pids -or $pids.Count -eq 0) {
    # Fallback to netstat parsing
    $lines = netstat -ano | Select-String -SimpleMatch (":"+$Port+" ") | Where-Object { $_.Line -match 'LISTENING' }
    foreach ($l in $lines) {
        if ($l.Line -match '\s(\d+)$') { $pids += $matches[1] }
    }
}

$pids = $pids | Sort-Object -Unique

# Build objects with details
$procs = @()
foreach ($pid in $pids) {
    $img = 'unknown.exe'
    try { $img = ((Get-Process -Id $pid -ErrorAction Stop).ProcessName + '.exe') } catch {}

    $usr = 'UNKNOWN'
    try {
        $owner = (Get-CimInstance Win32_Process -Filter "ProcessId=$pid").GetOwner()
        if ($owner -and $owner.User) { $usr = $owner.User }
    } catch {}

    $procs += [pscustomobject]@{ PID=$pid; Image=$img; User=$usr }
}

# Print listing first (if requested)
foreach ($p in $procs) {
    if ($Format) {
        Write-Output ('  - PID ' + $p.PID + ' Image="' + $p.Image + '" User="' + $p.User + '"')
    } else {
        Write-Output ($p.PID.ToString() + "`t" + $p.Image + "`t" + $p.User)
    }
}

# Perform killing if requested
if ($Kill -ne 'none') {
    $me = $env:USERNAME
    foreach ($p in $procs) {
        $ok = $false
        if ($Kill -eq 'all') {
            $ok = $true
        } elseif ($Kill -eq 'safe') {
            $wh = $false
            if ($Whitelist -and $Whitelist.Count -gt 0) {
                foreach ($w in $Whitelist) { if ($p.Image -ieq $w) { $wh = $true; break } }
            }
            $usrOk = (-not $OnlyCurrentUser) -or ($p.User -ieq $me)
            if ($wh -and $usrOk) { $ok = $true }
        }
        if ($ok) {
            $status = 'killed'
            try { Stop-Process -Id $p.PID -Force -ErrorAction Stop } catch { $status = 'failed' }
            Write-Output ('[kill] ' + $status + ' PID ' + $p.PID + ' Image="' + $p.Image + '" User="' + $p.User + '"')
        } else {
            Write-Output ('[kill] skipped PID ' + $p.PID + ' Image="' + $p.Image + '" User="' + $p.User + '"')
        }
    }
}

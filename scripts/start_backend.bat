@echo off
setlocal enabledelayedexpansion

REM start_backend.bat - safe port handling; args: [PORT] [APP_DIR] [DATABASE_URL] [--force]

REM Normalize codepage to UTF-8 (avoid mojibake); safe if already UTF-8
chcp 65001 >NUL 2>&1

set PORT=%~1
if "%PORT%"=="" set PORT=8000

set APP_DIR=%~2
if "%APP_DIR%"=="" set APP_DIR=backend

set DBURL=%~3
if not "%DBURL%"=="" set "DATABASE_URL=%DBURL%"

set FORCE_FLAG=%~4
set SAFE_KILL=1
if /I "%FORCE_FLAG%"=="--force" (
  set SAFE_KILL=0
)

echo ================================================
echo [start_backend] Target port: %PORT%
echo [start_backend] App dir:    %APP_DIR%
if not "%DBURL%"=="" (
  echo [start_backend] DATABASE_URL is set
) else (
  echo [start_backend] DATABASE_URL: using default from app/core/config.py
)
if %SAFE_KILL%==0 (
  echo [start_backend][WARN] --force enabled: will kill any process on :%PORT%
)
echo ================================================

REM 1) Detect listeners on the target port (no kill in this step)
echo [start_backend] Scanning listeners on port %PORT% ...
set "_FOUND=0"
set "_PIDLIST=%TEMP%\pids_%PORT%_%RANDOM%.txt"
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\scan_port.ps1" -Port %PORT% -Format > "%_PIDLIST%"
if not exist "%_PIDLIST%" goto SCAN_NOFILE
for %%F in ("%_PIDLIST%") do set "_SIZE=%%~zF"
if "%_SIZE%"=="" set "_SIZE=0"
if %_SIZE%==0 goto SCAN_EMPTY
type "%_PIDLIST%"
set "_FOUND=1"
echo [start_backend] Above processes are listening on :%PORT% (no kill performed).
del /f /q "%_PIDLIST%" >NUL 2>&1
goto SCAN_DONE

:SCAN_EMPTY
echo [start_backend] Port %PORT% has no LISTENING process.
del /f /q "%_PIDLIST%" >NUL 2>&1
goto SCAN_DONE

:SCAN_NOFILE
echo [start_backend][WARN] PID list file not created, skipping process display.
goto SCAN_DONE

:SCAN_DONE

REM 2) Prepare venv
REM Safe release port (kill only whitelisted current-user processes unless --force)
echo [start_backend] Releasing port %PORT% (safe mode; use --force to override)...
set "KMODE=safe"
if "%SAFE_KILL%"=="0" set "KMODE=all"
set "_KRES=%TEMP%\kill_%PORT%_%RANDOM%.txt"
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\scan_port.ps1" -Port %PORT% -Kill %KMODE% -Whitelist "python.exe","uvicorn.exe" -OnlyCurrentUser -Format > "%_KRES%"
if exist "%_KRES%" type "%_KRES%"
del /f /q "%_KRES%" >NUL 2>&1

REM Proceed to environment setup
if not exist .venv\Scripts\activate.bat (
  echo [start_backend] Creating virtual environment .venv ...
  py -3 -m venv .venv || (
    echo [start_backend][ERROR] Failed to create venv. Ensure Python is installed and in PATH.
    exit /b 1
  )
)

call .venv\Scripts\activate.bat || (
  echo [start_backend][ERROR] Failed to activate venv.
  exit /b 1
)

REM 3) Install backend requirements (idempotent)
echo [start_backend] Installing dependencies ...
set "_PIPLOG=%TEMP%\pip_install_%RANDOM%.log"
pip install -r backend\requirements.txt > "%_PIPLOG%" 2>&1
if errorlevel 1 (
  echo [start_backend][ERROR] pip install failed. See log below:
  type "%_PIPLOG%"
  del /f /q "%_PIPLOG%" >NUL 2>&1
  exit /b 1
) else (
  del /f /q "%_PIPLOG%" >NUL 2>&1
)

REM 4) Start backend (listen on all interfaces for LAN/IP access)
set UVICORN_CMD=uvicorn app.main:app --reload --host 0.0.0.0 --port %PORT% --app-dir %APP_DIR%
echo [start_backend] Starting: %UVICORN_CMD%
%UVICORN_CMD%

endlocal

REM --------------------------------------------------
REM Helper: PRINT_PROCESS_INFO <PID> <PORT>
:PRINT_PROCESS_INFO
setlocal enabledelayedexpansion
set "_PID=%~1"
set "_PORT=%~2"

REM Query process name and owner via PowerShell (locale-agnostic)
for /f "usebackq delims=" %%I in (`powershell -NoProfile -Command "try{(Get-Process -Id %_PID% -ErrorAction Stop).ProcessName}catch{}"`) do set "IMG=%%I"
if not defined IMG set "IMG=unknown"
set "IMG=%IMG%.exe"

for /f "usebackq delims=" %%I in (`powershell -NoProfile -Command "try{(Get-CimInstance Win32_Process -Filter 'ProcessId=%_PID%').GetOwner().User}catch{}"`) do set "USR=%%I"
if not defined USR set "USR=UNKNOWN"

echo   - PID %_PID% Image="!IMG!" User="!USR!" on :%_PORT%
endlocal & exit /b 0


@echo off
setlocal
set "DEV_PORT=%~1"
if "%DEV_PORT%"=="" set "DEV_PORT=5173"
set "BACKEND_PORT=%~2"
set "FORCE_FLAG=%~3"
set "HOST_ARG=%~4"
if "%HOST_ARG%"=="" set "HOST_ARG=0.0.0.0"
set "PS1=%~dp0start_frontend.ps1"

if "%BACKEND_PORT%"=="" (
  if /I "%FORCE_FLAG%"=="--force" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" -DevPort %DEV_PORT% -ListenHost "%HOST_ARG%" -Force
  ) else (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" -DevPort %DEV_PORT% -ListenHost "%HOST_ARG%"
  )
) else (
  if /I "%FORCE_FLAG%"=="--force" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" -DevPort %DEV_PORT% -BackendPort %BACKEND_PORT% -ListenHost "%HOST_ARG%" -Force
  ) else (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" -DevPort %DEV_PORT% -BackendPort %BACKEND_PORT% -ListenHost "%HOST_ARG%"
  )
)

endlocal


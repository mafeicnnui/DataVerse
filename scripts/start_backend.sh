#!/usr/bin/env bash
set -euo pipefail

# Usage: scripts/start_backend.sh [PORT] [APP_DIR] [--force]
# Defaults
PORT="${1:-8001}"
APP_DIR="${2:-backend}"
FORCE="${3:-}"

log(){ echo -e "[backend] $*"; }

# Find listener on port
find_pid(){
  lsof -iTCP -sTCP:LISTEN -nP 2>/dev/null | awk -v p=":$PORT" '$9 ~ p {print $2" "$1}' | sort -u
}

kill_safe(){
  local pid="$1" exe="$2"
  if [[ "$FORCE" == "--force" ]]; then
    kill -9 "$pid" || true; return
  fi
  case "$exe" in
    python*|uvicorn*) kill "$pid" || true;;
    *) log "Refuse to kill process $pid ($exe) on port $PORT. Use --force if you are sure."; exit 2;;
  esac
}

# Stop existing listener(s)
PIDS=$(find_pid || true)
if [[ -n "${PIDS}" ]]; then
  while read -r pid exe; do
    [[ -z "$pid" ]] && continue
    log "Killing $pid ($exe) on :$PORT"
    kill_safe "$pid" "$exe"
    sleep 0.3
  done <<< "$PIDS"
fi

# Create/activate venv（容错：无 python3 时回退 python；创建失败则跳过）
create_venv(){
  if command -v python3 >/dev/null 2>&1; then
    python3 -m venv .venv || true
  elif command -v python >/dev/null 2>&1; then
    python -m venv .venv || true
  fi
}
if [[ ! -d .venv ]]; then
  log "Creating venv (.venv)"
  create_venv
fi
if [[ -f .venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
else
  log "WARN: venv not available, continue with system Python"
fi

# Install requirements if uvicorn missing（pip/pip3 兼容）
if ! command -v uvicorn >/dev/null 2>&1; then
  log "Installing backend requirements"
  if command -v pip >/dev/null 2>&1; then pip install -r "$APP_DIR/requirements.txt"; else pip3 install -r "$APP_DIR/requirements.txt"; fi
fi

# Start backend
export PYTHONUNBUFFERED=1
log "Starting uvicorn on :$PORT (app-dir=$APP_DIR)"
exec uvicorn app.main:app --reload --port "$PORT" --app-dir "$APP_DIR"

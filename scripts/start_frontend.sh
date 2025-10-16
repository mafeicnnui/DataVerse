#!/usr/bin/env bash
set -euo pipefail

# Usage: scripts/start_frontend.sh [DEV_PORT] [BACKEND_PORT] [--force] [HOST]
DEV_PORT="${1:-5173}"
BACKEND_PORT="${2:-8001}"
FORCE="${3:-}"
HOST="${4:-0.0.0.0}"

log(){ echo -e "[frontend] $*"; }

cd "$(dirname "$0")/.."

# Update vite proxy target if vite.config.js 存在
VITE=frontend/vite.config.js
if [[ -f "$VITE" ]]; then
  cp -f "$VITE" "$VITE.bak" || true
  sed -E -i "s#(target:\s*')[^']*('#)#\1http://127.0.0.1:$BACKEND_PORT\2#g" "$VITE" || true
  sed -E -i "s#(target:\s*")([^"]*)(")#\1http://127.0.0.1:$BACKEND_PORT\3#g" "$VITE" || true
  log "Proxy set to http://127.0.0.1:$BACKEND_PORT"
fi

# Kill node on the port (safe)
find_pid(){
  lsof -iTCP -sTCP:LISTEN -nP 2>/dev/null | awk -v p=":$DEV_PORT" '$9 ~ p {print $2" "$1}' | sort -u
}
kill_safe(){
  local pid="$1" exe="$2"
  if [[ "$FORCE" == "--force" ]]; then kill -9 "$pid" || true; return; fi
  case "$exe" in
    node*) kill "$pid" || true;;
    *) log "Refuse to kill $pid ($exe) on :$DEV_PORT. Use --force if sure."; exit 2;;
  esac
}
PIDS=$(find_pid || true)
if [[ -n "${PIDS}" ]]; then
  while read -r pid exe; do
    [[ -z "$pid" ]] && continue
    log "Killing $pid ($exe) on :$DEV_PORT"
    kill_safe "$pid" "$exe"
    sleep 0.3
  done <<< "$PIDS"
fi

# Install deps if needed and start
cd frontend
if [[ ! -d node_modules ]]; then
  log "Installing npm deps"
  npm ci || npm install
fi

export HOST
log "Starting Vite on $HOST:$DEV_PORT"
exec npm run dev -- --host "$HOST" --port "$DEV_PORT"

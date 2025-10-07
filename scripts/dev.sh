#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Start calc (4001), policy (8001), teambuilder (8002)

# Calc
( cd "$ROOT_DIR/services/calc" && npm run build && node dist/index.js ) &
CALC_PID=$!

# Policy
( cd "$ROOT_DIR/services/policy" && uvicorn app.main:app --host 0.0.0.0 --port 8001 ) &
POLICY_PID=$!

# Teambuilder
( cd "$ROOT_DIR/services/teambuilder" && uvicorn app.main:app --host 0.0.0.0 --port 8002 ) &
TEAM_PID=$!

cleanup() {
  echo "Shutting down..."
  kill $CALC_PID $POLICY_PID $TEAM_PID 2>/dev/null || true
}
trap cleanup EXIT

wait

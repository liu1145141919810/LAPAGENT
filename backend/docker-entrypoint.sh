#!/usr/bin/env sh
set -eu

HOST="${LAPAGENT_HOST:-0.0.0.0}"
PORT="${LAPAGENT_PORT:-8000}"
ENV_MODE="${LAPAGENT_ENV:-production}"
RELOAD="${LAPAGENT_RELOAD:-false}"

if [ "$ENV_MODE" = "development" ] || [ "$RELOAD" = "true" ]; then
  exec uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
else
  exec uvicorn app.main:app --host "$HOST" --port "$PORT"
fi

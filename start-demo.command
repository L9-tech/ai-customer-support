#!/bin/zsh
cd "${0:A:h}"
export APP_MODE=demo
export DASHBOARD_USERNAME=admin
export DASHBOARD_PASSWORD=demo-local
exec "$HOME/.local/bin/uv" run uvicorn app.main:app --host 127.0.0.1 --port 8080

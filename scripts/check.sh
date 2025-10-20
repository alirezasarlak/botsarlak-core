#!/bin/bash
set -e
BASE="$(cd $(dirname "$0")/.. && pwd)"
source "$BASE/venv/bin/activate" || true
pip show python-telegram-bot | grep "Version: 22.5" || echo "⚠️ PTB version mismatch"
psql -h 127.0.0.1 -U sarlak_user -d sarlak_db -c "SELECT 1" -w || echo "⚠️ DB connection failed"
[ -f "$BASE/.env" ] || echo "⚠️ .env missing"
systemctl is-active sarlakbot >/dev/null && echo "✅ service active" || echo "⚠️ service not active"

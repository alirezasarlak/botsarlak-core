#!/bin/bash
set -e
BASE="$(cd $(dirname "$0")/.. && pwd)"
sudo cp "$BASE/systemd.service" /etc/systemd/system/sarlakbot.service
sudo systemctl daemon-reload
sudo systemctl restart sarlakbot
sudo systemctl enable sarlakbot
echo "✅ Deployed."

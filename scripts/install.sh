#!/bin/bash
set -e
cd $(dirname "$0")/..
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python main.py || true
echo "✅ Install finished. Configure .env then run deploy.sh"

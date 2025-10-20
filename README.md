# Sarlak Academy Telegram Bot — v6.1 Ultimate

## Quick Deploy
```bash
sudo mkdir -p /home/ali/sarlakbot && sudo chown -R ali:ali /home/ali/sarlakbot
# Upload ZIP, then:
cd /home/ali/sarlakbot
unzip SarlakBot_v6_Full.zip
bash scripts/install.sh
cp .env.example .env && nano .env   # fill BOT_TOKEN, ADMIN_ID, DB creds
bash scripts/deploy.sh
journalctl -u sarlakbot -f
```
Run a ping:
```bash
source venv/bin/activate
python scripts/smoke_test.py
```

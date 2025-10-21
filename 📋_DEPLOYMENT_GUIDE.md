# 📋 Sarlak Academy Bot - Complete Deployment Guide

> **🚀 Ready-to-use deployment guide with all credentials configured**

## 🎯 Quick Start (Recommended)

### Option 1: One-Click Deployment
```bash
# Make sure you're in the project directory
cd /Users/alireza/Desktop/botsarlak_v2_clean

# Run the complete deployment script
./🚀_DEPLOY_COMPLETE.sh
```

**That's it!** The script will handle everything automatically.

---

## 🔧 Manual Step-by-Step Deployment

### Step 1: Pre-deployment Setup
```bash
# Navigate to project directory
cd /Users/alireza/Desktop/botsarlak_v2_clean

# Verify you have the main files
ls -la main.py requirements.txt

# Check credentials file exists
ls -la 🔐_CREDENTIALS_SECURE.md
```

### Step 2: Environment Configuration
```bash
# Copy production environment file
cp env.production .env

# Verify .env file has correct credentials
cat .env | grep -E "(BOT_TOKEN|ADMIN_ID|DB_PASSWORD)"
```

### Step 3: File Synchronization
```bash
# Sync files to server (using rsync)
rsync -avz --delete \
    --exclude ".git" \
    --exclude "__pycache__" \
    --exclude ".venv" \
    --exclude "venv" \
    --exclude "*.log" \
    --exclude ".env" \
    --exclude "🔐_CREDENTIALS_SECURE.md" \
    ./ ali@163.5.94.227:/home/ali/botsarlak/
```

### Step 4: Remote Server Setup
```bash
# Connect to server
ssh ali@163.5.94.227

# Navigate to project directory
cd /home/ali/botsarlak

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Database Setup
```bash
# On the server, create database if it doesn't exist
createdb -h localhost -U postgres sarlak_academy

# Run migrations (if Makefile exists)
make migrate
```

### Step 6: Systemd Service Setup
```bash
# Create systemd service file
sudo tee /etc/systemd/system/botsarlak.service > /dev/null << 'EOF'
[Unit]
Description=Sarlak Academy Telegram Bot
After=network.target postgresql.service

[Service]
Type=simple
User=ali
WorkingDirectory=/home/ali/botsarlak
Environment="PATH=/home/ali/botsarlak/.venv/bin"
ExecStart=/home/ali/botsarlak/.venv/bin/python main.py
Restart=always
RestartSec=10

# Logging
StandardOutput=append:/var/log/botsarlak/bot.log
StandardError=append:/var/log/botsarlak/bot_error.log

[Install]
WantedBy=multi-user.target
EOF

# Create log directory
sudo mkdir -p /var/log/botsarlak
sudo chown ali:ali /var/log/botsarlak

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable botsarlak
sudo systemctl start botsarlak
```

### Step 7: Verification
```bash
# Check service status
sudo systemctl status botsarlak

# Check logs
sudo journalctl -u botsarlak -f

# Test health endpoint
curl http://localhost:8080/healthz
```

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Service Won't Start
```bash
# Check detailed logs
sudo journalctl -u botsarlak -n 50

# Check if port is in use
sudo netstat -tlnp | grep :8080

# Restart service
sudo systemctl restart botsarlak
```

#### 2. Database Connection Issues
```bash
# Test database connection
psql -h localhost -U postgres -d sarlak_academy -c "SELECT 1;"

# Check PostgreSQL status
sudo systemctl status postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql
```

#### 3. Permission Issues
```bash
# Fix ownership
sudo chown -R ali:ali /home/ali/botsarlak
sudo chown -R ali:ali /var/log/botsarlak

# Fix permissions
chmod +x main.py
chmod 644 .env
```

#### 4. Dependencies Issues
```bash
# Recreate virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 📊 Monitoring Commands

### Service Management
```bash
# Check status
sudo systemctl status botsarlak

# Start/Stop/Restart
sudo systemctl start botsarlak
sudo systemctl stop botsarlak
sudo systemctl restart botsarlak

# Enable/Disable auto-start
sudo systemctl enable botsarlak
sudo systemctl disable botsarlak
```

### Log Monitoring
```bash
# Real-time logs
sudo journalctl -u botsarlak -f

# Last 50 lines
sudo journalctl -u botsarlak -n 50

# Logs from today
sudo journalctl -u botsarlak --since today

# Application logs
tail -f /var/log/botsarlak/bot.log
```

### Health Checks
```bash
# Health endpoint
curl http://localhost:8080/healthz

# Metrics endpoint
curl http://localhost:8080/metrics

# Database connection test
psql -h localhost -U postgres -d sarlak_academy -c "SELECT COUNT(*) FROM users;"
```

---

## 🔄 Update Process

### Quick Update
```bash
# Run the deployment script again
./🚀_DEPLOY_COMPLETE.sh
```

### Manual Update
```bash
# 1. Sync files
rsync -avz --delete ./ ali@163.5.94.227:/home/ali/botsarlak/

# 2. On server: restart service
ssh ali@163.5.94.227 "sudo systemctl restart botsarlak"
```

---

## 🛡️ Security Notes

### Credentials Management
- ✅ All credentials stored in `🔐_CREDENTIALS_SECURE.md`
- ✅ Production `.env` file created automatically
- ✅ Sensitive files excluded from sync
- ✅ Logs stored in secure location

### Server Security
- ✅ Service runs as non-root user (`ali`)
- ✅ Logs have proper permissions
- ✅ Database credentials secured
- ✅ Bot token protected

---

## 📞 Support Commands

### Quick Status Check
```bash
# All-in-one status check
ssh ali@163.5.94.227 "
    echo '=== Service Status ==='
    sudo systemctl status botsarlak --no-pager | head -10
    echo ''
    echo '=== Health Check ==='
    curl -s http://localhost:8080/healthz || echo 'Health endpoint not responding'
    echo ''
    echo '=== Recent Logs ==='
    sudo journalctl -u botsarlak -n 5 --no-pager
"
```

### Emergency Restart
```bash
# Emergency restart sequence
ssh ali@163.5.94.227 "
    sudo systemctl stop botsarlak
    sleep 5
    sudo systemctl start botsarlak
    sleep 10
    sudo systemctl status botsarlak --no-pager | head -10
"
```

---

## 🎉 Success Indicators

After successful deployment, you should see:

1. ✅ **Service Status**: `Active (running)`
2. ✅ **Health Endpoint**: Returns JSON with status
3. ✅ **Bot Response**: Bot responds to `/start` command
4. ✅ **Logs**: No critical errors in logs
5. ✅ **Database**: Can connect and query tables

---

## 📝 Notes

- **Server**: Ubuntu 20.04 LTS (163.5.94.227)
- **User**: ali
- **Path**: /home/ali/botsarlak
- **Service**: botsarlak
- **Health Port**: 8080
- **Database**: PostgreSQL (sarlak_academy)

**Last Updated**: $(date)
**Version**: 2.2.1-qa-fix




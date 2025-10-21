# 🔧 Sarlak Academy Bot - Troubleshooting Guide

> **Complete troubleshooting guide for common deployment and runtime issues**

## 🚨 Emergency Quick Fixes

### Bot Not Responding
```bash
# Quick restart
ssh ali@163.5.94.227 "sudo systemctl restart botsarlak"

# Check status
ssh ali@163.5.94.227 "sudo systemctl status botsarlak"
```

### Service Won't Start
```bash
# Check logs for errors
ssh ali@163.5.94.227 "sudo journalctl -u botsarlak -n 20"

# Check if port is in use
ssh ali@163.5.94.227 "sudo netstat -tlnp | grep :8080"
```

---

## 🔍 Diagnostic Commands

### System Health Check
```bash
# Complete system check
ssh ali@163.5.94.227 "
    echo '=== SYSTEM STATUS ==='
    echo 'Uptime:' \$(uptime)
    echo 'Disk:' \$(df -h /)
    echo 'Memory:' \$(free -h)
    echo ''
    echo '=== SERVICE STATUS ==='
    sudo systemctl status botsarlak --no-pager | head -15
    echo ''
    echo '=== HEALTH ENDPOINT ==='
    curl -s http://localhost:8080/healthz || echo 'Health endpoint not responding'
    echo ''
    echo '=== RECENT LOGS ==='
    sudo journalctl -u botsarlak -n 10 --no-pager
"
```

### Database Health Check
```bash
# Database connection test
ssh ali@163.5.94.227 "
    echo '=== DATABASE STATUS ==='
    sudo systemctl status postgresql --no-pager | head -10
    echo ''
    echo '=== DATABASE CONNECTION ==='
    psql -h localhost -U postgres -d sarlak_academy -c 'SELECT COUNT(*) as user_count FROM users;' || echo 'Database connection failed'
    echo ''
    echo '=== DATABASE SIZE ==='
    psql -h localhost -U postgres -d sarlak_academy -c 'SELECT pg_size_pretty(pg_database_size(current_database()));'
"
```

---

## 🐛 Common Issues & Solutions

### 1. Service Status: Failed

**Symptoms:**
- `sudo systemctl status botsarlak` shows "Failed"
- Bot not responding to commands

**Diagnosis:**
```bash
# Check detailed error logs
sudo journalctl -u botsarlak -n 50 --no-pager

# Check if Python file exists and is executable
ls -la /home/ali/botsarlak/main.py
```

**Solutions:**
```bash
# Fix 1: Check file permissions
sudo chown -R ali:ali /home/ali/botsarlak
chmod +x /home/ali/botsarlak/main.py

# Fix 2: Recreate virtual environment
cd /home/ali/botsarlak
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Fix 3: Check .env file
cat /home/ali/botsarlak/.env | grep -E "(BOT_TOKEN|ADMIN_ID)"

# Fix 4: Restart service
sudo systemctl restart botsarlak
```

### 2. Database Connection Error

**Symptoms:**
- Logs show "database connection failed"
- Health endpoint returns database error

**Diagnosis:**
```bash
# Test database connection
psql -h localhost -U postgres -d sarlak_academy -c "SELECT 1;"

# Check PostgreSQL status
sudo systemctl status postgresql
```

**Solutions:**
```bash
# Fix 1: Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Fix 2: Check database exists
sudo -u postgres psql -c "\\l" | grep sarlak_academy

# Fix 3: Create database if missing
sudo -u postgres createdb sarlak_academy

# Fix 4: Check user permissions
sudo -u postgres psql -c "\\du" | grep postgres
```

### 3. Bot Token Invalid

**Symptoms:**
- Logs show "Unauthorized" or "Invalid token"
- Bot doesn't respond to any commands

**Diagnosis:**
```bash
# Check token in .env file
grep BOT_TOKEN /home/ali/botsarlak/.env

# Test token with curl
curl -s "https://api.telegram.org/bot$(grep BOT_TOKEN /home/ali/botsarlak/.env | cut -d'=' -f2)/getMe"
```

**Solutions:**
```bash
# Fix 1: Update token in .env file
# Edit /home/ali/botsarlak/.env and update BOT_TOKEN

# Fix 2: Restart service after token update
sudo systemctl restart botsarlak

# Fix 3: Verify token is correct
# Check 🔐_CREDENTIALS_SECURE.md for correct token
```

### 4. Port 8080 Already in Use

**Symptoms:**
- Health endpoint not accessible
- Logs show "Address already in use"

**Diagnosis:**
```bash
# Check what's using port 8080
sudo netstat -tlnp | grep :8080
sudo lsof -i :8080
```

**Solutions:**
```bash
# Fix 1: Kill process using port 8080
sudo kill -9 $(sudo lsof -t -i:8080)

# Fix 2: Change health port in configuration
# Edit main.py or config file to use different port

# Fix 3: Restart service
sudo systemctl restart botsarlak
```

### 5. Permission Denied Errors

**Symptoms:**
- Logs show "Permission denied"
- Service can't write to log files

**Diagnosis:**
```bash
# Check file ownership
ls -la /home/ali/botsarlak/
ls -la /var/log/botsarlak/

# Check service user
sudo systemctl show botsarlak | grep User
```

**Solutions:**
```bash
# Fix 1: Fix ownership
sudo chown -R ali:ali /home/ali/botsarlak
sudo chown -R ali:ali /var/log/botsarlak

# Fix 2: Fix permissions
chmod 755 /home/ali/botsarlak
chmod 644 /home/ali/botsarlak/.env
chmod +x /home/ali/botsarlak/main.py

# Fix 3: Create log directory
sudo mkdir -p /var/log/botsarlak
sudo chown ali:ali /var/log/botsarlak
```

### 6. Import Errors

**Symptoms:**
- Logs show "ModuleNotFoundError"
- Service fails to start

**Diagnosis:**
```bash
# Check virtual environment
ls -la /home/ali/botsarlak/.venv/

# Test imports manually
cd /home/ali/botsarlak
source .venv/bin/activate
python -c "import telegram; print('OK')"
```

**Solutions:**
```bash
# Fix 1: Reinstall dependencies
cd /home/ali/botsarlak
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Fix 2: Check requirements.txt
cat requirements.txt | head -10

# Fix 3: Install missing packages
pip install python-telegram-bot asyncpg python-dotenv
```

---

## 🔄 Recovery Procedures

### Complete Service Reset
```bash
# Stop service
sudo systemctl stop botsarlak

# Clean up
rm -rf /home/ali/botsarlak/.venv
rm -f /home/ali/botsarlak/.env

# Recreate environment
cd /home/ali/botsarlak
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Recreate .env from template
cp env.production .env

# Start service
sudo systemctl start botsarlak
```

### Database Reset
```bash
# Backup current database
pg_dump -h localhost -U postgres sarlak_academy > backup_$(date +%Y%m%d_%H%M%S).sql

# Drop and recreate database
sudo -u postgres dropdb sarlak_academy
sudo -u postgres createdb sarlak_academy

# Run migrations
cd /home/ali/botsarlak
source .venv/bin/activate
make migrate
```

### Full System Reset
```bash
# Complete reset procedure
ssh ali@163.5.94.227 "
    # Stop all services
    sudo systemctl stop botsarlak
    
    # Clean project directory
    cd /home/ali/botsarlak
    rm -rf .venv __pycache__ *.pyc
    
    # Recreate from scratch
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    
    # Restart service
    sudo systemctl start botsarlak
"
```

---

## 📊 Monitoring & Logs

### Real-time Monitoring
```bash
# Watch service status
watch -n 5 'sudo systemctl status botsarlak --no-pager | head -10'

# Monitor logs in real-time
sudo journalctl -u botsarlak -f

# Monitor health endpoint
watch -n 10 'curl -s http://localhost:8080/healthz | jq .'
```

### Log Analysis
```bash
# Search for errors
sudo journalctl -u botsarlak | grep -i error

# Search for specific patterns
sudo journalctl -u botsarlak | grep -i "database\|connection\|token"

# Export logs for analysis
sudo journalctl -u botsarlak --since "1 hour ago" > bot_logs_$(date +%Y%m%d_%H%M).log
```

---

## 🆘 Emergency Contacts & Resources

### Quick Reference
- **Server**: 163.5.94.227
- **User**: ali
- **Service**: botsarlak
- **Health**: http://163.5.94.227:8080/healthz
- **Logs**: /var/log/botsarlak/

### Emergency Commands
```bash
# Emergency stop
sudo systemctl stop botsarlak

# Emergency start
sudo systemctl start botsarlak

# Emergency restart
sudo systemctl restart botsarlak

# Emergency status
sudo systemctl status botsarlak
```

### Backup & Recovery
```bash
# Create backup
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz /home/ali/botsarlak

# Database backup
pg_dump -h localhost -U postgres sarlak_academy > db_backup_$(date +%Y%m%d_%H%M%S).sql
```

---

## 📝 Troubleshooting Checklist

### Before Deployment
- [ ] Check server connectivity: `ping 163.5.94.227`
- [ ] Verify SSH access: `ssh ali@163.5.94.227`
- [ ] Check disk space: `df -h`
- [ ] Verify Python version: `python3 --version`

### After Deployment
- [ ] Service status: `sudo systemctl status botsarlak`
- [ ] Health endpoint: `curl http://localhost:8080/healthz`
- [ ] Bot response: Send `/start` to bot
- [ ] Database connection: `psql -h localhost -U postgres -d sarlak_academy -c "SELECT 1;"`
- [ ] Logs check: `sudo journalctl -u botsarlak -n 20`

### Regular Maintenance
- [ ] Check service status daily
- [ ] Monitor disk space weekly
- [ ] Review logs for errors
- [ ] Test health endpoint
- [ ] Verify bot functionality

---

**Last Updated**: $(date)
**Version**: 2.2.1-qa-fix





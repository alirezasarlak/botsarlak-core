#!/bin/bash

# SarlakBot v6 Full - Dual Bot Setup (Test + Main)
# This script sets up both test and main bots on the server

SERVER_IP="91.107.128.14"
SERVER_USER="ali"
SERVER_PASS="ali456456"

echo "🤖 Setting up dual bot configuration..."

# Create environment files for both bots
cat > /tmp/.env.test << 'EOF'
# Test Bot Configuration
BOT_TOKEN=8028965917:AAFw23S-_894fwa_ioJmtsS47d5l_XGcK7g
BOT_USERNAME=botsarlak_test
BOT_NAME=Sarlak Academy Test Bot

# Database Configuration
DATABASE_URL=postgresql+asyncpg://botsarlak_user:botsarlak_pass123@localhost/botsarlak_core
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=botsarlak_core
DATABASE_USER=botsarlak_user
DATABASE_PASSWORD=botsarlak_pass123

# Redis Configuration
REDIS_URL=redis://localhost:6379/1
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=1

# Channel Configuration
CHANNEL_USERNAME=Sarlak_Academy
CHANNEL_ID=@Sarlak_Academy

# Security
ENCRYPTION_KEY=your-32-character-secret-key-here
SECRET_KEY=your-secret-key-here

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Environment
ENVIRONMENT=test
DEBUG=true

# Features
ENABLE_ANALYTICS=true
ENABLE_COMPETITION=true
ENABLE_LEADERBOARD=true
EOF

cat > /tmp/.env.main << 'EOF'
# Main Bot Configuration
BOT_TOKEN=7214099093:AAEePAXAk8lBGULYzUbQS-6MiwplofDze8o
BOT_USERNAME=botsarlak_core
BOT_NAME=Sarlak Academy Bot

# Database Configuration
DATABASE_URL=postgresql+asyncpg://botsarlak_user:botsarlak_pass123@localhost/botsarlak_core
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=botsarlak_core
DATABASE_USER=botsarlak_user
DATABASE_PASSWORD=botsarlak_pass123

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Channel Configuration
CHANNEL_USERNAME=Sarlak_Academy
CHANNEL_ID=@Sarlak_Academy

# Security
ENCRYPTION_KEY=your-32-character-secret-key-here
SECRET_KEY=your-secret-key-here

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Environment
ENVIRONMENT=production
DEBUG=false

# Features
ENABLE_ANALYTICS=true
ENABLE_COMPETITION=true
ENABLE_LEADERBOARD=true
EOF

# Create systemd service files
cat > /tmp/botsarlak-test.service << 'EOF'
[Unit]
Description=SarlakBot v6 Test Bot
After=network.target postgresql.service redis-server.service
Wants=postgresql.service redis-server.service

[Service]
Type=simple
User=ali
Group=ali
WorkingDirectory=/home/ali/botsarlak-core
Environment=PATH=/usr/bin:/usr/local/bin
Environment=PYTHONPATH=/home/ali/botsarlak-core
EnvironmentFile=/home/ali/botsarlak-core/.env.test
ExecStart=/usr/bin/python3 /home/ali/botsarlak-core/app/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

cat > /tmp/botsarlak-main.service << 'EOF'
[Unit]
Description=SarlakBot v6 Main Bot
After=network.target postgresql.service redis-server.service
Wants=postgresql.service redis-server.service

[Service]
Type=simple
User=ali
Group=ali
WorkingDirectory=/home/ali/botsarlak-core
Environment=PATH=/usr/bin:/usr/local/bin
Environment=PYTHONPATH=/home/ali/botsarlak-core
EnvironmentFile=/home/ali/botsarlak-core/.env.main
ExecStart=/usr/bin/python3 /home/ali/botsarlak-core/app/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "📤 Uploading configuration files..."
expect << EOF
spawn scp /tmp/.env.test /tmp/.env.main /tmp/botsarlak-test.service /tmp/botsarlak-main.service $SERVER_USER@$SERVER_IP:/tmp/
expect "password:"
send "$SERVER_PASS\r"
expect eof
EOF

echo "🔧 Configuring server..."
expect << EOF
spawn ssh $SERVER_USER@$SERVER_IP
expect "password:"
send "$SERVER_PASS\r"
expect "$ "
send "cd botsarlak-core\r"
expect "$ "
send "echo '=== STOPPING EXISTING SERVICES ==='\r"
expect "$ "
send "sudo systemctl stop botsarlak-core.service 2>/dev/null || true\r"
expect "$ "
send "sudo systemctl stop botsarlak-test.service 2>/dev/null || true\r"
expect "$ "
send "sudo systemctl stop botsarlak-main.service 2>/dev/null || true\r"
expect "$ "
send "pkill -f 'python.*bot' 2>/dev/null || true\r"
expect "$ "
send "echo '=== SETTING UP ENVIRONMENT FILES ==='\r"
expect "$ "
send "cp /tmp/.env.test .env.test\r"
expect "$ "
send "cp /tmp/.env.main .env.main\r"
expect "$ "
send "echo '=== SETTING UP SERVICES ==='\r"
expect "$ "
send "sudo cp /tmp/botsarlak-test.service /etc/systemd/system/\r"
expect "$ "
send "sudo cp /tmp/botsarlak-main.service /etc/systemd/system/\r"
expect "$ "
send "sudo systemctl daemon-reload\r"
expect "$ "
send "echo '=== STARTING TEST BOT ==='\r"
expect "$ "
send "sudo systemctl enable botsarlak-test.service\r"
expect "$ "
send "sudo systemctl start botsarlak-test.service\r"
expect "$ "
send "sleep 3\r"
expect "$ "
send "echo '=== STARTING MAIN BOT ==='\r"
expect "$ "
send "sudo systemctl enable botsarlak-main.service\r"
expect "$ "
send "sudo systemctl start botsarlak-main.service\r"
expect "$ "
send "sleep 3\r"
expect "$ "
send "echo '=== CHECKING STATUS ==='\r"
expect "$ "
send "sudo systemctl status botsarlak-test.service\r"
expect "$ "
send "sudo systemctl status botsarlak-main.service\r"
expect "$ "
send "echo '=== CHECKING PROCESSES ==='\r"
expect "$ "
send "ps aux | grep python | grep bot\r"
expect "$ "
send "exit\r"
interact
EOF

echo "✅ Dual bot setup completed!"
echo "🤖 Test Bot: botsarlak-test.service"
echo "🤖 Main Bot: botsarlak-main.service"

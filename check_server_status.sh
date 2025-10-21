#!/bin/bash

# SarlakBot v6 Full - Server Status Check Script
# This script checks the complete status of the bot on the server

SERVER_IP="91.107.128.14"
SERVER_USER="ali"
SERVER_PASS="ali456456"

echo "🔍 Checking SarlakBot v6 Full server status..."

expect << EOF
spawn ssh $SERVER_USER@$SERVER_IP
expect "password:"
send "$SERVER_PASS\r"
expect "$ "
send "cd botsarlak-core\r"
expect "$ "
send "echo '=== BOT SERVICE STATUS ==='\r"
expect "$ "
send "sudo systemctl status botsarlak-core.service\r"
expect "$ "
send "echo '=== RUNNING PROCESSES ==='\r"
expect "$ "
send "ps aux | grep python | grep -v grep\r"
expect "$ "
send "echo '=== BOT LOGS (last 20 lines) ==='\r"
expect "$ "
send "tail -20 bot.log 2>/dev/null || echo 'No bot.log found'\r"
expect "$ "
send "echo '=== PROJECT STRUCTURE ==='\r"
expect "$ "
send "ls -la app/ 2>/dev/null || echo 'No app directory found'\r"
expect "$ "
send "echo '=== ENVIRONMENT CHECK ==='\r"
expect "$ "
send "python3 --version && pip3 --version\r"
expect "$ "
send "echo '=== DATABASE STATUS ==='\r"
expect "$ "
send "sudo systemctl status postgresql\r"
expect "$ "
send "echo '=== REDIS STATUS ==='\r"
expect "$ "
send "sudo systemctl status redis-server\r"
expect "$ "
send "echo '=== DISK USAGE ==='\r"
expect "$ "
send "df -h\r"
expect "$ "
send "echo '=== MEMORY USAGE ==='\r"
expect "$ "
send "free -h\r"
expect "$ "
send "exit\r"
interact
EOF

echo "✅ Server status check completed!"

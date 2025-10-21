#!/bin/bash

# Simple server fix script
SERVER_IP="91.107.128.14"
SERVER_USER="ali"
SERVER_PASS="ali456456"

echo "🔧 Simple server fix..."

expect << EOF
spawn ssh $SERVER_USER@$SERVER_IP
expect "password:"
send "$SERVER_PASS\r"
expect "$ "
send "cd botsarlak-core\r"
expect "$ "
send "sudo systemctl stop botsarlak-core.service\r"
expect "$ "
send "sudo systemctl disable botsarlak-core.service\r"
expect "$ "
send "python3 main.py &\r"
expect "$ "
send "sleep 5\r"
expect "$ "
send "ps aux | grep python | grep main\r"
expect "$ "
send "exit\r"
interact
EOF

echo "✅ Simple fix completed!"

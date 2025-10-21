#!/bin/bash

# SarlakBot v6 Full - Server Deployment Script
# This script deploys the latest version to the server

SERVER_IP="91.107.128.14"
SERVER_USER="ali"
SERVER_PASS="ali456456"
SERVER_PATH="~/botsarlak-core"

echo "🚀 Starting SarlakBot v6 Full deployment..."

# Create a temporary directory for deployment
TEMP_DIR="/tmp/sarlakbot_deploy_$(date +%s)"
mkdir -p "$TEMP_DIR"

echo "📦 Preparing deployment package..."
# Copy all necessary files except git and cache
rsync -av --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.venv' --exclude='bot_data.pkl' --exclude='*.log' --exclude='audit-reports' --exclude='docs' . "$TEMP_DIR/"

echo "📤 Uploading files to server..."
# Use expect to handle password authentication
expect << EOF
spawn scp -r "$TEMP_DIR"/* $SERVER_USER@$SERVER_IP:$SERVER_PATH/
expect "password:"
send "$SERVER_PASS\r"
expect eof
EOF

echo "🔧 Updating server configuration..."
# Connect to server and update
expect << EOF
spawn ssh $SERVER_USER@$SERVER_IP
expect "password:"
send "$SERVER_PASS\r"
expect "$ "
send "cd $SERVER_PATH\r"
expect "$ "
send "sudo systemctl stop botsarlak-core.service\r"
expect "$ "
send "pip3 install -r requirements.txt\r"
expect "$ "
send "sudo systemctl start botsarlak-core.service\r"
expect "$ "
send "sudo systemctl status botsarlak-core.service\r"
expect "$ "
send "exit\r"
interact
EOF

# Cleanup
rm -rf "$TEMP_DIR"

echo "✅ Deployment completed!"
echo "🌐 Bot should be running on the server"

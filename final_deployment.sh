#!/bin/bash

# Final SarlakBot v6 Full Deployment Script
echo "🚀 Final SarlakBot v6 Full Deployment"

SERVER_IP="91.107.128.14"
SERVER_USER="ali"
SERVER_PASS="ali456456"

# Create a comprehensive deployment script
cat > /tmp/final_deploy.sh << 'EOF'
#!/bin/bash

echo "🔧 Final server deployment..."

# Stop any running services
sudo systemctl stop botsarlak-core.service 2>/dev/null || true
sudo systemctl disable botsarlak-core.service 2>/dev/null || true

# Kill any existing bot processes
pkill -f "python.*bot" 2>/dev/null || true

# Navigate to project directory
cd /home/ali/botsarlak-core

# Check what files we have
echo "📁 Available Python files:"
ls -la *.py | head -5

# Try to run the bot with different approaches
echo "🤖 Starting bot..."

# Method 1: Try app/bot.py
if [ -f "app/bot.py" ]; then
    echo "Starting with app/bot.py..."
    nohup python3 app/bot.py > bot.log 2>&1 &
    sleep 3
    if ps aux | grep -q "app/bot.py"; then
        echo "✅ Bot started successfully with app/bot.py"
        exit 0
    fi
fi

# Method 2: Try main.py
if [ -f "main.py" ]; then
    echo "Starting with main.py..."
    nohup python3 main.py > bot.log 2>&1 &
    sleep 3
    if ps aux | grep -q "main.py"; then
        echo "✅ Bot started successfully with main.py"
        exit 0
    fi
fi

# Method 3: Try any working bot file
for bot_file in complete_rebuilt_bot.py final_working_bot.py ultimate_complete_bot.py; do
    if [ -f "$bot_file" ]; then
        echo "Starting with $bot_file..."
        nohup python3 "$bot_file" > bot.log 2>&1 &
        sleep 3
        if ps aux | grep -q "$bot_file"; then
            echo "✅ Bot started successfully with $bot_file"
            exit 0
        fi
    fi
done

echo "❌ Failed to start bot with any method"
exit 1
EOF

# Upload and run the script
expect << EOF
spawn scp /tmp/final_deploy.sh $SERVER_USER@$SERVER_IP:/tmp/
expect "password:"
send "$SERVER_PASS\r"
expect eof
EOF

expect << EOF
spawn ssh $SERVER_USER@$SERVER_IP
expect "password:"
send "$SERVER_PASS\r"
expect "$ "
send "chmod +x /tmp/final_deploy.sh\r"
expect "$ "
send "/tmp/final_deploy.sh\r"
expect "$ "
send "echo '=== FINAL STATUS CHECK ==='\r"
expect "$ "
send "ps aux | grep python | grep -v grep\r"
expect "$ "
send "echo '=== BOT LOGS ==='\r"
expect "$ "
send "tail -10 bot.log 2>/dev/null || echo 'No logs found'\r"
expect "$ "
send "exit\r"
interact
EOF

echo "✅ Final deployment completed!"

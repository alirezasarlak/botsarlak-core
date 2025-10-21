#!/bin/bash
# 🚀 Sarlak Academy Bot - Complete Deployment Script
# Based on reference files and updated credentials
# Version: 2.2.1-qa-fix

set -euo pipefail

# ==================== CONFIGURATION ====================
# All credentials from 🔐_CREDENTIALS_SECURE.md

SERVER_USER="ali"
SERVER_IP="163.5.94.227"
SERVER_PATH="/home/ali/botsarlak"
SERVER_PASSWORD="ali123123"

# Database Configuration
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="sarlak_academy"
DB_USER="postgres"
DB_PASSWORD="ali123123"

# Bot Configuration
BOT_TOKEN="7214099093:AAEqEOo2z_iOCo8jDmrw4ZX5FQn3qCjh61k"
ADMIN_ID="694245594"
OPENAI_API_KEY="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"

# ==================== COLORS ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# ==================== LOGGING FUNCTIONS ====================
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# ==================== PRE-DEPLOYMENT CHECKS ====================
pre_deployment_checks() {
    log_step "🔍 Pre-deployment checks..."
    
    # Check if we're in the right directory
    if [ ! -f "main.py" ]; then
        log_error "main.py not found! Are you in the correct directory?"
        exit 1
    fi
    
    # Check if credentials file exists
    if [ ! -f "🔐_CREDENTIALS_SECURE.md" ]; then
        log_warning "Credentials file not found, but continuing with hardcoded values"
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        log_info "Creating .env file from production template..."
        cp env.production .env
        log_success ".env file created"
    fi
    
    log_success "Pre-deployment checks completed"
}

# ==================== FILE SYNC ====================
sync_files() {
    log_step "📁 Syncing files to server..."
    
    # Create rsync command with proper exclusions
    rsync -avz --delete \
        --exclude ".git" \
        --exclude "__pycache__" \
        --exclude ".venv" \
        --exclude "venv" \
        --exclude "*.log" \
        --exclude ".env" \
        --exclude "🔐_CREDENTIALS_SECURE.md" \
        ./ ${SERVER_USER}@${SERVER_IP}:${SERVER_PATH}/
    
    log_success "Files synced successfully"
}

# ==================== REMOTE DEPLOYMENT ====================
remote_deployment() {
    log_step "🚀 Starting remote deployment..."
    
    ssh ${SERVER_USER}@${SERVER_IP} bash -lc "
        set -e
        cd ${SERVER_PATH}
        
        echo '📁 Setting up environment...'
        
        # Create virtual environment if it doesn't exist
        if [ ! -d '.venv' ]; then
            python3 -m venv .venv
            echo 'Virtual environment created'
        fi
        
        # Activate virtual environment
        source .venv/bin/activate
        
        # Update .env file with production credentials
        cat > .env << 'EOF'
# Sarlak Academy Bot Configuration - Production
BOT_TOKEN=${BOT_TOKEN}
ADMIN_ID=${ADMIN_ID}
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
OPENAI_API_KEY=${OPENAI_API_KEY}
BOT_NAME=Sarlak Academy
BOT_USERNAME=@SarlakAcademyBot
TIMEZONE=Asia/Tehran
LOG_LEVEL=INFO
LOG_FILE=bot.log
DAILY_REPORT_BONUS=10
STREAK_MULTIPLIER=5
LEVEL_UP_THRESHOLD=100
EOF
        
        echo '📦 Installing dependencies...'
        pip install --upgrade pip
        pip install -r requirements.txt
        
        echo '🗄️ Setting up database...'
        # Check if database exists, create if not
        if ! psql -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME} -c 'SELECT 1;' >/dev/null 2>&1; then
            echo 'Creating database...'
            createdb -h ${DB_HOST} -U ${DB_USER} ${DB_NAME} || true
        fi
        
        # Run migrations if Makefile exists
        if [ -f 'Makefile' ]; then
            make migrate || echo 'Migration failed, continuing...'
        fi
        
        echo '🔧 Setting up systemd service...'
        # Update systemd service file
        sudo tee /etc/systemd/system/botsarlak.service > /dev/null << 'EOF'
[Unit]
Description=Sarlak Academy Telegram Bot
After=network.target postgresql.service

[Service]
Type=simple
User=${SERVER_USER}
WorkingDirectory=${SERVER_PATH}
Environment=\"PATH=${SERVER_PATH}/.venv/bin\"
ExecStart=${SERVER_PATH}/.venv/bin/python main.py
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
        sudo chown ${SERVER_USER}:${SERVER_USER} /var/log/botsarlak
        
        # Reload systemd and enable service
        sudo systemctl daemon-reload
        sudo systemctl enable botsarlak
        
        echo '🔄 Restarting bot service...'
        sudo systemctl restart botsarlak
        
        echo '⏳ Waiting for service to start...'
        sleep 5
        
        echo '📊 Checking service status...'
        sudo systemctl status botsarlak --no-pager | head -20
        
        echo '🏥 Health check...'
        sleep 10
        curl -s http://localhost:8080/healthz || echo 'Health endpoint not responding yet'
        
        echo '📝 Logging deployment...'
        echo \"\$(date -Is) deploy completed successfully\" | sudo tee -a ${SERVER_PATH}/deploy.log
        
        echo '✅ Remote deployment completed!'
    "
    
    log_success "Remote deployment completed"
}

# ==================== POST-DEPLOYMENT VERIFICATION ====================
post_deployment_verification() {
    log_step "🔍 Post-deployment verification..."
    
    # Check if service is running
    if ssh ${SERVER_USER}@${SERVER_IP} "sudo systemctl is-active --quiet botsarlak"; then
        log_success "Bot service is running"
    else
        log_error "Bot service is not running!"
        log_info "Checking logs..."
        ssh ${SERVER_USER}@${SERVER_IP} "sudo journalctl -u botsarlak -n 20 --no-pager"
        return 1
    fi
    
    # Check health endpoint
    log_info "Checking health endpoint..."
    if curl -s --max-time 10 http://${SERVER_IP}:8080/healthz > /dev/null; then
        log_success "Health endpoint is responding"
    else
        log_warning "Health endpoint not responding (may take time to start)"
    fi
    
    # Show recent logs
    log_info "Recent bot logs:"
    ssh ${SERVER_USER}@${SERVER_IP} "sudo journalctl -u botsarlak -n 10 --no-pager"
    
    log_success "Post-deployment verification completed"
}

# ==================== MAIN DEPLOYMENT FLOW ====================
main() {
    echo "🚀 Sarlak Academy Bot - Complete Deployment"
    echo "=============================================="
    echo ""
    
    log_info "Starting deployment to ${SERVER_USER}@${SERVER_IP}:${SERVER_PATH}"
    echo ""
    
    # Run deployment steps
    pre_deployment_checks
    echo ""
    
    sync_files
    echo ""
    
    remote_deployment
    echo ""
    
    post_deployment_verification
    echo ""
    
    echo "🎉 Deployment completed successfully!"
    echo ""
    echo "📋 Useful commands:"
    echo "  🔍 Check status: ssh ${SERVER_USER}@${SERVER_IP} 'sudo systemctl status botsarlak'"
    echo "  📋 View logs: ssh ${SERVER_USER}@${SERVER_IP} 'sudo journalctl -u botsarlak -f'"
    echo "  🔄 Restart: ssh ${SERVER_USER}@${SERVER_IP} 'sudo systemctl restart botsarlak'"
    echo "  🏥 Health: curl http://${SERVER_IP}:8080/healthz"
    echo ""
    echo "🤖 Bot is ready to use!"
}

# ==================== ERROR HANDLING ====================
trap 'log_error "Deployment failed at line $LINENO"' ERR

# ==================== EXECUTION ====================
main "$@"





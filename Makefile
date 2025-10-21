# 🌌 SarlakBot v3.0 - Gen-Z Cosmic Study Journey
# Professional Makefile for development and deployment

.PHONY: help install test lint format check clean deploy setup run health logs

# Colors for output
BLUE=\033[0;34m
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)🌌 SarlakBot v3.0 - Gen-Z Cosmic Study Journey$(NC)"
	@echo "=============================================="
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# ==================== DEVELOPMENT ====================

install: ## Install dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	pip install -r requirements.txt
	@echo "$(GREEN)✅ Dependencies installed$(NC)"

setup: ## Initial setup (create venv and install deps)
	@echo "$(BLUE)Setting up development environment...$(NC)"
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	@echo "$(GREEN)✅ Setup complete$(NC)"

run: ## Run the bot locally
	@echo "$(BLUE)Starting SarlakBot v3.0...$(NC)"
	.venv/bin/python main.py

# ==================== CODE QUALITY ====================

test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	pytest tests/ -v
	@echo "$(GREEN)✅ Tests completed$(NC)"

lint: ## Run linting with ruff
	@echo "$(BLUE)Running linting...$(NC)"
	ruff check src/ tests/ main.py
	@echo "$(GREEN)✅ Linting passed$(NC)"

format: ## Format code with black
	@echo "$(BLUE)Formatting code...$(NC)"
	black src/ tests/ main.py
	@echo "$(GREEN)✅ Formatting complete$(NC)"

format-check: ## Check code formatting with black
	@echo "$(BLUE)Checking code formatting...$(NC)"
	black --check src/ tests/ main.py
	@echo "$(GREEN)✅ Format check passed$(NC)"

check: format-check lint test ## Run all quality checks
	@echo "$(GREEN)✅ All quality checks passed$(NC)"

clean: ## Clean up temporary files
	@echo "$(BLUE)Cleaning up temporary files...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

# ==================== DEPLOYMENT ====================

deploy: check ## Deploy to production (runs checks first)
	@echo "$(BLUE)Deploying SarlakBot v3.0 to production...$(NC)"
	./🚀_DEPLOY_COMPLETE.sh
	@echo "$(GREEN)✅ Deployment complete$(NC)"

deploy-docker: ## Deploy using Docker Compose
	@echo "$(BLUE)Deploying with Docker Compose...$(NC)"
	docker-compose -f docker-compose.production.yml up --build -d
	@echo "$(GREEN)✅ Docker deployment complete$(NC)"

deploy-quick: ## Quick deployment without checks
	@echo "$(YELLOW)Quick deployment (skipping checks)...$(NC)"
	./🚀_DEPLOY_COMPLETE.sh
	@echo "$(GREEN)✅ Quick deployment complete$(NC)"

# ==================== SERVER MANAGEMENT ====================

status: ## Check server status
	@echo "$(BLUE)Checking server status...$(NC)"
	ssh -i ~/.ssh/botsarlak_key -o StrictHostKeyChecking=no ali@163.5.94.227 "sudo systemctl status botsarlak --no-pager | head -15"

restart: ## Restart bot service
	@echo "$(BLUE)Restarting bot service...$(NC)"
	ssh -i ~/.ssh/botsarlak_key -o StrictHostKeyChecking=no ali@163.5.94.227 "sudo systemctl restart botsarlak"
	@echo "$(GREEN)✅ Service restarted$(NC)"

stop: ## Stop bot service
	@echo "$(BLUE)Stopping bot service...$(NC)"
	ssh -i ~/.ssh/botsarlak_key -o StrictHostKeyChecking=no ali@163.5.94.227 "sudo systemctl stop botsarlak"
	@echo "$(GREEN)✅ Service stopped$(NC)"

start: ## Start bot service
	@echo "$(BLUE)Starting bot service...$(NC)"
	ssh -i ~/.ssh/botsarlak_key -o StrictHostKeyChecking=no ali@163.5.94.227 "sudo systemctl start botsarlak"
	@echo "$(GREEN)✅ Service started$(NC)"

# ==================== MONITORING ====================

health: ## Check health endpoint
	@echo "$(BLUE)Checking health endpoint...$(NC)"
	curl -s http://163.5.94.227:8080/healthz | python -m json.tool || echo "$(RED)Health endpoint not responding$(NC)"

logs: ## Show recent logs
	@echo "$(BLUE)Showing recent logs...$(NC)"
	ssh -i ~/.ssh/botsarlak_key -o StrictHostKeyChecking=no ali@163.5.94.227 "sudo journalctl -u botsarlak -n 20 --no-pager"

logs-follow: ## Follow logs in real-time
	@echo "$(BLUE)Following logs...$(NC)"
	ssh -i ~/.ssh/botsarlak_key -o StrictHostKeyChecking=no ali@163.5.94.227 "sudo journalctl -u botsarlak -f"

# ==================== DATABASE ====================

migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	ssh -i ~/.ssh/botsarlak_key -o StrictHostKeyChecking=no ali@163.5.94.227 "cd /home/ali/botsarlak && source .venv/bin/activate && python -c 'from src.database.connection import db; import asyncio; asyncio.run(db.init())'"
	@echo "$(GREEN)✅ Migrations completed$(NC)"

db-status: ## Check database status
	@echo "$(BLUE)Checking database status...$(NC)"
	ssh -i ~/.ssh/botsarlak_key -o StrictHostKeyChecking=no ali@163.5.94.227 "PGPASSWORD=ali123123 psql -h localhost -U postgres -d sarlak_academy -c 'SELECT COUNT(*) as user_count FROM users;'"

# ==================== BACKUP & RESTORE ====================

backup: ## Create backup of database and code
	@echo "$(BLUE)Creating backup...$(NC)"
	@mkdir -p backups
	@TIMESTAMP=$$(date +%Y%m%d_%H%M%S); \
	ssh -i ~/.ssh/botsarlak_key -o StrictHostKeyChecking=no ali@163.5.94.227 "PGPASSWORD=ali123123 pg_dump -h localhost -U postgres sarlak_academy" > backups/db_backup_$$TIMESTAMP.sql; \
	rsync -avz ali@163.5.94.227:/home/ali/botsarlak/ backups/code_backup_$$TIMESTAMP/; \
	echo "$(GREEN)✅ Backup created: backups/db_backup_$$TIMESTAMP.sql$(NC)"

# ==================== DOCKER ====================

docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t sarlakbot:latest .
	@echo "$(GREEN)✅ Docker image built$(NC)"

docker-stop: ## Stop Docker containers
	@echo "$(BLUE)Stopping Docker containers...$(NC)"
	docker-compose -f docker-compose.production.yml down
	@echo "$(GREEN)✅ Docker containers stopped$(NC)"

docker-logs: ## Show Docker logs
	@echo "$(BLUE)Showing Docker logs...$(NC)"
	docker-compose -f docker-compose.production.yml logs -f

# ==================== UTILITIES ====================

sync: ## Sync files to server
	@echo "$(BLUE)Syncing files to server...$(NC)"
	rsync -avz --delete \
		--exclude ".git" \
		--exclude "__pycache__" \
		--exclude ".venv" \
		--exclude "venv" \
		--exclude "*.log" \
		--exclude ".env" \
		--exclude "🔐_CREDENTIALS_SECURE.md" \
		./ ali@163.5.94.227:/home/ali/botsarlak/
	@echo "$(GREEN)✅ Files synced$(NC)"

connect: ## Connect to server
	@echo "$(BLUE)Connecting to server...$(NC)"
	ssh -i ~/.ssh/botsarlak_key -o StrictHostKeyChecking=no ali@163.5.94.227

info: ## Show system information
	@echo "$(BLUE)System Information:$(NC)"
	@echo "Server: 163.5.94.227"
	@echo "User: ali"
	@echo "Path: /home/ali/botsarlak"
	@echo "Service: botsarlak"
	@echo "Health: http://163.5.94.227:8080/healthz"
	@echo "Bot: @SarlakAcademyBot"

# ==================== MAINTENANCE ====================

update-deps: ## Update dependencies
	@echo "$(BLUE)Updating dependencies...$(NC)"
	pip install --upgrade pip
	pip install -r requirements.txt --upgrade
	@echo "$(GREEN)✅ Dependencies updated$(NC)"

clean-logs: ## Clean old log files
	@echo "$(BLUE)Cleaning old log files...$(NC)"
	ssh -i ~/.ssh/botsarlak_key -o StrictHostKeyChecking=no ali@163.5.94.227 "sudo journalctl --vacuum-time=7d"
	@echo "$(GREEN)✅ Logs cleaned$(NC)"

# ==================== EMERGENCY ====================

emergency-stop: ## Emergency stop all services
	@echo "$(RED)EMERGENCY STOP - Stopping all services...$(NC)"
	ssh -i ~/.ssh/botsarlak_key -o StrictHostKeyChecking=no ali@163.5.94.227 "sudo systemctl stop botsarlak"
	docker-compose -f docker-compose.production.yml down
	@echo "$(RED)✅ All services stopped$(NC)"

emergency-restart: ## Emergency restart all services
	@echo "$(YELLOW)EMERGENCY RESTART - Restarting all services...$(NC)"
	ssh -i ~/.ssh/botsarlak_key -o StrictHostKeyChecking=no ali@163.5.94.227 "sudo systemctl restart botsarlak"
	docker-compose -f docker-compose.production.yml restart
	@echo "$(GREEN)✅ All services restarted$(NC)"

# ==================== HELPERS ====================

check-credentials: ## Check if credentials file exists
	@if [ -f "🔐_CREDENTIALS_SECURE.md" ]; then \
		echo "$(GREEN)✅ Credentials file found$(NC)"; \
	else \
		echo "$(RED)❌ Credentials file not found$(NC)"; \
	fi

validate-env: ## Validate environment configuration
	@echo "$(BLUE)Validating environment...$(NC)"
	@if [ -f ".env" ]; then \
		echo "$(GREEN)✅ .env file exists$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  .env file not found, copying from template...$(NC)"; \
		cp env.example .env; \
	fi
	@echo "$(GREEN)✅ Environment validated$(NC)"

# Default target
.DEFAULT_GOAL := help





.PHONY: help install install-dev format lint type-check test clean run setup

help: ## Show this help message
	@echo "SarlakBot v6 Full - Development Commands"
	@echo "============================================="
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Set up development environment
	python3 -m venv .venv
	@echo "Virtual environment created. Activate with: source .venv/bin/activate"

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements-dev.txt

format: ## Format code with black
	black .

lint: ## Lint code with ruff
	ruff check .

lint-fix: ## Fix linting issues with ruff
	ruff check . --fix

type-check: ## Run type checking with mypy
	mypy .

test: ## Run tests with pytest
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=app --cov-report=html --cov-report=term

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf dist
	rm -rf build

run: ## Run the bot
	python main.py

check: format lint type-check test ## Run all checks (format, lint, type-check, test)

pre-commit: ## Install pre-commit hooks
	pre-commit install

dev-setup: setup install-dev pre-commit ## Complete development setup
	@echo "Development environment ready!"
	@echo "Activate with: source .venv/bin/activate"

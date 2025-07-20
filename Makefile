# Django Makefile for Wellness AI Backend
# Usage: make <command>

# Variables
PYTHON = python3
MANAGE = manage.py
DJANGO_SETTINGS = apps.settings
DOCKER_COMPOSE = docker-compose
VENV_NAME = .venv
VENV_PATH = $(VENV_NAME)/bin
VENV_ACTIVATE = $(VENV_PATH)/activate

# Colors for output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
BLUE = \033[0;34m
NC = \033[0m # No Color

.PHONY: help venv venv-create venv-activate venv-check pyenv-setup python-check fresh-install install run run-dev migrate makemigrations superuser shell test test-coverage clean docker-up docker-down docker-logs docker-restart

# Default target
help:
	@echo "$(GREEN)Available commands:$(NC)"
	@echo "  $(YELLOW)venv$(NC)            - Create virtual environment if it doesn't exist"
	@echo "  $(YELLOW)venv-create$(NC)     - Force create new virtual environment"
	@echo "  $(YELLOW)venv-activate$(NC)   - Show activation command"
	@echo "  $(YELLOW)venv-check$(NC)      - Check if virtual environment is activated"
	@echo "  $(YELLOW)pyenv-setup$(NC)     - Setup pyenv Python version"
	@echo "  $(YELLOW)python-check$(NC)    - Check Python version compatibility"
	@echo "  $(YELLOW)fresh-install$(NC)   - Complete fresh environment setup"
	@echo "  $(YELLOW)install$(NC)         - Install dependencies using uv"
	@echo "  $(YELLOW)run$(NC)             - Run Django development server"
	@echo "  $(YELLOW)run-dev$(NC)         - Run Django server with debug mode"
	@echo "  $(YELLOW)migrate$(NC)         - Apply database migrations"
	@echo "  $(YELLOW)makemigrations$(NC)  - Create new database migrations"
	@echo "  $(YELLOW)superuser$(NC)       - Create Django superuser"
	@echo "  $(YELLOW)shell$(NC)           - Open Django shell"
	@echo "  $(YELLOW)test$(NC)            - Run tests"
	@echo "  $(YELLOW)test-coverage$(NC)   - Run tests with coverage report"
	@echo "  $(YELLOW)clean$(NC)           - Clean Python cache files"
	@echo "  $(YELLOW)docker-up$(NC)       - Start Docker services"
	@echo "  $(YELLOW)docker-down$(NC)     - Stop Docker services"
	@echo "  $(YELLOW)docker-logs$(NC)     - Show Docker logs"
	@echo "  $(YELLOW)docker-restart$(NC)  - Restart Docker services"
	@echo "  $(YELLOW)reset-db$(NC)        - Reset database (drop and recreate)"
	@echo "  $(YELLOW)collectstatic$(NC)   - Collect static files"
	@echo "  $(YELLOW)check$(NC)           - Run Django system check"

# Virtual environment management
venv:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(BLUE)Creating virtual environment...$(NC)"; \
		if command -v pyenv >/dev/null 2>&1; then \
			echo "$(YELLOW)Using pyenv Python version...$(NC)"; \
			pyenv exec $(PYTHON) -m venv $(VENV_NAME); \
		else \
			$(PYTHON) -m venv $(VENV_NAME); \
		fi; \
		echo "$(GREEN)Virtual environment created!$(NC)"; \
		echo "$(YELLOW)Run 'source $(VENV_ACTIVATE)' to activate it manually$(NC)"; \
	else \
		echo "$(GREEN)Virtual environment already exists at $(VENV_NAME)$(NC)"; \
	fi

venv-create:
	@echo "$(BLUE)Creating new virtual environment...$(NC)"
	@if [ -d "$(VENV_NAME)" ]; then \
		echo "$(YELLOW)Removing existing virtual environment...$(NC)"; \
		rm -rf $(VENV_NAME); \
	fi
	@if command -v pyenv >/dev/null 2>&1; then \
		echo "$(YELLOW)Using pyenv Python version...$(NC)"; \
		pyenv exec $(PYTHON) -m venv $(VENV_NAME); \
	else \
		$(PYTHON) -m venv $(VENV_NAME); \
	fi
	@echo "$(GREEN)Virtual environment created!$(NC)"
	@echo "$(YELLOW)Run 'source $(VENV_ACTIVATE)' to activate it manually$(NC)"

venv-activate:
	@echo "$(BLUE)To activate the virtual environment, run:$(NC)"
	@echo "$(YELLOW)source $(VENV_ACTIVATE)$(NC)"
	@echo "$(BLUE)Or use:$(NC)"
	@echo "$(YELLOW). $(VENV_ACTIVATE)$(NC)"

# Check if virtual environment is activated
venv-check:
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "$(RED)Virtual environment is not activated!$(NC)"; \
		echo "$(YELLOW)Run 'source $(VENV_ACTIVATE)' to activate it$(NC)"; \
	else \
		echo "$(GREEN)Virtual environment is activated: $$VIRTUAL_ENV$(NC)"; \
	fi

# Setup pyenv Python version
pyenv-setup:
	@if command -v pyenv >/dev/null 2>&1; then \
		echo "$(BLUE)Setting up pyenv Python version...$(NC)"; \
		if [ -f ".python-version" ]; then \
			REQUIRED_VERSION=$$(cat .python-version); \
			echo "$(YELLOW)Required Python version: $$REQUIRED_VERSION$(NC)"; \
			if pyenv versions | grep -q "$$REQUIRED_VERSION"; then \
				echo "$(GREEN)Python $$REQUIRED_VERSION is already installed$(NC)"; \
			else \
				echo "$(YELLOW)Installing Python $$REQUIRED_VERSION...$(NC)"; \
				pyenv install $$REQUIRED_VERSION; \
			fi; \
			pyenv local $$REQUIRED_VERSION; \
			echo "$(GREEN)Python version set to $$REQUIRED_VERSION$(NC)"; \
		else \
			echo "$(RED)No .python-version file found$(NC)"; \
		fi; \
	else \
		echo "$(RED)pyenv is not installed$(NC)"; \
		echo "$(YELLOW)Install pyenv first: https://github.com/pyenv/pyenv$(NC)"; \
	fi

# Check Python version compatibility
python-check:
	@if [ -f "pyproject.toml" ]; then \
		REQUIRED_PYTHON=$$(grep "requires-python" pyproject.toml | sed 's/.*= "\(.*\)"/\1/'); \
		CURRENT_VERSION=$$(python3 --version 2>&1 | sed 's/Python //'); \
		echo "$(BLUE)Project requires Python: $$REQUIRED_PYTHON$(NC)"; \
		echo "$(BLUE)Current Python version: $$CURRENT_VERSION$(NC)"; \
		if command -v pyenv >/dev/null 2>&1; then \
			echo "$(YELLOW)Available pyenv versions:$(NC)"; \
			pyenv versions --bare | head -5; \
		fi; \
	fi

# Complete fresh environment setup from scratch
fresh-install: clean
	@echo "$(BLUE)🚀 Starting fresh environment setup...$(NC)"
	@echo "$(YELLOW)This will:$(NC)"
	@echo "  • Clean existing environment"
	@echo "  • Setup Python version"
	@echo "  • Create virtual environment"
	@echo "  • Install all dependencies"
	@echo "  • Start database services"
	@echo "  • Apply database migrations"
	@echo ""
	@read -p "Continue? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(GREEN)Proceeding with fresh install...$(NC)"; \
		$(MAKE) install; \
		$(MAKE) docker-up; \
		@sleep 10; \
		cd apps && uv run $(MANAGE) migrate; \
		echo "$(GREEN)✅ Fresh environment setup complete!$(NC)"; \
		echo "$(BLUE)Your Django project is ready to run!$(NC)"; \
		echo "$(YELLOW)Run 'make run' to start the development server$(NC)"; \
	else \
		echo "$(YELLOW)Fresh install cancelled.$(NC)"; \
	fi

# Install dependencies and setup complete environment from scratch
install: python-check pyenv-setup venv
	@echo "$(GREEN)Installing dependencies...$(NC)"
	uv sync
	@echo "$(GREEN)✅ Dependencies installed successfully!$(NC)"
	@echo "$(BLUE)Environment setup complete!$(NC)"
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "  • Run 'make docker-up' to start database services"
	@echo "  • Run 'make migrate' to apply database migrations"
	@echo "  • Run 'make run' to start the development server"
	@echo "  • Or use 'make setup-dev' for complete setup including databases"

# Run Django development server
run:
	@echo "$(GREEN)Starting Django development server...$(NC)"
	cd apps && uv run $(MANAGE) runserver

# Run Django development server with debug
run-dev:
	@echo "$(GREEN)Starting Django development server with debug...$(NC)"
	cd apps && uv run $(MANAGE) runserver --verbosity=2

# Apply database migrations
migrate:
	@echo "$(GREEN)Applying database migrations...$(NC)"
	cd apps && uv run $(MANAGE) migrate

# Create new database migrations
makemigrations:
	@echo "$(GREEN)Creating new migrations...$(NC)"
	cd apps && uv run $(MANAGE) makemigrations

# Create Django superuser
superuser:
	@echo "$(GREEN)Creating Django superuser...$(NC)"
	cd apps && uv run $(MANAGE) createsuperuser

# Open Django shell
shell:
	@echo "$(GREEN)Opening Django shell...$(NC)"
	cd apps && uv run $(MANAGE) shell

# Run tests
test:
	@echo "$(GREEN)Running tests...$(NC)"
	cd apps && uv run $(MANAGE) test

# Run tests with coverage
test-coverage:
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	cd apps && uv run coverage run --source='.' $(MANAGE) test
	uv run coverage report
	uv run coverage html

# Clean Python cache files and environment
clean:
	@echo "$(GREEN)Cleaning environment...$(NC)"
	@echo "$(YELLOW)Removing Python cache files...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@echo "$(YELLOW)Removing virtual environment...$(NC)"
	@if [ -d "$(VENV_NAME)" ]; then \
		rm -rf $(VENV_NAME); \
		echo "$(GREEN)Virtual environment removed.$(NC)"; \
	else \
		echo "$(BLUE)No virtual environment found.$(NC)"; \
	fi
	@echo "$(GREEN)✅ Environment cleaned!$(NC)"

# Docker commands
docker-up:
	@echo "$(GREEN)Starting Docker services...$(NC)"
	$(DOCKER_COMPOSE) up -d

docker-down:
	@echo "$(GREEN)Stopping Docker services...$(NC)"
	$(DOCKER_COMPOSE) down

docker-logs:
	@echo "$(GREEN)Showing Docker logs...$(NC)"
	$(DOCKER_COMPOSE) logs -f

docker-restart:
	@echo "$(GREEN)Restarting Docker services...$(NC)"
	$(DOCKER_COMPOSE) restart

# Reset database (drop and recreate)
reset-db:
	@echo "$(RED)Warning: This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(GREEN)Resetting database...$(NC)"; \
		cd apps && uv run $(MANAGE) flush --no-input; \
		uv run $(MANAGE) migrate; \
		echo "$(GREEN)Database reset complete!$(NC)"; \
	else \
		echo "$(YELLOW)Database reset cancelled.$(NC)"; \
	fi

# Collect static files
collectstatic:
	@echo "$(GREEN)Collecting static files...$(NC)"
	cd apps && uv run $(MANAGE) collectstatic --no-input

# Run Django system check
check:
	@echo "$(GREEN)Running Django system check...$(NC)"
	cd apps && uv run $(MANAGE) check

# Development setup (install + migrate + create superuser)
setup-dev: install docker-up
	@echo "$(GREEN)Setting up development environment...$(NC)"
	@sleep 5  # Wait for database to be ready
	cd apps && uv run $(MANAGE) migrate
	@echo "$(GREEN)Development setup complete!$(NC)"
	@echo "$(YELLOW)Run 'make run' to start the development server$(NC)"

# Quick start (setup + run)
start: setup-dev
	@echo "$(GREEN)Starting development server...$(NC)"
	cd apps && uv run $(MANAGE) runserver 
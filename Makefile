# Stardog Cloud MCP Server Makefile

# Variables
PYTHON := python3
VENV := $(PWD)/venv
PIP := $(VENV)/bin/pip
PYTHON_SRC := stardog_cloud_mcp

YELLOW := \033[1;33m
GREEN := \033[1;32m
NC := \033[0m  # No Color

# Default target
.PHONY: help
help:
	@echo "$(GREEN)Stardog Cloud MCP Server Makefile$(NC)"
	@echo "$(YELLOW)Usage:$(NC)"
	@echo "  make help               Show this help message"
	@echo "  make install            Create virtual environment and install the package"
	@echo "  make install-dev        Install development dependencies"
	@echo "  make run                Run the MCP server (requires STARDOG_CLOUD_TOKEN)"
	@echo "  make format             Format code with black and isort"
	@echo "  make lint               Run linting checks with flake8"
	@echo "  make typecheck          Run type checking with mypy"
	@echo "  make test               Run tests with pytest"
	@echo "  make clean              Remove build artifacts and virtual environment"
	@echo "  make docker-build       Build the Docker image"
	@echo "  make docker-run         Run the server in Docker (requires STARDOG_CLOUD_TOKEN)"
	@echo "  make docker-compose     Run with docker-compose (requires STARDOG_CLOUD_TOKEN)"
	@echo "  make docker-stop        Stop docker-compose services"
	@echo "  make docker-clean       Remove Docker containers and images"
	@echo ""

# Setup and installation
$(VENV):
	@echo "$(GREEN)Creating virtual environment...$(NC)"
	@$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)Virtual environment created at $(VENV)$(NC)"

.PHONY: install
install: $(VENV)
	@echo "$(GREEN)Installing package...$(NC)"
	@$(PIP) install -e .
	@echo "$(GREEN)Package installed successfully!$(NC)"

# Run this before running tests or development tools
.PHONY: install-dev
install-dev: $(VENV)
	@echo "$(GREEN)Installing development dependencies...$(NC)"
	@$(PIP) install -e ".[dev]"
	@echo "$(GREEN)Development dependencies installed!$(NC)"

# Development tools
.PHONY: format-check
format-check:
	@echo "$(GREEN)Formatting code...$(NC)"
	isort --check-only $(PYTHON_SRC) && black --check $(PYTHON_SRC)
	@echo "$(GREEN)Code format check complete!$(NC)"

.PHONY: format
format:
	@echo "$(GREEN)Formatting code...$(NC)"
	black $(PYTHON_SRC) && isort $(PYTHON_SRC)
	@echo "$(GREEN)Code formatted!$(NC)"

.PHONY: lint
lint:
	@echo "$(GREEN)Running linter...$(NC)"
	flake8 $(PYTHON_SRC)
	@echo "$(GREEN)Linting complete!$(NC)"

.PHONY: typecheck
typecheck:
	@echo "$(GREEN)Running type checker...$(NC)"
	mypy $(PYTHON_SRC)
	@echo "$(GREEN)Type checking complete!$(NC)"

.PHONY: ci
ci:  format-check typecheck lint

.PHONY: test
test:
	@echo "$(GREEN)Running tests...$(NC)"
	@$(VENV)/bin/pytest tests --cov=$(PYTHON_SRC) --cov-report=term-missing
	@echo "$(GREEN)Tests complete!$(NC)"

.PHONY: clean
clean:
	@echo "$(GREEN)Cleaning up...$(NC)"
	@rm -rf $(VENV)
	@rm -rf .pytest_cache/
	@rm -rf .mypy_cache/
	@echo "$(GREEN)Cleanup complete!$(NC)"

# Docker targets
.PHONY: docker-build
docker-build:
	@echo "$(GREEN)Building Docker image...$(NC)"
	docker build --no-cache -t stardog-cloud-mcp .
	@echo "$(GREEN)Docker image built!$(NC)"

.PHONY: docker-up
docker-up:
	@echo "$(GREEN)Starting container with docker-compose...$(NC)"
	docker compose up

.PHONY: docker-stop
docker-stop:
	@echo "$(GREEN)Stopping docker-compose services...$(NC)"
	docker compose down
	@echo "$(GREEN)Services stopped!$(NC)"

.PHONY: docker-clean
docker-clean: docker-stop
	@echo "$(GREEN)Removing Docker containers and images...$(NC)"
	docker rmi stardog-cloud-mcp || true
	@echo "$(GREEN)Docker cleanup complete!$(NC)"


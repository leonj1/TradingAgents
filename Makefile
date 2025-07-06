# Makefile for TradingAgents
# A multi-agent LLM financial trading framework

# Variables
DOCKER_IMAGE_NAME = tradingagents
DOCKER_CONTAINER_NAME = tradingagents
COMPOSE_FILE = docker-compose.yml
ENV_FILE = .env

# Optional web interface port (not currently used, but available for future extensions)
PORT ?= 8000

# Colors for output
GREEN = \033[0;32m
YELLOW = \033[0;33m
RED = \033[0;31m
NC = \033[0m # No Color

# Detect docker compose command
DOCKER_COMPOSE := $(shell if command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; elif docker compose version >/dev/null 2>&1; then echo "docker compose"; else echo ""; fi)

# Check if docker compose is available
ifeq ($(DOCKER_COMPOSE),)
$(error Neither 'docker-compose' nor 'docker compose' command found. Please install Docker Compose.)
endif

# Default target
.DEFAULT_GOAL := help

# Show which docker compose command is being used
show-docker-info:
	@echo "$(GREEN)Using Docker Compose command: $(DOCKER_COMPOSE)$(NC)"

# Check if .env file exists
check-env:
	@if [ ! -f $(ENV_FILE) ]; then \
		echo "$(RED)Error: $(ENV_FILE) not found!$(NC)"; \
		echo "$(YELLOW)Creating $(ENV_FILE) from template...$(NC)"; \
		cp .env.example $(ENV_FILE); \
		echo "$(GREEN)Created $(ENV_FILE). Please edit it and add your API keys.$(NC)"; \
		exit 1; \
	fi

# Build the Docker image
.PHONY: build
build: check-env
	@echo "$(GREEN)Building Docker image using $(DOCKER_COMPOSE)...$(NC)"
	$(DOCKER_COMPOSE) build
	@echo "$(GREEN)Build complete!$(NC)"

# Start the services
.PHONY: start
start: check-env
	@echo "$(GREEN)Starting TradingAgents services...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)Services started!$(NC)"
	@echo "$(YELLOW)Run 'make logs' to view logs$(NC)"

# Stop the services
.PHONY: stop
stop:
	@echo "$(YELLOW)Stopping TradingAgents services...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)Services stopped!$(NC)"

# Restart the services
.PHONY: restart
restart: stop start
	@echo "$(GREEN)Services restarted!$(NC)"

# Run the interactive CLI
.PHONY: cli
cli: check-env
	@echo "$(GREEN)Starting TradingAgents CLI...$(NC)"
	$(DOCKER_COMPOSE) run --rm tradingagents cli

# Run analysis for a specific ticker
.PHONY: analyze
analyze: check-env
	@if [ -z "$(TICKER)" ] || [ -z "$(DATE)" ]; then \
		echo "$(RED)Error: TICKER and DATE are required!$(NC)"; \
		echo "$(YELLOW)Usage: make analyze TICKER=NVDA DATE=2024-05-10$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Analyzing $(TICKER) for $(DATE)...$(NC)"
	$(DOCKER_COMPOSE) run --rm tradingagents analyze $(TICKER) $(DATE)

# View logs
.PHONY: logs
logs:
	$(DOCKER_COMPOSE) logs -f

# View logs for specific service
.PHONY: logs-tradingagents
logs-tradingagents:
	$(DOCKER_COMPOSE) logs -f tradingagents

.PHONY: logs-redis
logs-redis:
	$(DOCKER_COMPOSE) logs -f redis

# Shell access to the container
.PHONY: shell
shell: check-env
	@echo "$(GREEN)Opening shell in TradingAgents container...$(NC)"
	$(DOCKER_COMPOSE) run --rm tradingagents bash

# Run Python script
.PHONY: python
python: check-env
	@if [ -z "$(SCRIPT)" ]; then \
		echo "$(GREEN)Running main.py...$(NC)"; \
		$(DOCKER_COMPOSE) run --rm tradingagents python main.py; \
	else \
		echo "$(GREEN)Running $(SCRIPT)...$(NC)"; \
		$(DOCKER_COMPOSE) run --rm tradingagents python $(SCRIPT); \
	fi

# Clean up containers and volumes
.PHONY: clean
clean:
	@echo "$(YELLOW)Cleaning up containers and volumes...$(NC)"
	$(DOCKER_COMPOSE) down -v
	@echo "$(GREEN)Cleanup complete!$(NC)"

# Remove Docker image
.PHONY: clean-image
clean-image: clean
	@echo "$(YELLOW)Removing Docker image...$(NC)"
	docker rmi $(DOCKER_IMAGE_NAME):latest || true
	@echo "$(GREEN)Image removed!$(NC)"

# Full cleanup (containers, volumes, and images)
.PHONY: clean-all
clean-all: clean-image
	@echo "$(GREEN)Full cleanup complete!$(NC)"

# Show container status
.PHONY: status
status:
	@echo "$(GREEN)Container Status:$(NC)"
	@$(DOCKER_COMPOSE) ps

# Run tests (placeholder for when tests are added)
.PHONY: test
test: check-env
	@echo "$(YELLOW)No tests configured yet.$(NC)"
	@echo "$(YELLOW)To add tests, create a tests/ directory and update this target.$(NC)"

# Lint code (placeholder for when linting is configured)
.PHONY: lint
lint:
	@echo "$(YELLOW)No linting configured yet.$(NC)"
	@echo "$(YELLOW)Consider adding flake8, black, or ruff for code quality.$(NC)"

# Pull latest changes and rebuild
.PHONY: update
update:
	@echo "$(GREEN)Pulling latest changes...$(NC)"
	git pull
	@echo "$(GREEN)Rebuilding Docker image...$(NC)"
	$(MAKE) build
	@echo "$(GREEN)Update complete!$(NC)"

# Export environment template
.PHONY: env-template
env-template:
	@echo "$(GREEN)Creating .env.example template...$(NC)"
	@if [ -f .env.example ]; then \
		echo "$(YELLOW).env.example already exists$(NC)"; \
	else \
		echo "$(RED).env.example not found$(NC)"; \
	fi

# Help target
.PHONY: help
help:
	@echo "$(GREEN)TradingAgents Makefile$(NC)"
	@echo ""
	@echo "$(YELLOW)Available targets:$(NC)"
	@echo "  $(GREEN)build$(NC)            - Build Docker image"
	@echo "  $(GREEN)start$(NC)            - Start services in background"
	@echo "  $(GREEN)stop$(NC)             - Stop running services"
	@echo "  $(GREEN)restart$(NC)          - Restart services"
	@echo "  $(GREEN)cli$(NC)              - Run interactive CLI"
	@echo "  $(GREEN)analyze$(NC)          - Analyze ticker (TICKER=NVDA DATE=2024-05-10)"
	@echo "  $(GREEN)logs$(NC)             - View all logs"
	@echo "  $(GREEN)logs-tradingagents$(NC) - View tradingagents logs"
	@echo "  $(GREEN)logs-redis$(NC)       - View Redis logs"
	@echo "  $(GREEN)shell$(NC)            - Open bash shell in container"
	@echo "  $(GREEN)python$(NC)           - Run Python script (SCRIPT=path/to/script.py)"
	@echo "  $(GREEN)status$(NC)           - Show container status"
	@echo "  $(GREEN)clean$(NC)            - Remove containers and volumes"
	@echo "  $(GREEN)clean-image$(NC)      - Remove containers, volumes, and image"
	@echo "  $(GREEN)clean-all$(NC)        - Full cleanup"
	@echo "  $(GREEN)update$(NC)           - Pull latest changes and rebuild"
	@echo "  $(GREEN)test$(NC)             - Run tests (when available)"
	@echo "  $(GREEN)lint$(NC)             - Run linting (when configured)"
	@echo "  $(GREEN)help$(NC)             - Show this help message"
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make build"
	@echo "  make cli"
	@echo "  make analyze TICKER=AAPL DATE=2024-05-15"
	@echo "  make python SCRIPT=main.py"
	@echo ""
	@echo "$(YELLOW)Note:$(NC) PORT variable available for future web interface (default: $(PORT))"
	@echo ""
	@echo "$(YELLOW)Docker Compose:$(NC) This Makefile supports both 'docker-compose' and 'docker compose' commands"
	@echo "                Currently using: $(GREEN)$(DOCKER_COMPOSE)$(NC)"

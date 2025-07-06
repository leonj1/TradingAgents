# Makefile for Meta-Agent System
SHELL := /bin/bash

# Variables
IMAGE_NAME = meta-agent
CONTAINER_NAME = meta-agent-container
DOCKERFILE = Dockerfile.metaagent
PORT = 8000

# Colors for output
GREEN = \033[0;32m
YELLOW = \033[0;33m
RED = \033[0;31m
NC = \033[0m # No Color

# Detect docker compose command (from main Makefile pattern)
DOCKER_COMPOSE := $(shell if command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; elif docker compose version >/dev/null 2>&1; then echo "docker compose"; else echo ""; fi)

# Default target
.DEFAULT_GOAL := help

# Check if API key is set
check-api-key:
	@if [ -z "$$OPENAI_API_KEY" ]; then \
		echo "$(RED)Warning: OPENAI_API_KEY environment variable is not set$(NC)"; \
		echo "$(YELLOW)Set it with: export OPENAI_API_KEY=your-api-key$(NC)"; \
	fi

# Build the Docker image
.PHONY: build
build: check-api-key
	@echo "$(GREEN)Building Meta-Agent Docker image...$(NC)"
	@echo "$(YELLOW)Context: Current directory ($(shell pwd))$(NC)"
	docker build -f $(DOCKERFILE) -t $(IMAGE_NAME):latest .
	@echo "$(GREEN)Build complete!$(NC)"

# Run CLI in interactive mode
.PHONY: run-cli
run-cli: check-api-key
	@echo "$(GREEN)Starting Meta-Agent CLI...$(NC)"
	docker run -it --rm \
		--name $(CONTAINER_NAME)-cli \
		-e OPENAI_API_KEY="$$OPENAI_API_KEY" \
		-v $(PWD)/results:/app/results \
		$(IMAGE_NAME):latest \
		python -m meta_agent.interfaces.cli interactive

# Run CLI with a specific topic
.PHONY: analyze
analyze: check-api-key
	@if [ -z "$(TOPIC)" ]; then \
		echo "$(RED)Error: TOPIC is required!$(NC)"; \
		echo "$(YELLOW)Usage: make analyze TOPIC=\"Your topic here\"$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Analyzing topic: $(TOPIC)$(NC)"
	docker run --rm \
		--name $(CONTAINER_NAME)-analyze \
		-e OPENAI_API_KEY="$$OPENAI_API_KEY" \
		-v $(PWD)/results:/app/results \
		$(IMAGE_NAME):latest \
		python -m meta_agent.interfaces.cli analyze "$(TOPIC)"

# Run the FastAPI server
.PHONY: run-api
run-api: check-api-key
	@echo "$(GREEN)Starting Meta-Agent API server on port $(PORT)...$(NC)"
	docker run -it --rm \
		--name $(CONTAINER_NAME)-api \
		-e OPENAI_API_KEY="$$OPENAI_API_KEY" \
		-p $(PORT):8000 \
		-v $(PWD)/results:/app/results \
		$(IMAGE_NAME):latest \
		python -m meta_agent.interfaces.api

# Run the demo script
.PHONY: run-demo
run-demo: check-api-key
	@echo "$(GREEN)Running Meta-Agent demo...$(NC)"
	docker run -it --rm \
		--name $(CONTAINER_NAME)-demo \
		-e OPENAI_API_KEY="$$OPENAI_API_KEY" \
		-v $(PWD)/results:/app/results \
		$(IMAGE_NAME):latest \
		python -m meta_agent.examples.topic_response_demo

# Run the cooking domain example
.PHONY: run-cooking
run-cooking: check-api-key
	@echo "$(GREEN)Running cooking domain example...$(NC)"
	docker run -it --rm \
		--name $(CONTAINER_NAME)-cooking \
		-e OPENAI_API_KEY="$$OPENAI_API_KEY" \
		-v $(PWD)/results:/app/results \
		$(IMAGE_NAME):latest \
		python -m meta_agent.examples.cooking_domain

# Open a shell in the container
.PHONY: shell
shell:
	@echo "$(GREEN)Opening shell in Meta-Agent container...$(NC)"
	docker run -it --rm \
		--name $(CONTAINER_NAME)-shell \
		-e OPENAI_API_KEY="$$OPENAI_API_KEY" \
		-v $(PWD)/results:/app/results \
		-v $(PWD)/meta_agent:/app/meta_agent \
		--entrypoint /bin/bash \
		$(IMAGE_NAME):latest

# Run tests
.PHONY: test
test:
	@echo "$(GREEN)Running Meta-Agent tests...$(NC)"
	docker run -it --rm \
		--name $(CONTAINER_NAME)-test \
		-v $(PWD)/results:/app/results \
		$(IMAGE_NAME):latest \
		python -m pytest meta_agent/tests/ -v

# Test OpenAI connection
.PHONY: test-openai
test-openai: check-api-key
	@echo "$(GREEN)Testing OpenAI connection...$(NC)"
	docker run -it --rm \
		--name $(CONTAINER_NAME)-test-openai \
		-e OPENAI_API_KEY="$$OPENAI_API_KEY" \
		$(IMAGE_NAME):latest \
		python /app/meta_agent/test_openai_connection.py

# Show logs from running container
.PHONY: logs
logs:
	@echo "$(GREEN)Showing logs from Meta-Agent container...$(NC)"
	docker logs -f $(CONTAINER_NAME)-api || docker logs -f $(CONTAINER_NAME)-cli || echo "$(RED)No running container found$(NC)"

# Stop running containers
.PHONY: stop
stop:
	@echo "$(YELLOW)Stopping Meta-Agent containers...$(NC)"
	@docker stop $(CONTAINER_NAME)-api 2>/dev/null || true
	@docker stop $(CONTAINER_NAME)-cli 2>/dev/null || true
	@docker stop $(CONTAINER_NAME)-demo 2>/dev/null || true
	@echo "$(GREEN)Containers stopped$(NC)"

# Clean up containers and images
.PHONY: clean
clean: stop
	@echo "$(YELLOW)Cleaning up Meta-Agent containers...$(NC)"
	@docker rm -f $$(docker ps -a -q -f name=$(CONTAINER_NAME)) 2>/dev/null || true
	@echo "$(GREEN)Cleanup complete$(NC)"

# Remove the Docker image
.PHONY: clean-image
clean-image: clean
	@echo "$(YELLOW)Removing Meta-Agent Docker image...$(NC)"
	@docker rmi $(IMAGE_NAME):latest 2>/dev/null || true
	@echo "$(GREEN)Image removed$(NC)"

# Show running containers
.PHONY: ps
ps:
	@echo "$(GREEN)Meta-Agent containers:$(NC)"
	@docker ps -a --filter name=$(CONTAINER_NAME) --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Development mode - mount source code
.PHONY: dev
dev: check-api-key
	@echo "$(GREEN)Starting Meta-Agent in development mode...$(NC)"
	docker run -it --rm \
		--name $(CONTAINER_NAME)-dev \
		-e OPENAI_API_KEY="$$OPENAI_API_KEY" \
		-v $(PWD)/meta_agent:/app/meta_agent \
		-v $(PWD)/results:/app/results \
		-p $(PORT):8000 \
		$(IMAGE_NAME):latest \
		/bin/bash

# Help target
.PHONY: help
help:
	@echo "$(GREEN)Meta-Agent Docker Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)Build & Run:$(NC)"
	@echo "  $(GREEN)make build$(NC)           - Build the Docker image"
	@echo "  $(GREEN)make run-cli$(NC)         - Run interactive CLI"
	@echo "  $(GREEN)make run-api$(NC)         - Run FastAPI server (port $(PORT))"
	@echo "  $(GREEN)make analyze TOPIC=\"...\"$(NC) - Analyze a specific topic"
	@echo ""
	@echo "$(YELLOW)Examples & Testing:$(NC)"
	@echo "  $(GREEN)make run-demo$(NC)        - Run the demo script"
	@echo "  $(GREEN)make run-cooking$(NC)     - Run cooking domain example"
	@echo "  $(GREEN)make test$(NC)            - Run tests"
	@echo ""
	@echo "$(YELLOW)Development:$(NC)"
	@echo "  $(GREEN)make shell$(NC)           - Open shell in container"
	@echo "  $(GREEN)make dev$(NC)             - Development mode with mounted code"
	@echo "  $(GREEN)make logs$(NC)            - Show container logs"
	@echo ""
	@echo "$(YELLOW)Management:$(NC)"
	@echo "  $(GREEN)make ps$(NC)              - Show running containers"
	@echo "  $(GREEN)make stop$(NC)            - Stop all containers"
	@echo "  $(GREEN)make clean$(NC)           - Remove containers"
	@echo "  $(GREEN)make clean-image$(NC)     - Remove containers and image"
	@echo ""
	@echo "$(YELLOW)Environment:$(NC)"
	@echo "  Required: export OPENAI_API_KEY=your-api-key"
	@echo "  Optional: PORT=8000 (default)"
.PHONY: help install lint format check test clean lint-frontend format-frontend format-check-frontend type-check-frontend check-frontend check-all

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -r requirements.txt

lint:  ## Run Ruff linter
	ruff check api/ test_local.py

lint-fix:  ## Run Ruff linter with auto-fix
	ruff check --fix api/ test_local.py

format:  ## Format code with Ruff
	ruff format api/ test_local.py

format-check:  ## Check code formatting without making changes
	ruff format --check api/ test_local.py

check: lint format-check  ## Run all backend checks (lint + format check)

# === Frontend Commands ===

lint-frontend:  ## Run ESLint for frontend
	bun run lint

lint-fix-frontend:  ## Run ESLint with auto-fix for frontend
	bun run lint:fix

format-frontend:  ## Format frontend code with Prettier
	bun run format

format-check-frontend:  ## Check frontend code formatting without making changes
	bun run format:check

type-check-frontend:  ## Run TypeScript type checking
	bun run type-check

check-frontend: lint-frontend format-check-frontend type-check-frontend  ## Run all frontend checks

check-all: check check-frontend  ## Run all checks (backend + frontend)

test:  ## Run local test
	python test_local.py "Nike"

clean:  ## Clean cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -f results.json

dev:  ## Start development server (local)
	uvicorn api.index:app --reload --host 127.0.0.1 --port 8000

# === Docker Commands ===

docker-build:  ## Build Docker images
	docker-compose build

docker-build-api:  ## Build only API Docker image
	docker-compose build api

docker-build-frontend:  ## Build only Frontend Docker image
	docker-compose build frontend

docker-up:  ## Start services with Docker Compose
	docker-compose up -d

docker-down:  ## Stop services
	docker-compose down

docker-logs:  ## Show logs (all services)
	docker-compose logs -f

docker-logs-api:  ## Show API logs
	docker-compose logs -f api

docker-logs-frontend:  ## Show Frontend logs
	docker-compose logs -f frontend

docker-restart:  ## Restart services
	docker-compose restart

docker-restart-api:  ## Restart API service
	docker-compose restart api

docker-restart-frontend:  ## Restart Frontend service
	docker-compose restart frontend

docker-clean:  ## Clean all containers, volumes, and images
	docker-compose down -v --rmi all

docker-shell:  ## Open shell in API container
	docker-compose exec api /bin/bash

docker-shell-frontend:  ## Open shell in Frontend container
	docker-compose exec frontend /bin/sh

docker-test:  ## Run tests in container
	docker-compose exec api python test_local.py "Nike"


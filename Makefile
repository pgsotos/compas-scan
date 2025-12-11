.PHONY: help install lint format check test clean lint-frontend format-frontend format-check-frontend type-check-frontend check-frontend check-all dev-up dev-down dev-logs dev-shell dev-test

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# === Development (Docker-First) ===

dev-up:  ## 🚀 Start complete development environment (Docker)
	docker-compose up -d --build
	@echo "✅ Development environment started!"
	@echo "🌐 Frontend: http://localhost:3000"
	@echo "🔧 Backend:  http://localhost:8000"
	@echo "📊 Redis:    redis://localhost:6379"

dev-down:  ## 🛑 Stop development environment
	docker-compose down
	@echo "✅ Development environment stopped!"

dev-logs:  ## 📋 Show all logs
	docker-compose logs -f

dev-logs-backend:  ## 📋 Show backend logs
	docker-compose logs -f backend

dev-logs-frontend:  ## 📋 Show frontend logs
	docker-compose logs -f frontend

dev-shell-backend:  ## 🐚 Open shell in backend container
	docker-compose exec backend /bin/bash

dev-shell-frontend:  ## 🐚 Open shell in frontend container
	docker-compose exec frontend /bin/sh

dev-restart:  ## 🔄 Restart all services
	docker-compose restart
	@echo "✅ Services restarted!"

dev-test:  ## 🧪 Run tests in development environment
	docker-compose exec backend python tests/test_local.py "Nike"

dev-clean:  ## 🧹 Clean all Docker resources
	docker-compose down -v --rmi all
	docker system prune -f
	@echo "✅ Docker environment cleaned!"

# === Backend Commands ===

install-backend:  ## Install backend dependencies (for local development)
	cd backend && pip install -r requirements.txt

lint-backend:  ## Run Ruff linter for backend
	ruff check backend/src/ backend/tests/

lint-fix-backend:  ## Run Ruff linter with auto-fix for backend
	ruff check --fix backend/src/ backend/tests/

format-backend:  ## Format backend code with Ruff
	ruff format backend/src/ backend/tests/

format-check-backend:  ## Check backend code formatting
	ruff format --check backend/src/ backend/tests/

check-backend: lint-backend format-check-backend  ## Run all backend checks

test-backend:  ## Run backend tests
	cd backend && python -m pytest tests/ -v

# === Frontend Commands ===

install-frontend:  ## Install frontend dependencies (for local development)
	cd frontend && bun install

lint-frontend:  ## Run ESLint for frontend
	cd frontend && bun run lint

lint-fix-frontend:  ## Run ESLint with auto-fix for frontend
	cd frontend && bun run lint:fix

format-frontend:  ## Format frontend code with Prettier
	cd frontend && bun run format

format-check-frontend:  ## Check frontend code formatting
	cd frontend && bun run format:check

type-check-frontend:  ## Run TypeScript type checking
	cd frontend && bun run type-check

check-frontend: lint-frontend format-check-frontend type-check-frontend  ## Run all frontend checks

test-frontend:  ## Run frontend tests
	cd frontend && bun run test

# === Combined Commands ===

install: install-backend install-frontend  ## Install all dependencies

check: check-backend check-frontend  ## Run all checks (backend + frontend)

test: test-backend test-frontend  ## Run all tests

clean:  ## Clean cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	rm -f results.json
	@echo "✅ Cache and temporary files cleaned!"

# === Legacy Commands (Deprecated) ===

dev:  ## ⚠️  Deprecated: Use 'dev-up' instead
	@echo "⚠️  'dev' is deprecated. Use 'dev-up' for Docker-first development!"
	@echo "💡 Run 'make dev-up' to start the complete environment."

docker-up: dev-up  ## Alias for dev-up
docker-down: dev-down  ## Alias for dev-down
docker-logs: dev-logs  ## Alias for dev-logs
docker-test: dev-test  ## Alias for dev-test


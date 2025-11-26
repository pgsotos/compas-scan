.PHONY: help install lint format check test clean

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

check: lint format-check  ## Run all checks (lint + format check)

test:  ## Run local test
	python test_local.py "Nike"

clean:  ## Clean cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -f results.json

dev:  ## Start development server
	uvicorn api.index:app --reload --host 127.0.0.1 --port 8000


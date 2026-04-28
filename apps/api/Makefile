# =====================================================================
# AI Travel Planner - Makefile
# Cross-platform: works with GNU Make on macOS/Linux/WSL.
# Windows users without Make: use `invoke <task>` (see tasks.py).
# =====================================================================

.PHONY: help install install-dev run dev test test-cov lint format type \
        precommit clean check ci

PY ?= python
PIP ?= $(PY) -m pip

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install runtime dependencies
	$(PIP) install -r requirements.txt

install-dev: ## Install runtime + dev dependencies (run `pre-commit install` from repo root)
	$(PIP) install -r requirements-dev.txt
	@echo "Tip: from repo root run  pre-commit install  (hooks live at project root)."

run: ## Run the API server (production-style, single worker)
	uvicorn app.main:app --host 0.0.0.0 --port 8000

dev: ## Run the API server with auto-reload for development
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

test: ## Run the test suite
	pytest

test-cov: ## Run the test suite with coverage report
	pytest --cov=app --cov-report=term-missing --cov-report=html

lint: ## Run the linter (ruff)
	ruff check . ../../packages

format: ## Auto-format the code (ruff)
	ruff format . ../../packages
	ruff check --fix . ../../packages

type: ## Run static type checking (mypy)
	mypy app

precommit: ## Run all pre-commit hooks (must be run from repository root)
	cd ../.. && pre-commit run --all-files

check: lint type test ## Lint + type-check + test (used by CI)

clean: ## Remove caches and build artefacts
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

ci: check ## Alias for `check`, used by GitHub Actions

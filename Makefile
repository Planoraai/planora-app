# =====================================================================
# AI Travel Planner — Monorepo root Makefile
#
# API (Python/FastAPI):    apps/api/
# Web (Next.js):           apps/web/
# Reusable packages:       packages/{platform, domain_contracts, orchestrator,
#                                    tools, agents/*, memory, reliability}/
#
# All Python lint/test/type targets delegate to apps/api/Makefile.
# =====================================================================

.PHONY: help api-install api-install-dev api-dev api-test \
        api-lint api-format api-type api-check \
        web-dev hooks

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ---- API (apps/api) -------------------------------------------------
api-install: ## Install API runtime dependencies
	$(MAKE) -C apps/api install

api-install-dev: ## Install API dev deps + remind about pre-commit
	$(MAKE) -C apps/api install-dev

api-dev: ## Run FastAPI with reload (port 8000)
	$(MAKE) -C apps/api dev

api-test: ## Run pytest suite (api + every packages/* test)
	$(MAKE) -C apps/api test

api-lint: ## Ruff check (api + packages)
	$(MAKE) -C apps/api lint

api-format: ## Ruff format (api + packages)
	$(MAKE) -C apps/api format

api-type: ## Mypy
	$(MAKE) -C apps/api type

api-check: ## Lint + type + test (same as CI)
	$(MAKE) -C apps/api check

hooks: ## Install pre-commit hooks (run once from repo root)
	pre-commit install

# ---- Web (apps/web) -------------------------------------------------
web-dev: ## Next.js dev server
	cd apps/web && npm run dev

.PHONY: help install hooks-update hooks-run secrets-scan secrets-audit completion

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies and setup pre-commit hooks
	uv sync --extra dev
	uv run pre-commit install
	$(MAKE) hooks-update

hooks-update: ## Update pre-commit hooks to latest versions
	uv run pre-commit autoupdate

hooks-run: ## Run all pre-commit hooks on all files
	uv run pre-commit run --all-files

secrets-scan: ## Scan for secrets in the codebase
	@if [ ! -f .secrets.baseline ]; then \
		echo "Creating new baseline..."; \
		uv run detect-secrets scan | tee .secrets.baseline; \
	else \
		echo "Updating existing baseline..."; \
		uv run detect-secrets scan --baseline .secrets.baseline; \
	fi

secrets-audit: ## Interactively review detected secrets
	uv run detect-secrets audit .secrets.baseline

completion: ## Regenerate zsh completion script
	uv run python scripts/generate-completion.py
	hal sync

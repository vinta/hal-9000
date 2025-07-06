.PHONY: help install hooks-update hooks-run secrets-scan secrets-audit

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:
	pip install -r requirements.txt
	pre-commit install
	$(MAKE) hooks-update

hooks-update: ## Update pre-commit hooks to latest versions
	pre-commit autoupdate

hooks-run: ## Run all pre-commit hooks on all files
	pre-commit run --all-files

secrets-scan: ## Scan for secrets in the codebase
	@if [ ! -f .secrets.baseline ]; then \
		echo "Creating new baseline..."; \
		detect-secrets scan | tee .secrets.baseline; \
	else \
		echo "Updating existing baseline..."; \
		detect-secrets scan --baseline .secrets.baseline; \
	fi

secrets-audit: ## Interactively review detected secrets
	detect-secrets audit .secrets.baseline


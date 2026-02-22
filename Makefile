.PHONY: help install lint format typecheck update-hooks run-hooks scan-secrets run-gitleaks run-detect-secrets audit-detect-secrets-report hal-completion

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies and setup pre-commit hooks
	uv sync
	uv run pip-audit
	uv run ansible-galaxy collection install community.general
	uv run pre-commit install
	HOMEBREW_NO_AUTO_UPDATE=1 brew install gitleaks
	$(MAKE) update-hooks

lint: ## Run ruff linter, formatter check, and ansible-lint
	uv run ruff format --check .
	uv run ruff check .
	uv run ansible-lint playbooks/
	cd playbooks && ansible-playbook site.yml --syntax-check

format: ## Auto-format and fix lint issues
	uv run ruff format .
	uv run ruff check --fix .

typecheck: ## Run ty type checker
	uv run ty check bin/hal

update-hooks: ## Update pre-commit hooks to latest versions
	uv run pre-commit autoupdate

run-hooks: ## Run all pre-commit hooks on all files
	uv run pre-commit run --all-files

scan-secrets: run-gitleaks run-detect-secrets  ## Scan for secrets using all scanners

run-gitleaks: ## Scan full git history for secrets
	gitleaks git . --verbose --no-banner

run-detect-secrets: ## Scan for secrets in the codebase
	@if [ ! -f .secrets.baseline ]; then \
		echo "Creating new baseline..."; \
		uv run detect-secrets scan | tee .secrets.baseline; \
	else \
		echo "Updating existing baseline..."; \
		uv run detect-secrets scan --baseline .secrets.baseline; \
	fi

audit-detect-secrets-report: ## Interactively review detected secrets
	uv run detect-secrets audit .secrets.baseline

hal-completion: ## Regenerate zsh completion script for hal
	uv run python scripts/generate-completion.py
	hal sync

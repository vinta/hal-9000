.PHONY: help install lint lint-python lint-ansible format test update-hooks run-hooks scan-secrets run-gitleaks run-detect-secrets audit-detect-secrets-report hal-completion

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-35s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies and setup pre-commit hooks
	uv sync --locked
	uv audit
	ansible-galaxy install -r playbooks/collections/requirements.yml
	uv run pre-commit install
	@if command -v gitleaks >/dev/null 2>&1; then \
		echo "gitleaks already installed"; \
	else \
		HOMEBREW_NO_AUTO_UPDATE=1 brew install --quiet gitleaks; \
	fi
	$(MAKE) update-hooks

lint: lint-python lint-ansible ## Run all linters

lint-python: ## Run ruff formatter check, linter, type checker, and system python3 compatibility check
	uv run ruff format --check .
	uv run ruff check .
	uv run ty check
	uv run vermin -t=3.9 --eval-annotations --no-parse-comments --no-tips --exclude 'typing.NotRequired' \
		bin/hal.py \
		dotfiles/.claude/hooks/guard-bash-paths.py \
		plugins/hal-statusline/hal-statusline.py \
		plugins/hal-session-auto-rename/scripts/hal-session-auto-rename.py \
		plugins/hal-voice/scripts/hal-voice.py

lint-ansible: ## Run ansible-lint and a playbook syntax check
	uv run ansible-lint playbooks/
	cd playbooks && ansible-playbook site.yml --syntax-check

format: ## Auto-format and fix lint issues
	uv run ruff format .
	uv run ruff check --fix .

test: ## Run tests
	uv run pytest -v

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

.PHONY: help install lint lint-python lint-ansible format test scan-secrets scan-secrets-history hal-completion

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-35s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies and setup pre-commit hooks
	uv sync --locked
	uv audit
	ansible-galaxy install -r playbooks/collections/requirements.yml
	HOMEBREW_NO_AUTO_UPDATE=1 brew install --quiet betterleaks
	uv run pre-commit install
	uv run pre-commit autoupdate

lint: lint-python lint-ansible ## Run all linters

lint-python: ## Run ruff formatter check, linter, type checker, and system python3 compatibility check
	uv run ruff format --check .
	uv run ruff check .
	uv run ty check
	uv run vermin -t=3.9 --eval-annotations --no-parse-comments --no-tips --hidden --exclude 'typing.NotRequired' bin/ dotfiles/ plugins/ skills/

lint-ansible: ## Run ansible-lint and a playbook syntax check
	uv run ansible-lint playbooks/
	cd playbooks && ansible-playbook site.yml --syntax-check

format: ## Auto-format and fix lint issues
	uv run ruff format .
	uv run ruff check --fix .

test: ## Run tests
	uv run pytest -v

scan-secrets: ## Scan the working tree for secrets
	betterleaks dir . --verbose --no-banner

scan-secrets-history: ## Scan full git history for secrets
	betterleaks git . --verbose --no-banner

hal-completion: ## Regenerate zsh completion script for hal
	uv run python scripts/generate-zsh-completion.py

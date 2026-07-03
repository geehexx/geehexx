.PHONY: install hooks build profile resume qa compare lint policy secrets format test check clean

install:
	uv sync --extra dev

hooks:
	uv run pre-commit install --install-hooks
	command -v lefthook >/dev/null 2>&1 && lefthook install || true

build:
	uv run profile-cv build --clean

profile:
	uv run profile-cv render-profile --check

resume:
	uv run profile-cv build --clean --no-profile-check

qa:
	uv run profile-cv qa

compare:
	uv run profile-cv compare-themes

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy

test:
	uv run pytest

policy:
	$(MAKE) secrets
	uvx --from actionlint-py actionlint
	uvx check-jsonschema --builtin-schema vendor.github-workflows .github/workflows/ci.yml .github/workflows/profile-drift.yml
	uvx check-jsonschema --builtin-schema custom.github-workflows-require-timeout .github/workflows/ci.yml .github/workflows/profile-drift.yml
	uvx check-jsonschema --builtin-schema vendor.dependabot .github/dependabot.yml
	uvx yamllint .github/dependabot.yml .github/workflows quality-gates.yaml resume.yaml .yamllint.yml
	uvx zizmor --format plain .
	uv run python scripts/check_workflows.py
	uv run python scripts/check_public_surface.py
	uv run python scripts/lint_readme.py README.md

secrets:
	git ls-files -z | xargs -0 uv run --with detect-secrets detect-secrets-hook --exclude-files '^(vendor/typst/)'

check: lint test policy build

format:
	uv run ruff format .
	uv run ruff check . --fix

clean:
	rm -rf dist site _qa_pdf _qa_docx .pytest_cache .ruff_cache .mypy_cache

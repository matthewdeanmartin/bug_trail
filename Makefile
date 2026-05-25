# Root Makefile for bug-trail-workspace

.PHONY: sync test lint clean update-about

sync:
	uv sync

test:
	uv run pytest packages

lint:
	uv run ruff check packages
	uv run mypy packages

clean:
	rm -rf .venv .pytest_cache .mypy_cache .ruff_cache docs_api site
	$(MAKE) -C packages/bug-trail-core clean
	$(MAKE) -C packages/bug-trail clean

update-about:
	uv run metametameta pep621 --source packages/bug-trail-core/pyproject.toml --output packages/bug-trail-core/src/bug_trail_core/__about__.py
	uv run metametameta pep621 --source packages/bug-trail/pyproject.toml --output packages/bug-trail/src/bug_trail/__about__.py

docs:
	rm -rf docs_api site
	mkdir -p docs_api
	PYTHONPATH="packages/bug-trail-core/src;packages/bug-trail/src" uv run pdoc --html --output-dir docs_api bug_trail_core bug_trail --force
	uv run zensical build

# ── Dogfooding targets (independent, not wired into check) ───────────────────

.PHONY: version-check
version-check:
	@uv run jiggle_version check

.PHONY: dev-status
dev-status:
	@uv run troml-dev-status validate .

.PHONY: prerelease-check
prerelease-check: version-check dev-status
	@echo "Pre-release checks passed."

.PHONY: dont-be-lazy
dont-be-lazy:
	@uv run dont_be_lazy --root . --no-color summary
	@uv run dont_be_lazy --root . --no-color scan bug_trail --no-config-suppressions || true

.PHONY: pydoc-docs
pydoc-docs:
	@uv run pydoc_fork bug_trail -o ./pydoc/

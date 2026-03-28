# Makefile for bug-trail

.PHONY: test lint clean

test:
	uv run pytest tests

lint:
	uv run ruff check src
	uv run mypy src

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache

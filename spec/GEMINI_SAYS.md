# Architectural Review & Migration Plan: Bug Trail Monorepo

## Status: Phases 1 & 2 Complete ✅
*   **uv Workspaces**: Implemented. Root `pyproject.toml` manages `packages/*`.
*   **Source Migration**: `bug_trail` and `bug_trail_core` moved to `packages/` with `src/` layout.
*   **Tests Distributed**: Tests moved to respective package directories.
*   **Tooling**: `metametameta` integrated for `__about__.py` synchronization.
*   **Makefiles**: Scoped `Makefile`s added to root and each package.

---

## Overview
`bug_trail` is a dual-component project consisting of a core logging library (`bug_trail_core`) and a static HTML log viewer (`bug_trail`).

The goal is a formal **monorepo structure** using **uv workspaces**, allowing for easier local development, shared tooling, and independent publishing to PyPI.

---

## Modernization Goals
1.  **Unified Tooling**: Migrate all linting, formatting, and type-checking to **Ruff** and **MyPy** (root-level config).
2.  **uv Workspaces**: Leverage `uv` for lightning-fast dependency management and workspace isolation.
3.  **Standardized Layout**: Use the `src/` layout for both packages to prevent accidental imports and ensure clean packaging.
4.  **CI/CD Automation**: Dual-package build and test pipelines with automated PyPI publishing.
5.  **Modern Python**: Target Python 3.12+ features.
6.  **Synchronized Releases**: Both packages will be versioned and released together to maintain compatibility.
7.  **Metadata Management**: Use `metametameta` to keep `__about__.py` files in sync with `pyproject.toml`.

---

## Proposed Structure
```text
/
├── pyproject.toml (Root Workspace)
├── uv.lock
├── Makefile (Workspace-wide tasks)
├── packages/
│   ├── bug-trail-core/
│   │   ├── pyproject.toml
│   │   ├── src/bug_trail_core/
│   │   ├── tests/
│   │   └── Makefile (Scoped tasks)
│   └── bug-trail/
│       ├── pyproject.toml
│       ├── src/bug_trail/
│       ├── tests/
│       └── Makefile (Scoped tasks)
└── .github/workflows/
```

---

## Phased Implementation Plan

### Phase 1: Workspace Scaffolding (Smart) - DONE ✅
*   **Goal**: Establish the monorepo structure.
*   **Tasks**:
    1.  Create `packages/` directory.
    2.  Initialize `packages/bug-trail-core/pyproject.toml`.
    3.  Initialize `packages/bug-trail/pyproject.toml`.
    4.  Update root `pyproject.toml` to `[tool.uv.workspace]` mode.
    5.  Run `uv sync` to verify environment.

### Phase 2: Source Migration (Ordinary) - DONE ✅
*   **Goal**: Move files to the new layout.
*   **Tasks**:
    1.  Move `bug_trail_core/` to `packages/bug-trail-core/src/bug_trail_core/`.
    2.  Move `bug_trail/` to `packages/bug-trail/src/bug_trail/`.
    3.  Distribute existing `tests/` to their respective package directories.
    4.  Fix any resource loading issues.
    5.  Update `__about__.py` using `metametameta`.

### Phase 3: Tooling Consolidation (Ordinary) - IN PROGRESS
*   **Goal**: Standardize on modern tools.
*   **Tasks**:
    1.  Consolidate `black`, `isort`, and `pylint` configurations into a single `ruff.toml` or root `pyproject.toml`.
    2.  Update `Makefile` to run checks across all workspace members.
    3.  Configure `pytest` to discover tests in `packages/*/tests`.

### Phase 4: Core & Demo Refinement (Ordinary)
*   **Goal**: Clean up existing code and examples.
*   **Tasks**:
    1.  Update `example.py` and `fish_tank/` to work with the new structure.
    2.  Modernize type hints (e.g., `list[str]` instead of `List[str]`).
    3.  Ensure `py.typed` is correctly placed in both packages.

### Phase 5: CI/CD & Publishing (Smart)
*   **Goal**: Automate the release process.
*   **Tasks**:
    1.  Update GitHub Actions to use `uv` and test both packages.
    2.  Add a release workflow that builds and publishes both packages to PyPI when a tag is pushed.

---

## Recommendations
*   **Versioning**: Use `metametameta` to keep `src/**/__about__.py` in sync with `pyproject.toml`.
*   **Releases**: Always publish synchronized releases (e.g., same version number for both packages).
*   **Local Dev**: Use `uv run bug_trail` from the root to run the viewer; it will automatically use the local `bug_trail_core` thanks to the workspace.
*   **Documentation**: Switch from `pdoc3` to `mkdocs-material` for a more modern documentation site that can aggregate both libraries.

## Application Review: Bug Trail (Post-Migration)

Following the successful monorepo migration, a deep dive into the application code reveals several areas for improvement in reliability, ergonomics, and architectural scalability, particularly for its target audience of LLM-driven applications.

### Phase 6: Reliability & Correctness (Bug Fixes) - DONE ✅
*   **Fix `extra` Data Crash**: Implemented `user_data` JSON column to capture all non-standard LogRecord attributes.
*   **Fix `traceback_info` Schema**: Updated to use `INTEGER PRIMARY KEY AUTOINCREMENT` for `id` and fixed `INSERT` logic.
*   **Optimize DB Connections**: Refactored to reuse connections in `single_threaded` mode and use WAL mode for better concurrency.
*   **Thread Safety**: Added `threading.Lock` and `check_same_thread=False` support.

### Documentation Updates - DONE ✅
*   **API Docs**: Configured `pdoc3` to output to `docs_api/`.
*   **User Docs**: Integrated `zensical` for modern documentation site (outputs to `site/`).
*   **Makefile**: Added `make docs` target to automate both.

### Phase 7: LLM-First Features & Ergonomics
*   **Unstructured Metadata Support**: Add a `user_data` (JSON) column to the `logs` table to store all `extra` attributes from `LogRecord`, avoiding the need for a dynamic schema while preserving rich context.
*   **Global Exception Hooks**: Provide a one-line utility to register `sys.excepthook` and `threading.excepthook` to ensure no error goes unlogged, even "in the dark".
*   **LLM Context Capturing**: Add explicit support for capturing LLM-specific metadata (prompts, completions, model IDs, token usage) as a first-class citizen in the data model and UI.
*   **Improved Traceback Visualization**: The current viewer displays raw tracebacks. Integrate a more readable, colorized traceback view with local variable inspection (leveraging the already captured `f_locals`).

### Phase 8: Architectural Modernization
*   **From Static to Dynamic**: Replace the static HTML generation with a lightweight dynamic dashboard (e.g., FastAPI + Jinja2). This eliminates the $O(N)$ scaling issue where adding one error requires re-rendering thousands of files.
*   **Live Dashboard**: Implement a "Live View" using Server-Sent Events (SSE) or WebSockets to show errors in real-time as they occur during development.
*   **Search & Filter**: Leverage the SQLite backend for server-side searching and filtering of logs by level, module, or exception type.
*   **Contextual Grouping**: Group identical errors (same exception type and location) to reduce noise in the main view, similar to the original Elmah's behavior.

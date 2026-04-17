# Bug Trail Modernization Plan

## Goal

Replace the static-site generator with a live FastAPI web server that users launch with
`bug_trail start` and keep running while they develop. The page auto-refreshes when the SQLite
database changes. The core logging library (`bug_trail_core`) stays untouched.

---

## Current State

| Package | Role | Problem |
|---|---|---|
| `bug-trail-core` | SQLite logging handler | Fine as-is |
| `bug-trail` | Static HTML generator + watchdog | No real server; must re-run to see new data |

Neither package defines a `[project.scripts]` entry point, so there is no `bug_trail` CLI today.

---

## Target Install Model

```
pip install bug_trail          # core library only (handlers, config)
pip install bug_trail[web]     # adds the FastAPI web server
```

This means:

- `bug-trail-core` becomes the package people depend on in their projects (`pip install bug_trail_core`).
- `bug-trail` becomes the web-server package, installed as an optional extra of `bug_trail_core`
  **or** standalone. The `[web]` extra is declared in `bug_trail_core`'s `pyproject.toml` so
  that `pip install bug_trail[web]` installs both.

> **Naming note:** Because the PyPI name `bug_trail` already belongs to the current site-generator
> package, the simplest migration is:
> - Keep `bug-trail-core` → published as `bug-trail-core` (no change).
> - Repurpose `bug-trail` → published as `bug-trail`, but now it ships the FastAPI server.
> - Add `[web]` optional-dependencies in `bug-trail-core`'s pyproject pointing at `bug-trail`.

---

## Technology Choices

| Concern | Choice | Reason |
|---|---|---|
| Web framework | **FastAPI** | Lightweight, async, ships its own dev server (`uvicorn`), easy SSE support |
| Templating | **Jinja2** (keep existing templates) | Already a dependency; minimal rewrite |
| Auto-refresh | **Server-Sent Events (SSE)** from FastAPI | No WebSocket complexity; watchdog still watches the DB |
| Static assets | FastAPI `StaticFiles` mount | Replaces manual asset copying |
| Production server | `uvicorn` (bundled with FastAPI install) | Single `bug_trail start` command |

---

## New CLI: `bug_trail`

Defined in `bug-trail/pyproject.toml`:

```toml
[project.scripts]
bug_trail = "bug_trail.__main__:main"
```

### Commands

```
bug_trail start          # Start the web server (default port 7890)
bug_trail start --port 8080 --db /path/to/errors.db --host 0.0.0.0
bug_trail start --reload # Auto-reload server on code changes (dev mode)

bug_trail admin clear    # Wipe all rows from all log tables (keeps schema)
bug_trail admin reset    # Drop and recreate all tables
bug_trail admin export   # Dump DB to JSON/CSV (future)
```

---

## Page Structure

All pages are server-rendered Jinja2 templates. No SPA / JavaScript framework.

| Route | Template | Description |
|---|---|---|
| `GET /` | `view_main.jinja` | Log list with pagination |
| `GET /log/{record_id}` | `view_detail.jinja` | Single exception detail |
| `GET /environment` | `view_python_environment.jinja` | Venv / package info |
| `GET /system` | `view_system_info.jinja` | OS / hardware info |
| `GET /help` | `view_help.jinja` | **New** — setup instructions |
| `GET /admin` | `view_admin.jinja` | **New** — data management |
| `POST /admin/clear` | — | Clear all log data, redirect to /admin |
| `POST /admin/reset` | — | Full DB reset, redirect to /admin |
| `GET /events` | — | SSE stream; pushes `"refresh"` event when DB changes |

### Auto-refresh (SSE)

The base template includes a small `<script>` block (inline, no build step):

```html
<script>
  const es = new EventSource("/events");
  es.onmessage = () => location.reload();
</script>
```

The `/events` endpoint uses `watchdog` (already a dependency) to watch the `.db` file; when a
`FileModifiedEvent` fires it writes `data: refresh\n\n` to all open SSE connections.

---

## Help Page (`/help`)

The help page is the first thing a new user should see. It covers:

1. **What bug_trail does** — one paragraph.
2. **Register the handler** — copy-pasteable Python snippet:

```python
import logging
import bug_trail_core

config = bug_trail_core.read_config("pyproject.toml")
handler = bug_trail_core.BugTrailHandler(config.database_path)
handler.setLevel(logging.ERROR)

logger = logging.getLogger()       # root logger
logger.addHandler(handler)

# Or for a specific logger:
logger = logging.getLogger("myapp")
logger.addHandler(handler)
```

3. **pyproject.toml config** — the `[tool.bug_trail]` section with all keys explained.
4. **Start the server** — `bug_trail start`.
5. **Verify** — open `http://localhost:7890`, trigger an error, watch the list update.

---

## Admin Page (`/admin`)

Displays:

- DB file path and current size.
- Row counts per table (`exception_instance`, `traceback_info`, `system_info`, `python_libraries`).
- Two danger-zone buttons:
  - **Clear data** (`POST /admin/clear`) — truncates all tables, preserves schema.
  - **Reset database** (`POST /admin/reset`) — drops and recreates everything.
- Both actions require a `confirm=yes` hidden field (POST-only, no GET-triggered side effects).

---

## Migration Steps

### Phase 1 — Plumbing (no user-visible change)

1. Add `[project.scripts]` to `bug-trail/pyproject.toml`:
   ```toml
   [project.scripts]
   bug_trail = "bug_trail.__main__:main"
   ```
2. Add FastAPI + uvicorn to `bug-trail` dependencies:
   ```toml
   dependencies = [
     "bug-trail-core",
     "fastapi",
     "uvicorn[standard]",
     "jinja2",
     "pygments",
     "humanize",
     "watchdog",
   ]
   ```
3. Rewrite `__main__.py` to use `argparse` subcommands (`start`, `admin`).
4. Add `[web]` optional extra to `bug-trail-core/pyproject.toml`:
   ```toml
   [project.optional-dependencies]
   web = ["bug-trail>=3.2.0"]
   ```

### Phase 2 — FastAPI app

5. Create `bug_trail/app.py` — the FastAPI application:
   - Lifespan handler starts the watchdog observer on the configured DB path.
   - Mounts `StaticFiles` for `/static`.
   - Registers all routes listed in the Page Structure table above.
   - SSE endpoint streams DB-change events.
6. Port existing view logic from `views.py` / `view_*.py` into FastAPI route handlers.
   - Each handler queries the DB directly (same `data_code.py` functions) and renders a template.
   - No intermediate HTML file generation — responses stream directly to the browser.
7. Update Jinja2 templates:
   - Remove any assumption of file:// URLs (templates were written for static files).
   - Add `<script>` SSE block to `view_base.jinja`.
   - Add active-nav highlighting using FastAPI's `request.url.path`.

### Phase 3 — New pages

8. `view_help.jinja` — static help content (see Help Page section above).
9. `view_admin.jinja` — admin dashboard with row counts and action buttons.
10. Route handlers for `POST /admin/clear` and `POST /admin/reset`.

### Phase 4 — Polish

11. `bug_trail start` prints the URL and a one-liner on how to open `/help`.
12. If the DB doesn't exist yet, the index page shows a friendly "no data yet" state and
    links to `/help` instead of an empty table.
13. Fix the bugs catalogued in `SONNET_SAYS.md` that affect the live-server path
    (especially BUG1, BUG2, BUG6, BUG7).

---

## File Layout After Migration

```
packages/
  bug-trail-core/           # unchanged
    src/bug_trail_core/
      handlers.py
      config.py
      ...

  bug-trail/
    src/bug_trail/
      __main__.py           # rewritten: subcommands start / admin
      app.py                # NEW: FastAPI app factory
      routes/
        logs.py             # GET /, GET /log/{id}
        environment.py      # GET /environment, /system
        help.py             # GET /help
        admin.py            # GET /admin, POST /admin/clear, POST /admin/reset
        events.py           # GET /events (SSE)
      data_code.py          # unchanged
      view_shared.py        # unchanged
      pygments_job.py       # unchanged
      templates/
        view_base.jinja     # add SSE script block
        view_main.jinja
        view_detail.jinja
        view_python_environment.jinja
        view_system_info.jinja
        view_help.jinja     # NEW
        view_admin.jinja    # NEW
        view_navbar.jinja
      static/
        img/logo.png
        css/                # any future styles
```

The old `views.py`, `view_main.py`, `view_detail.py`, `incremental.py`, and `fs_utils.py` are
removed once the FastAPI routes cover the same functionality. Keep `data_code.py` and
`view_shared.py` — they contain DB queries and rendering helpers that are still useful.

---

## Out of Scope (for now)

- Authentication / login (this is a local dev tool).
- Pagination via HTMX or any JS framework — plain HTML `?page=N` query params are fine.
- Production deployment guide — this is a developer tool, not a production app.
- Email / webhook alerting.
- The `--ctags_file` / source-link feature can be preserved but is not a blocker.

# Bug Trail — Next Steps

## What was done

The static-site generator has been replaced with a live FastAPI server, per
`spec/MODERNIZATION.md`. Summary of the changes that landed on this branch:

### New architecture

- `bug_trail start` launches a uvicorn + FastAPI server (default port 7890).
- Page auto-refresh uses Server-Sent Events (`GET /events`) driven by watchdog.
- Templates moved to `packages/bug-trail/src/bug_trail/templates/`.
- Static assets moved to `packages/bug-trail/src/bug_trail/static/`
  (served from `/static`).
- Routes organised under `packages/bug-trail/src/bug_trail/routes/`:
  - `logs.py` — `GET /`, `GET /log/{log_key}`
  - `environment.py` — `GET /environment`, `GET /system`
  - `help.py` — `GET /help` (new, setup instructions)
  - `admin.py` — `GET /admin`, `POST /admin/clear`, `POST /admin/reset`
  - `events.py` — `GET /events` (SSE)
- `admin_ops.py` — shared logic for clearing/resetting data, used by the CLI
  admin commands and the admin-page forms.
- `db_watcher.py` — async-aware watchdog wrapper that fans out change events
  to all open SSE connections.

### CLI

`bug_trail` is now a real console script, registered in
`packages/bug-trail/pyproject.toml`.

Commands:

```
bug_trail start                              # default: 127.0.0.1:7890
bug_trail start --host 0.0.0.0 --port 8080
bug_trail start --db /tmp/errors.db
bug_trail start --reload                     # dev mode

bug_trail admin clear                        # truncate all log tables
bug_trail admin reset                        # drop + recreate schema
```

### Packaging

- `bug-trail-core` stays the library that applications depend on.
- `bug-trail` has a new `[project.scripts] bug_trail = bug_trail.__main__:main`.
- `bug-trail-core` now declares an optional extra so `pip install bug_trail_core[web]`
  pulls in the web server.
- Both package versions bumped to `3.2.0`.

### Bugs fixed during the port

Bugs in `spec/SONNET_SAYS.md` that were still open when work started:

- **`logs`-table column mismatch**: `emit()` prepended `record_id` to
  `field_names` but the SQL schema already declares `record_id` as the PK
  column, producing `INSERT INTO logs (record_id, record_id, …)` and the
  confusing "no such column user_data" error. Fixed in
  `bug_trail_core/handlers.py`.
- **Missing-column migration**: existing user databases from 3.1.x have no
  `user_data` column. Added a `_migrate_schema` pass that runs
  `ALTER TABLE ADD COLUMN` for any field_names missing from the live table.
- **`truncate_table` ran VACUUM inside an open transaction**: now commits the
  DELETE first and runs VACUUM outside the transaction.
- **Recursive logging handler loop**: `bug_trail_core.sqlite3_utils` logger
  now has `propagate = False` so error messages emitted from inside the
  handler never feed back into themselves through root-logger handlers.

Most of the other bugs catalogued in `SONNET_SAYS.md` (BUG1–BUG12) were
already resolved in commits on the current branch before this work started.
They have been left marked in that file as-is; no regressions were introduced.

### Removed

- `views.py`, `view_main.py`, `view_detail.py`,
  `view_python_environment.py`, `view_system_info.py`, `incremental.py`,
  `fs_utils.py`, `exceptions.py`, `pygments_job.py` — the static-site
  generator. All functionality replaced by FastAPI routes.
- Tests for the removed modules (`test_views.py`, `test_main.py`,
  `test_fs_utils.py`). A new `test_app.py` covers the FastAPI endpoints.
- `assets/` directory (merged into `static/`).

### Test coverage

`uv run pytest` → 18 passing:

- `tests/test_app.py` (9 tests) — index, help, empty state, detail, admin
  dashboard, admin clear, environment/system, health check.
- `tests/test_data_code.py` (4 tests) — SQLite serialization helpers.
- `tests/test_handlers.py` (5 tests in bug-trail-core).

---

## What's left

### Near-term polish

- [ ] **Source-code browsing**. The old static generator ran Pygments over
  the `source_folder` and linked log entries to highlighted HTML files.
  The FastAPI server does not. If we want this back, the options are:
  (a) on-demand `GET /source/{path}` route that highlights one file per
  request, or (b) a one-shot `bug_trail source rebuild` that generates a
  static tree served from `/static/src/`. (a) is simpler; (b) matches the
  old behaviour. Either way, the `pygments` dependency comes back.
- [ ] **Filtering and search on `/`**. Today the index table has no filter
  controls. A couple of query params (`?level=ERROR`, `?q=keyword`) would
  be cheap to add and materially more useful than pagination alone.
- [ ] **Detail-page keys**. `/log/{key}` uses a composite of
  `created|filename|lineno`. That's stable enough for a dev tool, but it's
  fragile against duplicate log lines and requires a full table scan on
  lookup. Switching to `record_id` (already the PK) would be faster and
  unique — worth a small follow-up.
- [ ] **Pagination controls**. The pager shows every page as a numbered
  link. For a log database with hundreds of pages this is ugly. Add
  first / prev / next / last plus a small window around the current page.
- [ ] **`/events` behind a reverse proxy**. Most dev users run this
  directly, but if anyone puts it behind nginx/Caddy without
  `proxy_buffering off`, SSE will break. Worth a note in the help page.

### Schema & data-model follow-ups

- [ ] **`exception_instance_id` FK type**. In `traceback_info` the column is
  declared `TEXT` and references `exception_instance.record_id` (TEXT PK).
  Good. But the old column name is still `exception_instance_id`, which
  reads as an integer. Rename to `record_id` for consistency, or add a
  comment that it's a UUID string.
- [ ] **Schema-drift tests**. The new `_migrate_schema` path uses
  `ALTER TABLE ADD COLUMN` but has no test that exercises it against a
  3.1.x-shaped database. A regression test that creates the old schema,
  opens a new handler, and writes a record would guard that path.
- [ ] **`single_threaded=False` path is untested**. The handler supports a
  per-emit reopen mode for multithreaded apps, but there are no tests
  around connection hygiene under that mode. Worth a dedicated test that
  hammers it from multiple threads.

### Distribution

- [ ] **Publish 3.2.0**. Both packages have been bumped locally; CHANGELOG
  entries and a PyPI release are still TODO.
- [ ] **Decide the `pip install bug_trail[web]` story**. The extra is
  declared on `bug-trail-core`, so `pip install bug_trail_core[web]`
  pulls in `bug-trail>=3.2.0`. If we want the more natural
  `pip install bug_trail[web]` syntax to work, we need a small
  meta-package or redirect — or just document "install bug_trail_core[web]
  — yes, `_core`".

### Known caveats

- **Windows-specific**: The CLI has been exercised on Windows 11 only so far.
  The file-watcher path uses `watchdog`, which supports all three major OSes,
  but the default-database path logic (`platformdirs`) produces different
  locations on Linux/macOS — worth a smoke test on both.
- **Hot-reload + SSE**: running with `--reload` disconnects SSE clients on
  every reload. Browser reconnects automatically but the "auto-refresh on
  DB change" gets fuzzy in that mode. This is fine for dev, just noted.
- **No authentication**. Deliberate — this is a localhost dev tool. Do not
  expose it on a public interface without sticking something in front.

### Optional (out of scope but cheap wins later)

- Dark mode. Bootstrap 5.3 supports `data-bs-theme="dark"` with one line;
  a toggle in the navbar would cost maybe 20 lines.
- JSON / CSV export (`bug_trail admin export`, noted in MODERNIZATION.md
  as future).
- A small badge on the navbar showing "connected" / "disconnected" based
  on SSE state, so the user can see at a glance whether auto-refresh is
  working.

---

## How to try it locally

```bash
# from the repo root
uv sync --all-extras
uv run python -m bug_trail start --port 7890 --db ./errors.db
# then in another terminal, emit some errors from your app
# and watch http://127.0.0.1:7890/ update live
```

Tests:

```bash
uv run pytest
```

"""FastAPI app factory for bug_trail."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass, field

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from bug_trail.db_watcher import DbWatcher

logger = logging.getLogger(__name__)


@dataclass
class AppState:
    """Process-wide runtime state for the web server."""

    db_path: str = ""
    source_folder: str = ""
    watcher: DbWatcher | None = field(default=None)


STATE = AppState()


def configure(db_path: str, source_folder: str = "") -> None:
    """Set runtime paths before uvicorn imports `app`."""
    STATE.db_path = db_path
    STATE.source_folder = source_folder


def _package_dir() -> str:
    return os.path.abspath(os.path.dirname(__file__))


def _templates() -> Jinja2Templates:
    templates = Jinja2Templates(directory=os.path.join(_package_dir(), "templates"))
    from bug_trail.view_shared import pretty_column_name

    templates.env.filters["pretty"] = pretty_column_name
    return templates


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_path = STATE.db_path
    if db_path:
        watch_dir = os.path.dirname(os.path.abspath(db_path)) or "."
        os.makedirs(watch_dir, exist_ok=True)
        STATE.watcher = DbWatcher(watch_dir, os.path.basename(db_path))
        STATE.watcher.start()
        logger.info("Watching %s for changes", watch_dir)
    yield
    if STATE.watcher is not None:
        STATE.watcher.stop()
        STATE.watcher = None


app = FastAPI(title="Bug Trail", lifespan=lifespan)

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(_package_dir(), "static")),
    name="static",
)

templates = _templates()


def _ctx(request: Request, **extra) -> dict:
    """Base template context (nav state + db info). Excludes the request."""
    path = request.url.path
    ctx = {
        "nav_active": _nav_active(path),
        "db_path": STATE.db_path,
        "db_exists": bool(STATE.db_path) and os.path.exists(STATE.db_path),
    }
    ctx.update(extra)
    return ctx


def render(request: Request, name: str, **extra):
    """Render a template with standard context."""
    return templates.TemplateResponse(request, name, _ctx(request, **extra))


def _nav_active(path: str) -> str:
    if path == "/" or path.startswith("/log/"):
        return "main"
    if path.startswith("/environment"):
        return "environment"
    if path.startswith("/system"):
        return "system"
    if path.startswith("/help"):
        return "help"
    if path.startswith("/admin"):
        return "admin"
    return ""


# Import routes to register endpoints. Imports are at the bottom so that
# `app` is defined and available to the route modules.
from bug_trail.routes import admin as _admin_routes  # noqa: E402,F401
from bug_trail.routes import environment as _environment_routes  # noqa: E402,F401
from bug_trail.routes import events as _events_routes  # noqa: E402,F401
from bug_trail.routes import help as _help_routes  # noqa: E402,F401
from bug_trail.routes import logs as _logs_routes  # noqa: E402,F401


@app.get("/health", response_class=HTMLResponse)
def health() -> str:
    return "ok"

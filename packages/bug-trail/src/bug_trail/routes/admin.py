"""Routes for /admin dashboard and data-management POST actions."""

from __future__ import annotations

import logging

from fastapi import Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from bug_trail.admin_ops import clear_all, db_size, reset_all, table_counts
from bug_trail.app import STATE, app, render

logger = logging.getLogger(__name__)


def _format_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


@app.get("/admin", response_class=HTMLResponse)
def admin_index(request: Request) -> HTMLResponse:
    db_path = STATE.db_path or ""
    counts = table_counts(db_path)
    size_bytes = db_size(db_path)
    return render(
        request,
        "view_admin.jinja",
        db_path=db_path,
        db_size=_format_size(size_bytes),
        db_size_bytes=size_bytes,
        counts=counts,
    )


@app.post("/admin/clear")
def admin_clear(confirm: str = Form("")) -> RedirectResponse:
    if confirm != "yes":
        return RedirectResponse(url="/admin", status_code=303)
    db_path = STATE.db_path or ""
    removed = clear_all(db_path)
    logger.info("admin clear removed %s rows from %s", removed, db_path)
    return RedirectResponse(url="/admin", status_code=303)


@app.post("/admin/reset")
def admin_reset(confirm: str = Form("")) -> RedirectResponse:
    if confirm != "yes":
        return RedirectResponse(url="/admin", status_code=303)
    db_path = STATE.db_path or ""
    reset_all(db_path)
    logger.info("admin reset completed for %s", db_path)
    return RedirectResponse(url="/admin", status_code=303)

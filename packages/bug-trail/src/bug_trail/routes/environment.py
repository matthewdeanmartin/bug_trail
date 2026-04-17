"""Routes for /environment and /system."""

from __future__ import annotations

import json
import logging
import os

from fastapi import Request
from fastapi.responses import HTMLResponse

from bug_trail.app import STATE, app, render
from bug_trail.data_code import fetch_table_as_list_of_dict

logger = logging.getLogger(__name__)


@app.get("/environment", response_class=HTMLResponse)
def environment(request: Request) -> HTMLResponse:
    db_path = STATE.db_path
    rows: list[dict] = []
    if db_path and os.path.exists(db_path):
        try:
            rows = fetch_table_as_list_of_dict(db_path, "python_libraries")
        except Exception as e:  # noqa: BLE001
            logger.warning("python_libraries read failed: %s", e)
    for row in rows:
        raw = row.get("urls")
        try:
            row["urls"] = json.loads(raw) if raw else {}
        except (ValueError, TypeError):
            row["urls"] = {}
    return render(request, "view_python_environment.jinja", logs=rows)


@app.get("/system", response_class=HTMLResponse)
def system(request: Request) -> HTMLResponse:
    db_path = STATE.db_path
    log: dict = {}
    if db_path and os.path.exists(db_path):
        try:
            rows = fetch_table_as_list_of_dict(db_path, "system_info")
            if rows:
                log = rows[0]
        except Exception as e:  # noqa: BLE001
            logger.warning("system_info read failed: %s", e)
    return render(request, "view_system_info.jinja", log=log)

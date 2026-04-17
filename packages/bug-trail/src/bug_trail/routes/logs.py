"""Routes for the main log list and individual log detail pages."""

from __future__ import annotations

import json
import logging
import os
from urllib.parse import quote

from fastapi import HTTPException, Request
from fastapi.responses import HTMLResponse

from bug_trail import data_code as data
from bug_trail.app import STATE, app, render
from bug_trail.view_shared import humanize_time, humanize_time_span, replace_msg_args

logger = logging.getLogger(__name__)

PAGE_SIZE = 100


def _log_key_raw(entry: dict) -> str:
    return f"{entry.get('created', '')}|{entry.get('filename', '')}|{entry.get('lineno', '')}"


def _log_key(entry: dict) -> str:
    """URL-safe detail key for the list view."""
    return quote(_log_key_raw(entry), safe="")


def _grouped_key_raw(entry: dict) -> str:
    return (
        f"{entry['TemporalDetails'].get('created', '')}|"
        f"{entry['SourceContext'].get('filename', '')}|"
        f"{entry['SourceContext'].get('lineno', '')}"
    )


@app.get("/", response_class=HTMLResponse)
def index(request: Request, page: int = 0) -> HTMLResponse:
    db_path = STATE.db_path
    if not db_path or not os.path.exists(db_path):
        return render(request, "view_empty.jinja")

    try:
        row_count = data.table_row_count(db_path, "logs")
    except Exception as e:  # noqa: BLE001
        logger.warning("Could not read logs table: %s", e)
        row_count = 0

    if row_count == 0:
        return render(request, "view_empty.jinja")

    offset = max(0, page) * PAGE_SIZE
    log_data = data.fetch_log_data(db_path, limit=PAGE_SIZE, offset=offset)

    for entry in log_data:
        entry["detail_key"] = _log_key(entry)
        lineno = entry.get("lineno")
        fname = entry.get("filename") or "(unknown)"
        entry["filename_display"] = f"{fname} ({lineno})" if lineno is not None else fname
        try:
            entry["created"] = humanize_time(entry.get("created") or 0, entry.get("msecs") or 0)
        except Exception:  # noqa: BLE001
            entry["created"] = str(entry.get("created", ""))
        try:
            replace_msg_args(entry)
        except Exception:  # noqa: BLE001
            pass

    total_pages = (row_count + PAGE_SIZE - 1) // PAGE_SIZE
    pages = list(range(total_pages))

    return render(
        request,
        "view_main.jinja",
        logs=log_data,
        pages=pages,
        current_page=page,
        row_count=row_count,
    )


@app.get("/log/{log_key}", response_class=HTMLResponse)
def log_detail(request: Request, log_key: str) -> HTMLResponse:
    db_path = STATE.db_path
    if not db_path or not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="No database available.")

    all_logs = data.fetch_log_data_grouped(db_path)

    # FastAPI has already URL-decoded log_key, so compare against the raw form.
    selected = None
    for entry in all_logs:
        if _grouped_key_raw(entry) == log_key:
            selected = entry
            break

    if selected is None:
        raise HTTPException(status_code=404, detail="Log entry not found.")

    _prepare_detail_view(selected)

    return render(request, "view_detail.jinja", log=selected)


def _prepare_detail_view(selected_log: dict) -> None:
    """In-place transformation — same logic as the old static generator."""
    ex_details = selected_log.get("ExceptionDetails", {})
    hierarchy_raw = ex_details.get("exception_hierarchy")
    if hierarchy_raw:
        try:
            exception_hierarchy = json.loads(hierarchy_raw)
            interesting = [
                {"type": t, "description": d}
                for t, d in exception_hierarchy
                if t not in ("type", "object")
            ]
            if interesting:
                ex_details["exception_hierarchy"] = interesting
            else:
                ex_details.pop("exception_hierarchy", None)
        except (ValueError, TypeError):
            pass

    temporal = selected_log.get("TemporalDetails", {})
    if "created" in temporal:
        try:
            temporal["created"] = humanize_time(
                temporal.get("created") or 0, temporal.get("msecs") or 0
            )
        except Exception:  # noqa: BLE001
            pass
    temporal.pop("msecs", None)
    if "relativeCreated" in temporal:
        try:
            formatted, apx = humanize_time_span(temporal["relativeCreated"])
            temporal["relativeCreated"] = f"{formatted} ({apx})"
        except Exception:  # noqa: BLE001
            pass

    message_details = selected_log.get("MessageDetails", {})
    if "levelname" in message_details and "levelno" in message_details:
        message_details["levelname"] = (
            f"{message_details['levelname']} ({message_details['levelno']})"
        )
        message_details.pop("levelno", None)
    try:
        replace_msg_args(message_details)
    except Exception:  # noqa: BLE001
        pass

    for section_name in list(selected_log.keys()):
        section = selected_log[section_name]
        if not isinstance(section, dict):
            continue
        to_delete = [k for k, v in section.items() if v is None or v == ""]
        for k in to_delete:
            del section[k]
    to_delete = [name for name, v in selected_log.items() if isinstance(v, dict) and not v]
    for name in to_delete:
        del selected_log[name]

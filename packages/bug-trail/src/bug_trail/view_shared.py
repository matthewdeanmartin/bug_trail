"""Template helpers used by the FastAPI route handlers."""

from __future__ import annotations

import ast
import datetime
import logging
from typing import Any

import humanize

logger = logging.getLogger(__name__)


def humanize_time(created: float, msecs: float = 0.0) -> str:
    """Convert epoch seconds to a human-readable date + relative time."""
    if not isinstance(created, float):
        created = float(created)
    if not isinstance(msecs, float):
        msecs = float(msecs)
    full_datetime = datetime.datetime.fromtimestamp(created + msecs / 1000.0)
    formatted_date = full_datetime.strftime("%B %d, %Y %H:%M:%S")
    relative_time = humanize.naturaltime(datetime.datetime.now() - full_datetime)
    return f"{formatted_date}, {relative_time}"


def humanize_time_span(milliseconds: float) -> tuple[str, str]:
    """Convert a time span in ms to (precise_format, general_description)."""
    if not isinstance(milliseconds, float):
        milliseconds = float(milliseconds)
    thresholds = {
        "millisecond": 1,
        "second": 60,
        "minute": 60 * 60,
        "hour": 60 * 60 * 24,
        "day": 60 * 60 * 24 * 30,
        "month": 60 * 60 * 24 * 30 * 12,
    }
    seconds = milliseconds / 1000.0

    unit = "N/A"
    for unit, limit in thresholds.items():  # noqa: B007
        if seconds < limit:
            break

    if unit == "millisecond":
        precise_format = f"{seconds * 1000:.0f} milliseconds"
    elif unit == "second":
        precise_format = f"{seconds:.0f} seconds"
    elif unit == "minute":
        precise_format = f"{seconds / 60:.0f} minutes"
    elif unit == "hour":
        precise_format = f"{seconds / 3600:.0f} hours"
    elif unit == "day":
        precise_format = f"{seconds / (3600 * 24):.0f} days"
    else:
        precise_format = f"{seconds / (3600 * 24 * 30):.0f} months"

    general_description = humanize.naturaldelta(seconds)
    return precise_format, general_description


def pretty_column_name(column_name: str) -> str:
    """Transform a column name for display.

    >>> pretty_column_name("lineno")
    'Line Number'
    """
    special_cases = {
        "lineno": "Line Number",
        "funcName": "Function Name",
        "exc_info": "Exception Info",
        "msg": "Message",
        "args": "Arguments",
        "levelname": "Level Name",
        "levelno": "Level Number",
        "pathname": "Path Name",
        "filename": "File Name",
        "msecs": "Milliseconds",
        "relativeCreated": "Relative Created",
        "processName": "Process Name",
        "threadName": "Thread Name",
        "exc_text": "Exception Text",
        "stack_info": "Stack Info",
    }
    if column_name in special_cases:
        return special_cases[column_name]
    return column_name.replace("_", " ").title()


def replace_msg_args(message_details: dict[str, Any]) -> None:
    """Apply %-format args into msg, then drop the args key in-place."""
    args = message_details.get("args")
    if args and args != "()":
        try:
            args_dict = ast.literal_eval(args)
            try:
                message_details["msg"] = message_details["msg"] % args_dict
            except TypeError:
                message_details["msg"] = f'{message_details["msg"]} % {args_dict}'
        except (ValueError, SyntaxError):
            pass
    message_details.pop("args", None)

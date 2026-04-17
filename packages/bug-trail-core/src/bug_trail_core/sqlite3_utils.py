"""
Another module to avoid Circular Import
"""

from __future__ import annotations

import datetime
import logging
import sqlite3
from typing import Any, Union

logger = logging.getLogger(__name__)
# Prevent the bug_trail handler from re-entering itself via its own error
# messages. Propagation is off unless an app explicitly re-enables it.
logger.propagate = False

ALL_TABLES = [
    "exception_instance",
    "exception_type",
    "logs",
    "python_libraries",
    "system_info",
    "traceback_info",
]


SqliteTypes = Union[None, int, float, str, bytes, datetime.date, datetime.datetime]


def serialize_to_sqlite_supported(value: Any | None) -> SqliteTypes:
    """
    Sqlite supports None, int, float, str, bytes by default, and also knows how to adapt datetime.date and datetime.datetime
    everything else is str(value)
    >>> serialize_to_sqlite_supported(1)
    1
    >>> serialize_to_sqlite_supported(1.0)
    1.0
    """
    # if isinstance(value, NoneType):
    #     return None
    if value is None:
        return None
    if isinstance(value, (int, float, str, bytes)):
        return value
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value
    return str(value)


def is_table_empty(conn: sqlite3.Connection, table_name: str) -> bool:
    """
    Check if the specified table is empty.

    Parameters:
    conn (sqlite3.Connection): The database connection.
    table_name (str): The name of the table to check.

    Returns:
    bool: True if the table is empty, False otherwise.
    """
    if table_name not in ALL_TABLES:
        raise TypeError("Bad table name.")
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT EXISTS(SELECT 1 FROM {table_name} LIMIT 1);"
        )  # nosec: table checked above
        return cursor.fetchone()[0] == 0
    except sqlite3.Error:
        return True  # Assuming empty if an error occurs


def truncate_table(conn: sqlite3.Connection, table_name: str) -> None:
    """
    Truncate the specified table.

    Parameters:
    conn (sqlite3.Connection): The database connection.
    table_name (str): The name of the table to truncate.
    """
    if table_name not in ALL_TABLES:
        raise TypeError("Bad table name.")
    try:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name};")  # nosec: table checked above
        conn.commit()
        # VACUUM must run outside a transaction.
        try:
            cursor.execute("VACUUM;")
        except sqlite3.OperationalError:
            pass
    except sqlite3.Error as e:
        try:
            conn.rollback()
        except sqlite3.Error:
            pass
        logger.warning("truncate_table(%s) failed: %s", table_name, e)

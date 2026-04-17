"""Admin operations on the bug_trail SQLite database."""

from __future__ import annotations

import os
import sqlite3

from bug_trail_core.handlers import BaseErrorLogHandler
from bug_trail_core.sqlite3_utils import ALL_TABLES, truncate_table


def clear_all(db_path: str) -> int:
    """Truncate every known table. Returns approximate rows removed."""
    if not os.path.exists(db_path):
        return 0
    conn = sqlite3.connect(db_path)
    try:
        total = 0
        for table in ALL_TABLES:
            try:
                cur = conn.cursor()
                cur.execute(f"SELECT count(*) FROM {table}")  # nosec
                total += cur.fetchone()[0]
            except sqlite3.OperationalError:
                continue
        for table in ALL_TABLES:
            try:
                truncate_table(conn, table)
            except sqlite3.OperationalError:
                continue
        return total
    finally:
        conn.close()


def reset_all(db_path: str) -> None:
    """Drop every known table and recreate the schema."""
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        try:
            for table in ALL_TABLES:
                try:
                    conn.execute(f"DROP TABLE IF EXISTS {table}")  # nosec
                except sqlite3.OperationalError:
                    continue
            conn.commit()
        finally:
            conn.close()
    # Recreate schema by constructing a handler (idempotent).
    BaseErrorLogHandler(db_path)


def table_counts(db_path: str) -> dict[str, int]:
    """Return row counts for each known table. Missing tables report 0."""
    result: dict[str, int] = {t: 0 for t in ALL_TABLES}
    if not os.path.exists(db_path):
        return result
    conn = sqlite3.connect(db_path)
    try:
        for table in ALL_TABLES:
            try:
                cur = conn.cursor()
                cur.execute(f"SELECT count(*) FROM {table}")  # nosec
                result[table] = cur.fetchone()[0]
            except sqlite3.OperationalError:
                result[table] = 0
    finally:
        conn.close()
    return result


def db_size(db_path: str) -> int:
    """Return the size of the SQLite file in bytes. 0 if missing."""
    try:
        return os.path.getsize(db_path)
    except OSError:
        return 0

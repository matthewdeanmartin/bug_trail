"""
This module contains custom logging handlers.
"""

from __future__ import annotations

import json
import logging
import re
import sqlite3
import sys
import threading
import traceback
import uuid
from importlib.resources import as_file, files
from typing import Any

from bug_trail_core.exceptions import (
    create_exception_instance_table,
    create_exception_type_table,
    create_traceback_info_table,
    insert_exception_instance,
    insert_exception_type,
    insert_traceback_info,
)
from bug_trail_core.sqlite3_utils import is_table_empty, serialize_to_sqlite_supported
from bug_trail_core.system_info import create_system_info_table, record_system_info
from bug_trail_core.venv_info import create_python_libraries_table, record_venv_info


class BaseErrorLogHandler:
    """
    A custom logging handler that logs to a SQLite database.
    """

    def __init__(
        self, db_path: str, pico: bool = False, minimum_level: int = logging.ERROR, single_threaded: bool = True
    ) -> None:
        """
        Initialize the handler
        Args:
            db_path (str): Path to the SQLite database
        """
        self.single_threaded = single_threaded
        self.db_path = db_path
        self.pico = pico
        self.minimum_level = minimum_level
        self.create_table_sql: str = ""
        self.formatted_sql = ""
        self.field_names: list[str] = []
        self._lock = threading.Lock()
        self.conn: sqlite3.Connection | None = None
        
        # Ensure tables exist
        self.reopen()
        assert self.conn is not None
        self.create_table()
        create_exception_type_table(self.conn)
        create_exception_instance_table(self.conn)
        create_traceback_info_table(self.conn)
        create_system_info_table(self.conn)
        if is_table_empty(self.conn, "system_info"):
            record_system_info(self.conn)

        create_python_libraries_table(self.conn)
        if is_table_empty(self.conn, "python_libraries"):
            record_venv_info(self.conn)

        if not self.single_threaded:
            self.conn.close()
            self.conn = None

    def reopen(self) -> None:
        """Reopen the connection"""
        if self.conn is not None:
            try:
                self.conn.close()
            except sqlite3.ProgrammingError:
                pass
        self.conn = sqlite3.connect(self.db_path, check_same_thread=self.single_threaded)
        self.conn.execute("PRAGMA journal_mode = WAL;")  # WAL is generally better for concurrency
        self.conn.execute("PRAGMA synchronous = NORMAL;")

    def create_table(self) -> None:
        """
        Create the logs table if it doesn't exist
        """
        # Locate the resource file
        source = files("bug_trail_core").joinpath("create_table.sql")

        with as_file(source) as file:
            self.create_table_sql = file.read_text(encoding="utf-8")

        if not self.create_table_sql:
            # Fallback schema if file not found
            self.create_table_sql = """CREATE TABLE IF NOT EXISTS logs (
                record_id TEXT PRIMARY KEY,
                args TEXT,
                asctime TEXT,
                created REAL,
                exc_info TEXT,
                exc_text TEXT,
                filename TEXT,
                funcName TEXT,
                levelname TEXT,
                levelno INTEGER,
                lineno INTEGER,
                message TEXT,
                module TEXT,
                msecs REAL,
                msg TEXT,
                name TEXT,
                pathname TEXT,
                process INTEGER,
                processName TEXT,
                relativeCreated REAL,
                stack_info TEXT,
                thread INTEGER,
                threadName TEXT,
                traceback TEXT,
                taskName TEXT,
                user_data TEXT
            )"""
            
        # Extract known field names from the SQL to avoid 'extra' crash
        self.field_names = []
        # Find all content within parentheses of CREATE TABLE
        match = re.search(r"CREATE TABLE IF NOT EXISTS logs\s*\((.*)\)", self.create_table_sql, re.DOTALL | re.IGNORECASE)
        if match:
            column_defs = match.group(1).split(",")
            for col_def in column_defs:
                col_def = col_def.strip()
                if not col_def:
                    continue
                # Extract first word as column name
                parts = col_def.split()
                if parts:
                    col_name = parts[0].strip()
                    if col_name.upper() not in ("PRIMARY", "FOREIGN", "CONSTRAINT", "CHECK", "UNIQUE"):
                        self.field_names.append(col_name)

        self.safe_execute(self.create_table_sql, [])

    def emit(self, record: logging.LogRecord) -> None:
        """
        Insert a log record into the database

        Args:
            record (logging.LogRecord): The log record to be inserted
        """
        if record.levelno < self.minimum_level:
            return

        # clientside primary key
        record_id = str(uuid.uuid4())
        if not record.exc_info:
            record.exc_info = sys.exc_info()
            if not record.exc_info[0]:
                record.exc_info = None

        # Check if there is exception information
        if record.exc_info:
            exception_type, exception, traceback_object = record.exc_info
            # Format the traceback
            traceback_str = "".join(traceback.format_exception(*record.exc_info))
            record.traceback = traceback_str

            if exception:
                with self._lock:
                    if not self.single_threaded:
                        self.reopen()
                    assert self.conn is not None
                    try:
                        # not unique per log entry
                        insert_exception_type(self.conn, exception)
                        # unique per log entry
                        insert_exception_instance(self.conn, record_id, exception)
                        exception_instance_id = record_id
                        # Insert traceback info
                        if exception and exception.__traceback__:
                            insert_traceback_info(self.conn, exception_instance_id, exception.__traceback__)
                        self.conn.commit()
                    finally:
                        if not self.single_threaded:
                            self.conn.close()
                            self.conn = None
        else:
            record.traceback = None

        # Prepare arguments, capturing 'extra' fields into user_data
        known_attrs = set(self.field_names)
        user_data = {}
        # Attributes to ignore (internal to LogRecord or already handled)
        internal_attrs = {'getMessage', 'exc_info', 'exc_text', 'stack_info', 'record_id'}
        
        for attr in dir(record):
            if attr.startswith('__') or attr in internal_attrs:
                continue
            if attr not in known_attrs:
                val = getattr(record, attr)
                if not callable(val):
                    user_data[attr] = val
        
        record.user_data = json.dumps(user_data, default=str) if user_data else None

        if not self.formatted_sql:
            fields = ["record_id"] + self.field_names
            placeholders = ", ".join(["?" for _ in fields])
            self.formatted_sql = f"INSERT INTO logs ({', '.join(fields)}) VALUES ({placeholders})"

        args = [record_id] + [getattr(record, field, None) for field in self.field_names]
        args = [serialize_to_sqlite_supported(arg) for arg in args]

        self.safe_execute(self.formatted_sql, args)

    def safe_execute(self, sql: str, args: list[Any], recurse_count: int = 0) -> None:
        with self._lock:
            if not self.single_threaded or self.conn is None:
                self.reopen()
            assert self.conn is not None
            try:
                self.conn.execute(sql, args)
                self.conn.commit()
            except sqlite3.OperationalError as oe:
                if "no such table" in oe.args[0] and recurse_count == 0:
                    self.create_table()
                    self.safe_execute(sql, args, recurse_count + 1)
                else:
                    raise
            finally:
                if not self.single_threaded:
                    self.conn.close()
                    self.conn = None

    def close(self) -> None:
        """
        Close the connection to the database
        """
        # If we are not single threaded, even talking to the conn object
        # will throw an error.
        if self.conn and self.single_threaded:
            try:
                self.conn.close()
            except sqlite3.ProgrammingError as programming_error:
                if "Cannot operate on a closed database" in str(programming_error):
                    pass
                raise


class BugTrailHandler(logging.Handler):
    """
    A custom logging handler that logs to a SQLite database.
    """

    def __init__(self, db_path: str, minimum_level: int = logging.ERROR, single_threaded: bool = True) -> None:
        """
        Initialize the handler
        Args:
            db_path (str): Path to the SQLite database
            single_threaded (bool): If True, the handler will close the connection after each emit.
        """
        self.base_handler = BaseErrorLogHandler(db_path, minimum_level=minimum_level, single_threaded=single_threaded)
        super().__init__()

    def emit(self, record: logging.LogRecord) -> None:
        """
        Insert a log record into the database

        Args:
            record (logging.LogRecord): The log record to be inserted
        """
        self.base_handler.emit(record)

    def close(self) -> None:
        """
        Close the connection to the database
        """
        self.base_handler.close()
        super().close()

"""
This module contains custom logging handlers.
"""
import logging
import sqlite3
import traceback
from typing import Optional

from bug_trail.sqlite3_utils import serialize_to_sqlite_supported

try:
    import picologging

    pico_available = True
except NameError:
    pico_available = False


class BaseErrorLogHandler:
    """
    A custom logging handler that logs to a SQLite database.
    """

    def __init__(self, db_path: str, pico: bool = False, minimum_level: int = logging.ERROR) -> None:
        """
        Initialize the handler
        Args:
            db_path (str): Path to the SQLite database
        """
        self.db_path = db_path
        self.pico = pico
        self.minimum_level = minimum_level
        self.reopen()
        self.create_table()

    def reopen(self):
        """Reopen the connection"""
        self.conn = sqlite3.connect(self.db_path)

    def create_table(self) -> None:
        """
        Create the logs table if it doesn't exist
        """
        # Create a dummy LogRecord to introspect its attributes
        dummy_record = None

        # Define a mapping of Python types to SQLite types
        type_mapping = {
            int: "INTEGER",
            float: "REAL",
            str: "TEXT",
            bytes: "BLOB",  # Assuming bytes should be stored as BLOB
            type(None): "TEXT",  # Why would we have a column of just None?
        }

        # Build the columns schema based on LogRecord attributes
        columns = []

        # mypyc won't deal with a union of the 2 kinds of LogRecords, so
        # we live with some duplication here.
        if self.pico:
            dummy_pico_record = picologging.LogRecord(
                name="", level=logging.ERROR, pathname="", lineno=0, msg="", args=(), exc_info=None
            )
            for attr in dir(dummy_pico_record):
                if not callable(getattr(dummy_pico_record, attr)) and not attr.startswith("__"):
                    attr_type = type(getattr(dummy_pico_record, attr, ""))
                    sqlite_type = type_mapping.get(attr_type, "TEXT")  # Default to TEXT if type not in mapping
                    columns.append(f"{attr} {sqlite_type}")
        else:
            dummy_record = logging.LogRecord(
                name="", level=logging.ERROR, pathname="", lineno=0, msg="", args=(), exc_info=None
            )
            for attr in dir(dummy_record):
                if not callable(getattr(dummy_record, attr)) and not attr.startswith("__"):
                    attr_type = type(getattr(dummy_record, attr, ""))
                    sqlite_type = type_mapping.get(attr_type, "TEXT")  # Default to TEXT if type not in mapping
                    columns.append(f"{attr} {sqlite_type}")

        # Add traceback column
        columns.append("traceback TEXT")

        # message is when `msg % args` gets evaluated by some part of the `logging` module?
        if "message TEXT" not in columns:
            columns.append("message TEXT")

        columns_text = ", ".join(columns)
        create_table_sql = f"CREATE TABLE IF NOT EXISTS logs ({columns_text})"
        self.conn.execute(create_table_sql)
        self.conn.commit()

    def emit(self, record: logging.LogRecord) -> None:
        """
        Insert a log record into the database

        Args:
            record (logging.LogRecord): The log record to be inserted
        """
        if record.levelno < self.minimum_level:
            return
        # Check if there is exception information
        if record.exc_info:
            # Format the traceback
            traceback_str = "".join(traceback.format_exception(*record.exc_info))
            record.traceback = traceback_str
            # TODO: do something with the traceback
            # exception_type, exception, traceback_object = record.exc_info
            # print(exception_type, exception, traceback_object)
        else:
            record.traceback = None

        insert_sql = "INSERT INTO logs ({fields}) VALUES ({values})"
        field_names = ", ".join(
            [attr for attr in dir(record) if not attr.startswith("__") and not attr == "getMessage"]
        )
        field_names = field_names + ", traceback"
        field_values = ", ".join(["?" for _ in field_names.split(", ")])
        formatted_sql = insert_sql.format(fields=field_names, values=field_values)
        args = [getattr(record, field, "") for field in field_names.split(", ")]
        args = [serialize_to_sqlite_supported(arg) for arg in args]

        self.conn.execute(formatted_sql, args)

        self.conn.commit()

    def pico_emit(self, record: picologging.LogRecord) -> None:
        """
        Insert a log record into the database

        Args:
            record (logging.LogRecord): The log record to be inserted
        """
        if record.levelno < self.minimum_level:
            return
        # Check if there is exception information
        traceback_str: Optional[str] = None
        if record.exc_info:
            # Format the traceback
            traceback_str = "".join(traceback.format_exception(*record.exc_info))
            # pico doesn't have this field.

        insert_sql = "INSERT INTO logs ({fields}) VALUES ({values})"
        field_names = ", ".join(
            [attr for attr in dir(record) if not attr.startswith("__") and not attr == "getMessage"]
        )
        field_names = field_names + ", traceback"
        field_values = ", ".join(["?" for _ in field_names.split(", ")])
        formatted_sql = insert_sql.format(fields=field_names, values=field_values)
        args = [getattr(record, field, "") for field in field_names.split(", ") if field != "traceback"]
        args += [traceback_str]
        args = [serialize_to_sqlite_supported(arg) for arg in args]

        self.conn.execute(formatted_sql, args)
        self.conn.commit()

    def close(self) -> None:
        """
        Close the connection to the database
        """
        if self.conn:
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

    def __init__(self, db_path: str, minimum_level: int = logging.ERROR) -> None:
        """
        Initialize the handler
        Args:
            db_path (str): Path to the SQLite database
        """
        self.base_handler = BaseErrorLogHandler(db_path, minimum_level=minimum_level)
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


# mypyc didn't like this
# if pico_available:


class PicoBugTrailHandler(picologging.Handler):
    """
    A custom logging handler that logs to a SQLite database.
    """

    def __init__(self, db_path: str, minimum_level: int = logging.ERROR) -> None:
        """
        Initialize the handler
        Args:
            db_path (str): Path to the SQLite database
        """
        super().__init__()
        self.base_handler = BaseErrorLogHandler(db_path, pico=True, minimum_level=minimum_level)

    def emit(self, record: picologging.LogRecord) -> None:
        """
        Insert a log record into the database

        Args:
            record (logging.LogRecord): The log record to be inserted
        """
        self.base_handler.pico_emit(record)

    def close(self) -> None:
        """
        Close the connection to the database
        """
        self.base_handler.close()
        super().close()

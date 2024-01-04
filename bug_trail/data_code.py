"""
Functions to fetch data from the SQLite database.
"""
import sqlite3
from typing import Any

from bug_trail_core.handlers import BaseErrorLogHandler


def fetch_log_data(db_path: str) -> list[dict[str, Any]]:
    """
    Fetch all log records from the database.

    Args:
        db_path (str): Path to the SQLite database

    Returns:
        list[dict[str, Any]]: A list of dictionaries containing all log records
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to fetch all rows from the logs table
    query = "SELECT * FROM logs ORDER BY created DESC"
    execute_safely(cursor, query, db_path)

    # Fetching column names from the cursor
    columns = [description[0] for description in cursor.description]

    # Fetch all rows, and convert each row to a dictionary
    rows = cursor.fetchall()
    log_data = []
    for row in rows:
        log_record = dict(zip(columns, row, strict=True))
        log_data.append(log_record)

    # Close the connection
    conn.close()
    return log_data


def fetch_log_data_grouped(db_path: str) -> Any:
    """
    Fetch all log records from the database, and group them into a nested dictionary.

    Args:
        db_path (str): Path to the SQLite database

    Returns:
        Any: A nested dictionary containing all log records
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to fetch all rows from the logs table
    query = "SELECT * FROM logs ORDER BY created DESC"
    execute_safely(cursor, query, db_path)

    # Fetching column names from the cursor
    columns = [description[0] for description in cursor.description]

    # Fetch all rows, and convert each row to a grouped dictionary
    rows = cursor.fetchall()
    log_data = []
    for row in rows:
        log_record = dict(zip(columns, row, strict=True))

        # Grouping the log record
        grouped_record = {
            "MessageDetails": {key: log_record[key] for key in ["msg", "args", "levelname", "levelno"]},
            "SourceContext": {
                key: log_record[key] for key in ["name", "pathname", "filename", "module", "funcName", "lineno"]
            },
            "TemporalDetails": {key: log_record[key] for key in ["created", "msecs", "relativeCreated"]},
            "ProcessThreadContext": {
                key: log_record[key] for key in ["process", "processName", "thread", "threadName"]
            },
            "ExceptionDetails": {key: log_record[key] for key in ["exc_info", "exc_text"]},
            "StackDetails": {key: log_record[key] for key in ["stack_info"]},
            "UserData": {
                key: log_record[key]
                for key in log_record.keys()
                - {
                    "msg",
                    "args",
                    "levelname",
                    "levelno",
                    "name",
                    "pathname",
                    "filename",
                    "module",
                    "funcName",
                    "lineno",
                    "created",
                    "msecs",
                    "relativeCreated",
                    "process",
                    "processName",
                    "thread",
                    "threadName",
                    "exc_info",
                    "exc_text",
                    "stack_info",
                }
            },
        }
        log_data.append(grouped_record)

    # Close the connection
    conn.close()
    return log_data


def execute_safely(cursor: sqlite3.Cursor, query: str, db_path: str) -> None:
    """
    Execute a query safely, creating the table if it doesn't exist

    Args:
        cursor (sqlite3.Cursor): The cursor to use
        query (str): The query to execute
        db_path (str): The path to the database
    """
    try:
        cursor.execute(query)
    except sqlite3.OperationalError as se:
        if "no such table" in str(se):
            # TODO: handle the possibility that the table is different for picologging
            handler = BaseErrorLogHandler(db_path)
            handler.create_table()
            cursor.execute(query)
        else:
            raise

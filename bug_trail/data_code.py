"""
Functions to fetch data from the SQLite database.
"""
import logging
import sqlite3
from typing import Any

from bug_trail_core.handlers import BaseErrorLogHandler

logger = logging.getLogger(__name__)

ALL_TABLES = [
    "exception_instance",
    "exception_type",
    "logs",
    "python_libraries",
    "system_info",
    "traceback_info",
]

ENTIRE_LOG_SET = (
    "SELECT logs.*, "
    "exception_instance.args, "
    "exception_instance.args as exception_args, "
    "exception_instance.args as exception_str, "
    "exception_instance.args as comments, "
    "exception_type.name as exception_name, "
    "exception_type.docstring as exception_docstring, "
    "exception_type.hierarchy as exception_hierarchy "
    "FROM logs "
    "left outer join exception_instance "
    "on logs.record_id = exception_instance.record_id "
    "left outer join exception_type "
    "on exception_instance.type_id = exception_type.id "
    "ORDER BY created DESC"
)


def table_row_count(conn: sqlite3.Connection, table_name: str) -> int:
    if table_name not in ALL_TABLES:
        raise TypeError("Bad table name.")
    cursor = conn.cursor()
    cursor.execute(f"SELECT count(*) FROM {table_name};")  # nosec: table name restricted above
    try:
        return cursor.fetchone()[0]
    except IndexError:
        return 0


def connect(db_path: str) -> sqlite3.Connection:
    """Open db, central code"""
    # Mock this to prevent extra dbs being created.
    return sqlite3.connect(db_path)


def fetch_log_data(conn: sqlite3.Connection, db_path: str, limit: int = -1, offset: int = -1) -> list[dict[str, Any]]:
    """
    Fetch all log records from the database.

    Args:
        conn (sqlite3.Connection): The connection to the database
        db_path (str): Path to the SQLite database
        limit (int, optional): Limit the number of records returned. Defaults to -1.
        offset (int, optional): Offset the records returned. Defaults to -1.

    Returns:
        list[dict[str, Any]]: A list of dictionaries containing all log records
    """
    # Connect to the SQLite database

    logger.debug(f"Connected to {db_path}")
    cursor = conn.cursor()

    # Query to fetch all rows from the logs table
    query = ENTIRE_LOG_SET
    if limit != -1:
        query += f" LIMIT {limit} OFFSET {offset}"
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


def fetch_table_as_list_of_dict(db_path: str, table: str) -> list[dict[str, Any]]:
    """
    Fetch all log records from the database.

    Args:
        db_path (str): Path to the SQLite database
        table (str): Table to query

    Returns:
        list[dict[str, Any]]: A list of dictionaries containing all log records
    """
    if table not in ALL_TABLES:
        raise TypeError("Don't know that table.")

    # Connect to the SQLite database
    conn = connect(db_path)
    logger.debug(f"Connected to {db_path}")
    cursor = conn.cursor()

    # Query to fetch all rows from the logs table
    query = f"SELECT * FROM {table}"  # nosec: table name restricted above
    execute_safely(cursor, query, db_path)

    # Fetching column names from the cursor
    columns = [description[0] for description in cursor.description]

    # Fetch all rows, and convert each row to a dictionary
    rows = cursor.fetchall()
    data = []
    for row in rows:
        record = dict(zip(columns, row, strict=True))
        data.append(record)

    # Close the connection
    conn.close()
    return data


def fetch_log_data_grouped(db_path: str) -> Any:
    """
    Fetch all log records from the database, and group them into a nested dictionary.

    Args:
        db_path (str): Path to the SQLite database

    Returns:
        Any: A nested dictionary containing all log records
    """
    # Connect to the SQLite database
    conn = connect(db_path)
    logger.debug(f"Connected to {db_path}")
    cursor = conn.cursor()

    # Query to fetch all rows from the logs table
    query = ENTIRE_LOG_SET
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
            "ExceptionDetails": {
                key: log_record.get(key)
                for key in [
                    "exc_info",
                    "exc_text",
                    "exception_args",
                    "exception_str",
                    "comments",
                    "exception_name",
                    "exception_docstring",
                    "exception_hierarchy",
                ]
            },
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
                    # exception table
                    "exception_args",
                    "exception_str",
                    "comments",
                    "exception_name",
                    "exception_docstring",
                    "exception_hierarchy",
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
        logger.debug(query)
        cursor.execute(query)
    except sqlite3.OperationalError as se:
        if "no such table" in str(se):
            # TODO: handle the possibility that the table is different for picologging
            handler = BaseErrorLogHandler(db_path)
            handler.create_table()
            cursor.execute(query)
        else:
            raise

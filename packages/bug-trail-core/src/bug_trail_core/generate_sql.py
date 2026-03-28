"""
Code to generate sql for table.
"""

from __future__ import annotations

import logging


def create_table_schemas(pico: bool) -> str:
    """
    Schema
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
    return create_table_sql


if __name__ == "__main__":
    print(create_table_schemas(True))
    print(create_table_schemas(False))

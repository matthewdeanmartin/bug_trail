"""
Record type, instance and call stack info about an exception.
"""

from __future__ import annotations

import json
import sqlite3


def get_exception_hierarchy(ex: BaseException) -> list[tuple[str, str | None]]:
    """
    Get the inheritance hierarchy of an exception.

    Parameters:
    ex (Exception): The exception instance.

    Returns:
    list of tuples: A list where each tuple contains the name and docstring of a class in the hierarchy.
    """
    hierarchy = []
    ex_class = ex.__class__

    # Traverse the inheritance hierarchy
    while ex_class:
        hierarchy.append((ex_class.__name__, ex_class.__doc__))
        if ex_class.__bases__:
            # Move up to the next base class
            ex_class = ex_class.__bases__[0]
        else:
            break

    return hierarchy


def create_connection(db_file: str) -> sqlite3.Connection:
    """Create a database connection to a SQLite database"""
    conn = sqlite3.connect(db_file)
    return conn


def create_exception_type_table(conn: sqlite3.Connection) -> None:
    """Create the exception_type table with an additional column for the hierarchy"""
    sql_create_exception_type_table = """CREATE TABLE IF NOT EXISTS exception_type (
                                            id INTEGER PRIMARY KEY,
                                            name TEXT NOT NULL,
                                            module TEXT NOT NULL,
                                            docstring TEXT,
                                            hierarchy TEXT
                                        );"""
    cursor = conn.cursor()
    cursor.execute(sql_create_exception_type_table)


def insert_exception_type(conn: sqlite3.Connection, ex: BaseException) -> int:
    """Insert a new row into the exception_type table including the hierarchy"""
    ex_class = ex.__class__
    ex_name = ex_class.__name__
    ex_module = ex_class.__module__
    ex_docstring = ex_class.__doc__
    ex_hierarchy = json.dumps(get_exception_hierarchy(ex))

    # Check if this type of exception already exists
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM exception_type WHERE name = ? AND module = ?", (ex_name, ex_module))
    data = cursor.fetchone()

    # Insert new exception type along with its hierarchy
    if data is not None:
        return data[0]
    sql_insert_exception_type = """INSERT INTO exception_type (name, module, docstring, hierarchy) 
                                   VALUES (?, ?, ?, ?)"""
    cursor.execute(sql_insert_exception_type, (ex_name, ex_module, ex_docstring, ex_hierarchy))
    conn.commit()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM exception_type WHERE name = ? AND module = ?", (ex_name, ex_module))
    data = cursor.fetchone()
    return data[0]


def create_exception_instance_table(conn: sqlite3.Connection) -> None:
    """Create the exception_instance table if it doesn't exist"""
    sql_create_exception_instance_table = """CREATE TABLE IF NOT EXISTS exception_instance (
                                                record_id TEXT PRIMARY KEY,
                                                type_id INTEGER,
                                                args TEXT,
                                                str_repr TEXT,
                                                comments TEXT,
                                                FOREIGN KEY (type_id) REFERENCES exception_type (id)
                                            );"""
    cursor = conn.cursor()
    cursor.execute(sql_create_exception_instance_table)


def insert_exception_instance(conn: sqlite3.Connection, record_id: str, ex: BaseException, comments: str = "") -> None:
    """Insert a new row into the exception_instance table"""
    ex_class = ex.__class__
    ex_name = ex_class.__name__
    ex_module = ex_class.__module__

    # Find the type_id from the exception_type table
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM exception_type WHERE name = ? AND module = ?", (ex_name, ex_module))
    type_data = cursor.fetchone()

    if type_data is not None:
        type_id = type_data[0]
        ex_args = str(ex.args)
        ex_str_repr = str(ex)

        # Insert new exception instance
        sql_insert_exception_instance = """INSERT INTO exception_instance 
                                           (record_id, type_id, args, str_repr, comments) 
                                           VALUES (?, ?, ?, ?, ?)"""
        cursor.execute(sql_insert_exception_instance, (record_id, type_id, ex_args, ex_str_repr, comments))
        conn.commit()


def create_traceback_info_table(conn: sqlite3.Connection) -> None:
    """Create the traceback_info table if it doesn't exist"""
    sql_create_traceback_info_table = """CREATE TABLE IF NOT EXISTS traceback_info (
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            exception_instance_id TEXT,
                                            frame_number INTEGER,
                                            f_locals TEXT,
                                            f_globals TEXT,
                                            FOREIGN KEY (exception_instance_id) REFERENCES exception_instance (id)
                                        );"""
    cursor = conn.cursor()
    cursor.execute(sql_create_traceback_info_table)


def insert_traceback_info(conn: sqlite3.Connection, exception_instance_id: str, tb) -> None:
    """Insert traceback information for each frame"""
    cursor = conn.cursor()
    frame_number = 0

    while tb:
        frame = tb.tb_frame
        f_locals = json.dumps(frame.f_locals, default=str)
        f_globals = json.dumps(frame.f_globals, default=str)

        sql_insert_traceback_info = """INSERT INTO traceback_info 
                                       (exception_instance_id, frame_number, f_locals, f_globals) 
                                       VALUES (?, ?, ?, ?)"""
        cursor.execute(sql_insert_traceback_info, (exception_instance_id, frame_number, f_locals, f_globals))

        tb = tb.tb_next
        frame_number += 1


if __name__ == "__main__":

    def run():
        # Example usage
        db_file = "path_to_your_database.db"
        conn = create_connection(db_file)
        if conn is not None:
            create_exception_type_table(conn)
            create_exception_instance_table(conn)
            create_traceback_info_table(conn)
            try:
                _ = 2 / 0
            except Exception as ex:
                insert_exception_type(conn, ex)
                # Insert exception instance and get its ID
                ex.add_note("Hello!")
                insert_exception_instance(conn, "abc", ex, "Comments about the exception")
                cursor = conn.cursor()
                cursor.execute("SELECT last_insert_rowid()")
                exception_instance_id = cursor.fetchone()[0]
                # Insert traceback info
                insert_traceback_info(conn, exception_instance_id, ex.__traceback__)

    run()

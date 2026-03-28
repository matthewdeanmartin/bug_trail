import importlib.metadata
import json
import sqlite3
import uuid
from collections.abc import Generator, Mapping
from contextlib import contextmanager
from typing import Any


@contextmanager
def create_connection(db_file: str) -> Generator[sqlite3.Connection, None, None]:
    """
    Establishes a connection to the SQLite database and ensures it's closed
    properly using a context manager.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        yield conn
    finally:
        if conn:
            conn.close()


def create_python_libraries_table(conn: sqlite3.Connection) -> None:
    sql_create_table = """CREATE TABLE IF NOT EXISTS python_libraries (
                              row_id TEXT PRIMARY KEY,
                              library_name TEXT NOT NULL,
                              version TEXT NOT NULL,
                              urls TEXT,
                              snapshot_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                          );"""

    cursor = conn.cursor()
    cursor.execute(sql_create_table)


def insert_python_library(conn: sqlite3.Connection, library_name: str, version: str, urls: dict[str, str]) -> None:
    sql_insert_library = """INSERT INTO python_libraries (row_id, library_name, version, urls)
                            VALUES (?, ?, ?, ?)"""
    cursor = conn.cursor()  # Corrected: This should be conn.cursor(), not conn.select()
    row_id = str(uuid.uuid4())
    cursor.execute(sql_insert_library, (row_id, library_name, version, json.dumps(urls)))
    conn.commit()


# Modified type hint for the metadata object
def get_installed_packages() -> Generator[tuple[str, str, Mapping[str, Any]], None, None]:  # type: ignore
    for package in importlib.metadata.distributions():
        # package.metadata in 3.9 is an email.message.Message object,
        # which behaves like a dictionary. We'll use Mapping[str, Any]
        # to represent its dictionary-like behavior without
        # relying on the internal email.message.Message type or the
        # not-yet-exposed PackageMetadata.
        yield package.metadata["Name"], package.version, package.metadata  # type: ignore


def record_venv_info(conn: sqlite3.Connection) -> None:
    if conn is None:
        raise TypeError("Need live connection")
    create_python_libraries_table(conn)
    for name, version, the_metadata in get_installed_packages():
        urls: dict[str, str] = {}  # Initialize urls as a Dict

        # Iterate over metadata items to find URLs.
        # the_metadata is a Mapping[str, Any]
        for key, value in the_metadata.items():
            if isinstance(value, str) and value.strip().lower().startswith("http"):
                urls[key] = value

        # Special handling for 'Project-URL' which can contain multiple URLs
        # In 3.9, the_metadata.get_all works for multi-value headers.
        project_urls = the_metadata.get_all("Project-URL")  # type: ignore
        if project_urls:
            for url_entry in project_urls:
                try:
                    # Use split with maxsplit to handle commas in the URL value itself
                    key, value = url_entry.split(",", 1)
                    urls[key.strip()] = value.strip()
                except ValueError:
                    # Handle cases where the Project-URL might not be in the expected format
                    pass

        insert_python_library(conn, name, version, urls)

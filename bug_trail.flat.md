# Contents of bug_trail source tree

## File: data_code.py

```python
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


def table_row_count(db_path: str, table_name: str) -> int:
    if table_name not in ALL_TABLES:
        raise TypeError("Bad table name.")
    conn = connect(db_path)
    try:
        cursor = conn.cursor()
    except sqlite3.ProgrammingError as ex:
        if "closed" in str(ex):
            # unexpectedly closed.
            conn = connect(db_path)
            cursor = conn.cursor()
        else:
            raise

    # table name restricted above
    cursor.execute(f"SELECT count(*) FROM {table_name};")  # nosec
    try:
        return cursor.fetchone()[0]
    except IndexError:
        return 0


def connect(db_path: str) -> sqlite3.Connection:
    """Open db, central code"""
    # Mock this to prevent extra dbs being created.
    return sqlite3.connect(db_path)


def fetch_log_data(db_path: str, limit: int = -1, offset: int = -1) -> list[dict[str, Any]]:
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
    conn = connect(db_path)
    logger.debug(f"Connected to {db_path}")
    try:
        cursor = conn.cursor()
    except sqlite3.ProgrammingError as ex:
        if "closed" in str(ex):
            # unexpectedly closed.
            conn = connect(db_path)
            cursor = conn.cursor()
        else:
            raise

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
    try:
        cursor = conn.cursor()
    except sqlite3.ProgrammingError as ex:
        if "closed" in str(ex):
            # unexpectedly closed.
            conn = connect(db_path)
            cursor = conn.cursor()
        else:
            raise

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
    try:
        cursor = conn.cursor()
    except sqlite3.ProgrammingError as ex:
        if "closed" in str(ex):
            # unexpectedly closed.
            conn = connect(db_path)
            cursor = conn.cursor()
        else:
            raise

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
            handler = BaseErrorLogHandler(db_path)
            handler.create_table()
            cursor.execute(query)
        else:
            raise

```

## File: exceptions.py

```python
"""
Look up info on exceptions.
"""


def docstring_for(ex):
    """
    Retrieve the docstring of the exception class.

    Parameters:
    ex (Exception): The exception instance.

    Returns:
    str: The docstring of the exception class.
    """
    # Get the class of the exception
    ex_class = ex.__class__

    # Get the docstring of the class
    return ex_class.__doc__


def documentation_link_for(ex):
    """
    Generate a link to the Python standard library documentation for the given exception.

    Parameters:
    ex (Exception): The exception instance.

    Returns:
    str: A URL to the documentation of the exception.
    """
    base_url = "https://docs.python.org/3/library/"
    ex_class = ex.__class__
    module = ex_class.__module__

    if module == "builtins":
        return f"{base_url}exceptions.html#{ex_class.__name__}"

    # Replace underscores with hyphens in the module name for the URL
    module_url = module.replace("_", "-")
    return f"{base_url}{module_url}.html#{module}.{ex_class.__name__}"


if __name__ == "__main__":
    try:
        _ = 1 / 0
    except ZeroDivisionError as e:
        print(docstring_for(e))
        print(documentation_link_for(e))

```

## File: fs_utils.py

```python
"""
This module contains functions related to file system operations.
"""

import logging
import os
import shutil

logger = logging.getLogger(__name__)


def empty_folder(folder_path: str) -> None:
    """
    Empty the folder at the given path

    Args:
        folder_path (str): Path to the folder to be emptied
    """
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        shutil.rmtree(folder_path)
        os.makedirs(folder_path, exist_ok=True)


def clear_data(log_folder: str, db_path: str) -> None:
    """
    Clear the database and log files
    """
    # Code to clear the database and log files
    empty_folder(log_folder)
    try:
        os.remove(db_path)
    except FileNotFoundError:
        pass


def get_containing_folder_path(file_path: str) -> str:
    """
    Get the absolute path of the folder containing the given file.

    Args:
        file_path (str): Path to the file (__file__)

    Returns:
        str: Absolute path of the containing folder
    """
    return os.path.abspath(os.path.dirname(file_path))


def is_git_repo(path: str) -> bool:
    """
    Check if the path is inside a git repository by looking for a .git directory.

    Args:
        path (str): The directory path to check.

    Returns:
        bool: True if inside a git repo, False otherwise.
    """
    current_path = path
    while current_path != os.path.dirname(current_path):
        if os.path.isdir(os.path.join(current_path, ".git")):
            return True
        current_path = os.path.dirname(current_path)
    return False


def prompt_and_update_gitignore(repo_path: str) -> None:
    """Prompt the user to ignore logs and update .gitignore accordingly."""
    if not is_git_repo(repo_path):
        return

    gitignore_path = os.path.join(repo_path, ".gitignore")

    # Check if .gitignore exists and 'logs' is already listed
    if os.path.exists(gitignore_path):
        with open(gitignore_path, encoding="utf-8") as file:
            if "logs" in file.read():
                print("'logs' directory is already ignored in .gitignore.")
                return

    # Prompt user for action
    response = (
        input("This directory is a Git repository. Do you want to ignore 'logs' directory? (y/n): ").strip().lower()
    )
    if (response.lower() + "xxx")[0] == "y":
        with open(gitignore_path, "a", encoding="utf-8") as file:
            file.write("\nlogs/")
        print("'logs' directory is now ignored in .gitignore.")
    else:
        print("No changes made to .gitignore.")


def copy_assets(destination: str) -> str:
    """Copy images, style sheets, etc to next web report folder
    Args:
        destination (str): report folder
    """
    src = os.path.join(os.path.dirname(__file__), "assets")
    result = shutil.copytree(src, destination, dirs_exist_ok=True)
    return result

```

## File: incremental.py

```python
"""Incremental file watcher for database changes using watchdog."""

from __future__ import annotations

import time
from collections.abc import Callable

from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer


class DbChangedHandler(FileSystemEventHandler):
    """Event handler that triggers a target function when a .db file is modified."""

    def __init__(self, target):
        """
        Initialize the event handler with a target function to call when a .db file is modified.
        """
        self.target = target
        super().__init__()

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent):
        """
        Handle file modified events.

        Args:
            event (FileModifiedEvent): The event that triggered the handler.
        """
        if isinstance(event, FileModifiedEvent):
            if str(event.src_path).endswith(".db"):
                print(event)
                self.target()


def watch_for_changes(path: str, target: Callable[[], None]) -> None:
    """
    Watch for changes in a directory and trigger a target function when a .db file is modified.

    Args:
        path (str): The directory to watch for changes.
        target (Callable[[], None]): The function to call when a change is detected.
    """
    event_handler = DbChangedHandler(target)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

```

## File: pygments_job.py

```python
"""
Highlight all python files in a directory and its subdirectories and save them as HTML files

pygmentize -g -O full,style=monokai,linenos=1 **/*.py
"""

import glob
import logging
import os

from pygments import highlight
from pygments.formatters import HtmlFormatter  # pylint: disable=no-name-in-module
from pygments.lexers import PythonLexer  # pylint: disable=no-name-in-module

logger = logging.getLogger(__name__)


def highlight_python_files(root_directory: str, output_directory: str, ctags_file: str) -> int:
    """
    Highlight all python files in a directory and its subdirectories and save them as HTML files
    Args:
        root_directory (str): The root directory to search for python files
        output_directory (str): The directory to save the HTML files
    Returns:
        int: The number of files highlighted
    """
    if not output_directory:
        logger.warning("No output directory provided, skipping highlighting.")
        return 0
    if not root_directory:
        logger.warning("No root directory provided, skipping highlighting.")
        return 0
    output_directory += "/src/"
    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Define the formatter with the desired options
    args = {
        "full": True,
        "style": "staroffice",  # Bad contrast! "monokai",
        "linenos": True,
        "lineanchors": "line",
        "anchorlinenos": True,
    }
    # if ctags_file:
    #     args["tagsfile"] = ctags_file
    #     #  url = self.tagurlformat % {'path': base, 'fname': filename,
    #     #                                                'fext': extension}
    #     args["tagurlformat"] = "%(path)s%(fname)s%(fext)s"
    #

    logger.info("Highlighting python files in %s", root_directory)
    for key, value in args.items():
        logger.debug("%s: %s", key, value)
    formatter = HtmlFormatter(**args)

    # Search for all .py files in the given directory and its subdirectories
    count = 0
    search_string = os.path.join(root_directory, "**", "*.py")
    for file_path in glob.glob(search_string, recursive=True):
        count += 1
        with open(file_path, encoding="utf-8") as file:
            code = file.read()
            # Highlight the code
            highlighted_code = highlight(code, PythonLexer(), formatter)

            # Define the output file path
            relative_path = os.path.relpath(file_path, root_directory)
            output_file_path = os.path.join(output_directory, relative_path + ".html")

            # Ensure the subdirectories in the output path exist
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

            logger.debug("Saving highlighted code to %s", output_file_path)
            # Save the highlighted code to the output file
            with open(output_file_path, "w", encoding="utf-8") as output_file:
                output_file.write(highlighted_code)
    if count == 0:
        print(f"No source files found, searched at {search_string}")
    return count

```

## File: views.py

```python
"""
This module contains the functions for rendering the HTML templates
"""

import logging

from bug_trail.fs_utils import copy_assets, empty_folder
from bug_trail.pygments_job import highlight_python_files
from bug_trail.view_detail import render_detail
from bug_trail.view_main import render_main
from bug_trail.view_python_environment import render_python_environment
from bug_trail.view_system_info import render_system_info

logger = logging.getLogger(__name__)


def render_all(db_path: str, logs_folder: str, source_folder: str, ctags_file: str) -> None:
    """
    Render all the pages

    Args:
        db_path (str): Path to the SQLite database
        logs_folder (str): Path to the folder containing the log files
        source_folder (str): Path to the folder containing the source code
        ctags_file (str): Path to the ctags file
    """
    logger.debug(f"Emptying {logs_folder}")
    empty_folder(logs_folder)
    logger.debug("Rendering main page")
    render_main(db_path, logs_folder, source_folder)
    logger.debug("Rendering detail pages")
    render_detail(db_path, logs_folder, source_folder)
    logger.debug("Highlighting source code")
    highlight_python_files(source_folder, logs_folder, ctags_file)
    copy_assets(logs_folder)
    render_python_environment(db_path, logs_folder)
    render_system_info(db_path, logs_folder)


if __name__ == "__main__":
    render_all(db_path="error_log.db", logs_folder="logs", source_folder="../bug_trail", ctags_file="")

```

## File: view_detail.py

```python
"""
Detail page. Displays one error log entry.
"""

import json
import logging
import os

from bug_trail.data_code import fetch_log_data_grouped
from bug_trail.view_shared import (
    add_url_to_source_context,
    detail_file_name_grouped,
    humanize_time,
    humanize_time_span,
    initialize_jinja,
    path_to_file_url,
    replace_msg_args,
)

logger = logging.getLogger(__name__)


def render_detail(db_path: str, log_folder: str, source_folder: str) -> str:
    """
    Render the detail page of a log entry

    Args:
        db_path (str): Path to the SQLite database
        log_folder (str): Path to the folder containing the log files
        source_folder (str): Path to the folder containing the source code

    Returns:
        str: The location of the detail page
    """
    env = initialize_jinja()
    log_data = fetch_log_data_grouped(db_path)  # Your log records here

    # Render the template with the selected log data
    template = env.get_template("view_detail.jinja")

    location = ""
    for log_entry in log_data:
        # Selected log record for display
        selected_log = log_entry
        # Using a unique key for each log entry, like a timestamp or a combination of fields
        key = detail_file_name_grouped(selected_log)

        location = f"{log_folder}/{key}"
        if os.path.exists(location):
            print(f"Already exists, {location}, skipping")

        if log_entry["ExceptionDetails"]["exception_hierarchy"]:
            exception_hierarchy = json.loads(log_entry["ExceptionDetails"]["exception_hierarchy"])
            # why as I logging this?
            # logger.info(exception_hierarchy)
            interesting_hierarchy = []
            for the_type, description in exception_hierarchy:
                if the_type not in ("type", "object"):
                    interesting_hierarchy.append({"type": the_type, "description": description})
            if not interesting_hierarchy:
                del log_entry["ExceptionDetails"]["exception_hierarchy"]
            else:
                log_entry["ExceptionDetails"]["exception_hierarchy"] = interesting_hierarchy

        # Clean up time
        temporal_details = selected_log["TemporalDetails"]
        temporal_details["created"] = humanize_time(temporal_details["created"], temporal_details["msecs"])
        del temporal_details["msecs"]
        formatted_time, apx_time = humanize_time_span(temporal_details["relativeCreated"])
        temporal_details["relativeCreated"] = f"{formatted_time} ({apx_time})"

        # Consolidate level
        message_details = selected_log["MessageDetails"]
        message_details["levelname"] = str(message_details["levelname"]) + f" ({str(message_details['levelno'])})"
        del message_details["levelno"]

        # Consolidate msg and args
        replace_msg_args(message_details)

        # Convert pathname to url
        source_context = selected_log["SourceContext"]

        # TODO: make this pretty

        path_to_file_url(source_context, log_folder, source_folder)
        add_url_to_source_context(source_context)

        # Remove empty fields
        for section in selected_log:
            to_delete = []
            for section_name, value in selected_log[section].items():
                if value is None or value == "":
                    to_delete.append(section_name)
            for section_name in to_delete:
                del selected_log[section][section_name]
        to_delete = []
        for section_name in selected_log:
            if len(selected_log[section_name]) == 0:
                to_delete.append(section_name)
        for section_name in to_delete:
            del selected_log[section_name]

        html_output = template.render(log=selected_log)

        # Write `html_output` to a file
        os.makedirs(location.rsplit("/", 1)[0], exist_ok=True)
        logger.info(f"Writing detail page to {location}")
        with open(location, "w", encoding="utf-8") as f:
            f.write(html_output)
    return location

```

## File: view_main.py

```python
"""
This module contains the functions for rendering the HTML templates
"""

import logging
import os

import bug_trail.data_code as data
from bug_trail.view_shared import (
    add_url_to_source_context,
    detail_file_name,
    humanize_time,
    initialize_jinja,
    path_to_file_url,
    replace_msg_args,
)

logger = logging.getLogger(__name__)


def render_main(db_path: str, log_folder: str, source_folder: str) -> None:
    """
    Render the main page of the log viewer

    Args:
        db_path (str): Path to the SQLite database
        log_folder (str): Path to the folder containing the log files
        source_folder (str): Path to the folder containing the source code
    """
    env = initialize_jinja()
    template = env.get_template("view_main.jinja")

    row_count = data.table_row_count(db_path, "logs")

    pages = {}
    for page in range(0, row_count, 100):
        if page == 0:
            index = f"{log_folder}/index.html"
        else:
            index = f"{log_folder}/index{page}.html"
        pages[page] = index

    for page in range(0, row_count, 100):
        log_data = data.fetch_log_data(db_path, limit=100, offset=page)

        for log_entry in log_data:
            log_entry["detailed_filename"] = detail_file_name(log_entry)

            log_entry["filename"] = f"{log_entry['filename']} ({log_entry['lineno']})"
            path_to_file_url(log_entry, log_folder, source_folder)
            add_url_to_source_context(log_entry)

            log_entry["created"] = humanize_time(log_entry["created"], log_entry["msecs"])

            # Consolidate msg and args
            replace_msg_args(log_entry)

        # Render the template with log data
        html_output = template.render(logs=log_data, pages=pages)

        if page == 0:
            index = f"{log_folder}/index.html"
        else:
            index = f"{log_folder}/index{page}.html"
        os.makedirs(index.rsplit("/", 1)[0], exist_ok=True)
        logger.info(f"Writing index to {index}")
        with open(index, "w", encoding="utf-8") as f:
            f.write(html_output)

```

## File: view_python_environment.py

```python
"""
This module contains the functions for rendering the HTML templates
"""

import json
import logging
import os

from bug_trail.data_code import fetch_table_as_list_of_dict
from bug_trail.view_shared import initialize_jinja

logger = logging.getLogger(__name__)


def render_python_environment(db_path: str, log_folder: str) -> None:
    """
    Render the main page of the log viewer

    Args:
        db_path (str): Path to the SQLite database
        log_folder (str): Path to the folder containing the log files
        source_folder (str): Path to the folder containing the source code
    """
    title = "python_environment"
    env = initialize_jinja()
    template = env.get_template(f"view_{title}.jinja")

    data = fetch_table_as_list_of_dict(db_path, "python_libraries")

    for datum in data:
        # expand complex types
        datum["urls"] = json.loads(datum["urls"])

    # Render the template with log data
    html_output = template.render(logs=data)

    index = f"{log_folder}/{title}.html"
    os.makedirs(index.rsplit("/", 1)[0], exist_ok=True)
    logger.info(f"Writing index to {index}")
    with open(index, "w", encoding="utf-8") as f:
        f.write(html_output)

```

## File: view_shared.py

```python
"""
This module contains the functions for rendering the HTML templates
"""

import ast
import datetime
import logging
from typing import Any

import humanize
from jinja2 import Environment, FileSystemLoader

from bug_trail.fs_utils import get_containing_folder_path

logger = logging.getLogger(__name__)


def humanize_time(created: float, msecs: float = 0.0) -> str:
    """
    Convert epoch time to a human-readable format and calculate the relative time passed.

    Args:
        created (float): Time in seconds since the epoch.
        msecs (float): Millisecond portion of 'created'.

    Returns:
        str: Human-readable time format.
    """
    if not isinstance(created, float):
        created = float(created)
    if not isinstance(msecs, float):
        msecs = float(msecs)
    # Combine created and msecs and convert to a datetime object
    full_datetime = datetime.datetime.fromtimestamp(created + msecs / 1000.0)

    # Format the date
    formatted_date = full_datetime.strftime("%B %d, %Y")

    # Calculate and format the relative time passed
    relative_time = humanize.naturaltime(datetime.datetime.now() - full_datetime)

    return f"{formatted_date}, {relative_time}"


def humanize_time_span(milliseconds: float):
    """
    Convert a time span in seconds to a human-readable format.

    Args:
        milliseconds (float): Time span in milliseconds.

    Returns:
        tuple: A tuple containing a precise human-readable format and a general description.
    """
    if not isinstance(milliseconds, float):
        milliseconds = float(milliseconds)
    # Define thresholds (in seconds) for different time units

    thresholds = {
        "millisecond": 1,  # Below 1 second
        "second": 60,  # Below 1 minute
        "minute": 60 * 60,  # Below 1 hour
        "hour": 60 * 60 * 24,  # Below 1 day
        "day": 60 * 60 * 24 * 30,  # Below 1 month
        "month": 60 * 60 * 24 * 30 * 12,  # Below 1 year
    }
    seconds = milliseconds / 1000.0

    unit = "N/A"

    # Find the largest unit of time to use
    for unit, limit in thresholds.items():  # noqa: B007
        # we use the fact that python holds on the the value
        # of a variable from the last iteration of a loop
        if seconds < limit:
            break

    # Convert to the appropriate unit and format the output
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
    else:  # 'month' or larger
        precise_format = f"{seconds / (3600 * 24 * 30):.0f} months"

    # Use humanize for a general description
    general_description = humanize.naturaldelta(seconds)

    return precise_format, general_description


# Example usage
# Assume relative_time_seconds = 116.669178009033
# humanized_time = humanize_time_span(relative_time_seconds)
# print(humanized_time)


def pretty_column_name(column_name: str) -> str:
    """
    Transform a column name into a pretty name for display
    Args:
        column_name (str): The column name to be transformed
    Returns:
        str: The transformed column name
    >>> pretty_column_name("lineno")
    'Line Number'
    """
    # Dictionary for special cases
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

    # Check if the column name is a special case
    if column_name in special_cases:
        return special_cases[column_name]

    # Rule-based transformation: snake_case to Title Case
    pretty_name = column_name.replace("_", " ").title()
    return pretty_name


def detail_file_name(selected_log: dict[str, str]) -> str:
    """
    Generate a filename for the detail page of a log entry

    Args:
        selected_log (dict[str, str]): The selected log entry
    Returns:
        str: The filename for the detail page

    >>> detail_file_name({'created': '2021-08-31 12:00:00.000000', 'filename': 'bug_trail/data_code.py', 'lineno': 1})
    'detail_2021-08-31 12:00:00_000000_bug_trail/data_code_py_1.html'
    """
    key = (
        f"{str(selected_log['created']).replace('.','_')}_"
        f"{selected_log['filename'].replace('.','_')}_"
        f"{selected_log['lineno']}"
    )
    return f"detail_{key}.html"


def detail_file_name_grouped(selected_log: dict[str, dict[str, str]]) -> str:
    """
    Generate a filename for the detail page of a log entry with grouped data

    Args:
        selected_log (dict[str, str]): The selected log entry
    Returns:
        str: The filename for the detail page

    >>> detail_file_name_grouped({'TemporalDetails': {'created': '2021-08-31 12:00:00.000000'}, 'SourceContext': {'filename': 'bug_trail/data_code.py', 'lineno': 1}})
    'detail_2021-08-31 12:00:00_000000_bug_trail/data_code_py_1.html'
    """
    key = (
        f"{str(selected_log['TemporalDetails']['created']).replace('.','_')}_"
        f"{selected_log['SourceContext']['filename'].replace('.','_')}_"
        f"{selected_log['SourceContext']['lineno']}"
    )
    return f"detail_{key}.html"


def add_url_to_source_context(source_context: dict[str, Any]):
    """
    Add a url to the source context with line number.

    Args:
        source_context (dict[str, Any]): The source context
    """
    if not source_context["pathname"]:
        raise ValueError("Source context has no pathname")
    source_context["pathname"] = f"{source_context['pathname']}.html#line-{source_context['lineno']}"
    return source_context


def find_and_return_after(text: str, search_string: str) -> str:
    """
    Find the last occurrence of a string and return everything after it.

    Args:
        text (str): The text to search in.
        search_string (str): The string to search for.

    Returns:
        str: Everything after the first occurrence of the search string.
             Returns an empty string if the search string is not found.
    """
    # Find the index of the last occurrence of the search string
    index = text.rfind(search_string)

    # If the string is found, return everything after it
    if index != -1:
        return text[index + len(search_string) :]

    # If the string is not found, return an empty string
    return ""


def path_to_file_url(source_context: dict[str, Any], logs_folder, source_folder: str) -> None:
    """
    Convert a path to a file url
    Args:
        source_context (dict[str, Any]): The source context
        logs_folder (str): The folder containing the logs
        source_folder (str): The folder containing the source code
    """
    logs_folder = logs_folder.replace("\\", "/")
    relative_path = find_and_return_after(
        source_context["pathname"].replace("\\", "/"), source_folder.replace("\\", "/")
    )
    source_context["pathname"] = f"file://{logs_folder}/src/{relative_path}"


def replace_msg_args(message_details: dict[str, Any]) -> None:
    """Handle % format strings

    Args:
        message_details (dict[str, Any]): The message details
    """
    if message_details["args"] and message_details["args"] != "()":
        args_dict = ast.literal_eval(message_details["args"])
        try:
            message_details["msg"] = message_details["msg"] % args_dict
        except TypeError:
            # can't evaluate
            message_details["msg"] = f'{message_details["msg"]} % {args_dict}'
    del message_details["args"]


def initialize_jinja() -> Environment:
    """Set up Jinja2 environment"""
    current = get_containing_folder_path(__file__)
    env = Environment(loader=FileSystemLoader(current), autoescape=True)
    env.filters["pretty"] = pretty_column_name
    return env

```

## File: view_system_info.py

```python
"""
This module contains the functions for rendering the HTML templates
"""

import logging
import os

from bug_trail.data_code import fetch_table_as_list_of_dict
from bug_trail.view_shared import initialize_jinja

logger = logging.getLogger(__name__)


def render_system_info(db_path: str, log_folder: str) -> None:
    """
    Render the main page of the log viewer

    Args:
        db_path (str): Path to the SQLite database
        log_folder (str): Path to the folder containing the log files
        source_folder (str): Path to the folder containing the source code
    """
    title = "system_info"
    env = initialize_jinja()
    template = env.get_template(f"view_{title}.jinja")

    data = fetch_table_as_list_of_dict(db_path, "system_info")

    # Render the template with log data
    html_output = template.render(log=data[0])

    index = f"{log_folder}/{title}.html"
    os.makedirs(index.rsplit("/", 1)[0], exist_ok=True)
    logger.info(f"Writing index to {index}")
    with open(index, "w", encoding="utf-8") as f:
        f.write(html_output)

```

## File: __about__.py

```python
"""Metadata for bug_trail."""

__all__ = [
    "__title__",
    "__version__",
    "__description__",
    "__readme__",
    "__requires_python__",
    "__keywords__",
    "__status__",
]

__title__ = "bug_trail"
__version__ = "3.0.1"
__description__ = "Local static html error logger to use while developing python code."
__readme__ = "README.md"
__requires_python__ = ">=3.12"
__keywords__ = ["error logging", "html log report"]
__status__ = "4 - Beta"

```

## File: __init__.py

```python
"""
CLI tool generates a static website for data capture by cli.
"""

__all__ = ["__version__"]

from bug_trail.__about__ import __version__

```

## File: __main__.py

```python
"""
Main entry point for the CLI.
"""

import argparse
import logging
import os
import sys

from bug_trail_core import read_config

import bug_trail.fs_utils as fs_utils
import bug_trail.views as views
from bug_trail.__about__ import __version__
from bug_trail.incremental import watch_for_changes


def main() -> int:
    """
    Main entry point for the CLI.

    Returns:
        int: 0 if successful, 1 if not
    """
    parser = argparse.ArgumentParser(description="Tool for local logging and error reporting.")
    parser.add_argument("--clear", action="store_true", help="Clear the database and log files")

    parser.add_argument(
        "--config", type=str, help="Path to the configuration file", required=False, default="pyproject.toml"
    )

    parser.add_argument("--version", action="version", version="%(prog)s " + f"{__version__}")
    parser.add_argument("--verbose", action="store_true", help="verbose output")
    parser.add_argument("--watch", action="store_true", help="watch database, generate continuously")
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    section = read_config(args.config)
    parser.add_argument("--output", action="store_true", help="Where to output the logs", default=section.report_folder)
    parser.add_argument("--db", action="store_true", help="Where to store the database", default=section.database_path)
    parser.add_argument(
        "--source", action="store_true", help="Where the app's source code is", default=section.source_folder
    )
    parser.add_argument(
        "--ctags_file", action="store_true", help="Where the app's ctags file is", default=section.ctags_file
    )

    args = parser.parse_args()
    db_path = args.db
    log_folder = args.output
    source_folder = args.source
    ctags_file = args.ctags_file
    if args.clear:
        print("Clearing database and log files...")
        fs_utils.clear_data(log_folder, db_path)
        print("Done")
        return 0

    # Right now, default behavior uses platform dirs and is safe.
    # This is only necessary if the user points config at own git repo folder
    # fs_utils.prompt_and_update_gitignore(".")
    # Default actions

    print("Generating log website:")
    print(f"Using source db at {db_path}")
    if ctags_file:
        print(f"Using ctags file at {ctags_file}")
    print(f"Using logs at {log_folder}")
    universal_path = log_folder.replace("\\", "/")
    print(f"Open at  file://{universal_path}/index.html")
    if not source_folder:
        print("No source folder specified, hyperlinks to source code will not work")

    if args.watch:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        watch_for_changes(
            os.path.dirname(db_path), lambda: views.render_all(db_path, log_folder, source_folder, ctags_file)
        )
    else:
        views.render_all(db_path, log_folder, source_folder, ctags_file)

    return 0


if __name__ == "__main__":
    sys.exit(main())

```


"""
This module contains the functions for rendering the HTML templates
"""
import ast
import datetime
import os
from typing import Any

import humanize
from jinja2 import Environment, FileSystemLoader

from bug_trail.data_code import fetch_log_data, fetch_log_data_grouped
from bug_trail.fs_utils import empty_folder, get_containing_folder_path
from bug_trail.pygments_job import highlight_python_files


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


def render_main(db_path: str, log_folder: str, source_folder: str) -> None:
    """
    Render the main page of the log viewer

    Args:
        db_path (str): Path to the SQLite database
        log_folder (str): Path to the folder containing the log files
        source_folder (str): Path to the folder containing the source code
    """
    env = initialize_jinja()
    template = env.get_template("log_overview.html")

    log_data = fetch_log_data(db_path)

    for log_entry in log_data:
        log_entry["detailed_filename"] = detail_file_name(log_entry)

        log_entry["filename"] = f"{log_entry['filename']} ({log_entry['lineno']})"
        path_to_file_url(log_entry, log_folder, source_folder)
        add_url_to_source_context(log_entry)

        log_entry["created"] = humanize_time(log_entry["created"], log_entry["msecs"])

        # Consolidate msg and args
        replace_msg_args(log_entry)

    # Render the template with log data
    html_output = template.render(logs=log_data)

    index = f"{log_folder}/index.html"
    os.makedirs(index.rsplit("/", 1)[0], exist_ok=True)
    with open(index, "w", encoding="utf-8") as f:
        f.write(html_output)


def add_url_to_source_context(source_context: dict[str, Any]):
    """
    Add a url to the source context with line number.

    Args:
        source_context (dict[str, Any]): The source context
    """
    source_context["pathname"] = f"{source_context['pathname']}.html#line-{source_context['lineno']}"
    return source_context


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
    template = env.get_template("log_detail.html")

    location = ""
    for log_entry in log_data:
        # Selected log record for display
        selected_log = log_entry
        # Using a unique key for each log entry, like a timestamp or a combination of fields
        key = detail_file_name_grouped(selected_log)

        location = f"{log_folder}/{key}"

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
        with open(location, "w", encoding="utf-8") as f:
            f.write(html_output)
    return location


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


def render_all(db_path: str, logs_folder: str, source_folder: str, ctags_file: str) -> None:
    """
    Render all the pages

    Args:
        db_path (str): Path to the SQLite database
        logs_folder (str): Path to the folder containing the log files
        source_folder (str): Path to the folder containing the source code
        ctags_file (str): Path to the ctags file
    """
    empty_folder(logs_folder)
    render_main(db_path, logs_folder, source_folder)
    render_detail(db_path, logs_folder, source_folder)
    highlight_python_files(source_folder, logs_folder, ctags_file)


if __name__ == "__main__":
    render_all(db_path="error_log.db", logs_folder="logs", source_folder="../bug_trail", ctags_file="")

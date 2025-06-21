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
            print(exception_hierarchy)
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

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

    conn = data.connect(db_path)
    row_count = data.table_row_count(conn, "logs")

    pages = {}
    for page in range(0, row_count, 100):
        if page == 0:
            index = f"{log_folder}/index.html"
        else:
            index = f"{log_folder}/index{page}.html"
        pages[page] = index

    for page in range(0, row_count, 100):
        log_data = data.fetch_log_data(conn, db_path, limit=100, offset=page)

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

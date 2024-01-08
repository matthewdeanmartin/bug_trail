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

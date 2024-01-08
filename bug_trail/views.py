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

"""
Configuration module for Bug Trail.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

try:
    import tomllib

    USE_TOMLLIB = True
except ImportError:
    USE_TOMLLIB = False
try:
    import toml
except ImportError:
    pass
import platformdirs


@dataclass
class BugTrailConfig:
    """Dataclass to hold Bug Trail configuration."""

    app_name: str
    app_author: str
    report_folder: str
    database_path: str
    source_folder: str
    ctags_file: str


def read_config(config_path: str) -> BugTrailConfig:
    """
    Read the Bug Trail configuration from a pyproject.toml file.

    Args:
        config_path (str): Path to the pyproject.toml file.

    Returns:
        BugTrailConfig: Configuration object for Bug Trail.
    """
    # Read the TOML file

    try:
        if USE_TOMLLIB:
            with open(config_path, "rb") as handle:
                bug_trail_config = tomllib.load(handle)
        else:
            bug_trail_config = toml.load(config_path)
    # toml and tomllib raise different errors
    except BaseException:
        bug_trail_config = {}

    section = bug_trail_config.get("tool", {}).get("bug_trail", {})

    # Set default values
    app_name = section.get("app_name", "bug_trail")
    app_author = section.get("app_author", "bug_trail")

    default_data_dir = platformdirs.user_data_dir(app_name, app_author, ensure_exists=True)
    default_config_dir = platformdirs.user_config_dir(app_name, app_author, ensure_exists=True)

    report_folder = section.get("report_folder", os.path.join(default_data_dir, "reports"))
    database_path = section.get("database_path", os.path.join(default_config_dir, "bug_trail.db"))

    # input!
    source_folder = section.get("source_folder", "")
    ctags_file = section.get("ctags_file", "")
    return BugTrailConfig(app_name, app_author, report_folder, database_path, source_folder, ctags_file)


if __name__ == "__main__":

    def run() -> None:
        """Example usage"""
        config = read_config("../pyproject.toml")
        print(config)

    run()

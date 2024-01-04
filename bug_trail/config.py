"""
Configuration module for Bug Trail.
"""
import os
from dataclasses import dataclass

import toml
from platformdirs import user_config_dir, user_data_dir


@dataclass
class BugTrailConfig:
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
        bug_trail_config = toml.load(config_path)

    except (FileNotFoundError, toml.TomlDecodeError):
        bug_trail_config = {}
    except TypeError:
        # print(f"Error reading config file: {e}")
        bug_trail_config = {}

    section = bug_trail_config.get("tool", {}).get("bug_trail", {})

    # Set default values
    app_name = section.get("app_name", "bug_trail")
    app_author = section.get("app_author", "bug_trail")

    default_data_dir = user_data_dir("bug_trail", app_author, ensure_exists=True)
    default_config_dir = user_config_dir("bug_trail", app_author, ensure_exists=True)

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

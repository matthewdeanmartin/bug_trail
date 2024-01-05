"""
Main entry point for the CLI.
"""
import argparse
import logging
import sys

from bug_trail_core import read_config

import bug_trail.fs_utils as fs_utils
import bug_trail.views as views
from bug_trail._version import __version__


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
    views.render_all(db_path, log_folder, source_folder, ctags_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())

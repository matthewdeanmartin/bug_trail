"""
Main entry point for the CLI.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from bug_trail_core import read_config
from bug_trail_core.__about__ import __version__


def main(argv: Sequence[str] | None = None) -> int:
    """
    Main entry point for the CLI.

    Returns:
        int: 0 if successful, 1 if not
    """
    parser = argparse.ArgumentParser(
        prog="bug_trail_core", description="Core library for bug_trail a tool for local logging and error reporting."
    )

    parser.add_argument(
        "--show-config",
        type=str,
        help="Path to the configuration file (usually pyproject.toml)",
        required=False,
    )
    parser.add_argument("--version", action="version", version="%(prog)s " + f"{__version__}")

    args = parser.parse_args(argv)
    if args.show_config:
        print("This is the core library. Install or run bug_trail to generate the website to view the logs.\n")
        print(read_config(args.show_config))
    else:
        print("This is the core library. Install or run bug_trail to generate the website to view the logs.\n")
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
Main entry point for the bug_trail CLI.

Subcommands:
    start          Launch the FastAPI web server.
    admin clear    Truncate all log tables (preserve schema).
    admin reset    Drop and recreate all tables.
"""

from __future__ import annotations

import argparse
import logging
import sys

from bug_trail_core import read_config

from bug_trail.__about__ import __version__


def _add_config_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--config",
        type=str,
        default="pyproject.toml",
        help="Path to the configuration file (default: pyproject.toml).",
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bug_trail",
        description="Local FastAPI web viewer for bug_trail error logs.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start", help="Start the web server.")
    _add_config_arg(start)
    start.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1).")
    start.add_argument("--port", type=int, default=7890, help="Port to bind (default: 7890).")
    start.add_argument("--db", type=str, default=None, help="Override database path from config.")
    start.add_argument("--source", type=str, default=None, help="Override source folder from config.")
    start.add_argument("--reload", action="store_true", help="Auto-reload on code changes (dev mode).")

    admin = subparsers.add_parser("admin", help="Data management commands.")
    admin_sub = admin.add_subparsers(dest="admin_command", required=True)

    admin_clear = admin_sub.add_parser("clear", help="Wipe rows from all log tables (keep schema).")
    _add_config_arg(admin_clear)
    admin_clear.add_argument("--db", type=str, default=None)

    admin_reset = admin_sub.add_parser("reset", help="Drop and recreate all tables.")
    _add_config_arg(admin_reset)
    admin_reset.add_argument("--db", type=str, default=None)

    return parser


def _resolve_db_path(args: argparse.Namespace) -> tuple[str, str]:
    section = read_config(args.config)
    db_path = getattr(args, "db", None) or section.database_path
    source_folder = getattr(args, "source", None) or section.source_folder
    return db_path, source_folder


def _cmd_start(args: argparse.Namespace) -> int:
    import uvicorn

    db_path, source_folder = _resolve_db_path(args)

    # Stash paths in env-ish globals for the app factory.
    from bug_trail import app as app_module

    app_module.configure(db_path=db_path, source_folder=source_folder)

    url = f"http://{args.host}:{args.port}"
    print(f"Bug Trail server starting at {url}")
    print(f"  Database: {db_path}")
    print(f"  Open {url}/help for setup instructions.")
    print("  Press Ctrl+C to stop.")

    uvicorn.run(
        "bug_trail.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info" if not args.verbose else "debug",
    )
    return 0


def _cmd_admin_clear(args: argparse.Namespace) -> int:
    from bug_trail.admin_ops import clear_all

    db_path, _ = _resolve_db_path(args)
    rows = clear_all(db_path)
    print(f"Cleared {rows} rows from {db_path}")
    return 0


def _cmd_admin_reset(args: argparse.Namespace) -> int:
    from bug_trail.admin_ops import reset_all

    db_path, _ = _resolve_db_path(args)
    reset_all(db_path)
    print(f"Reset database at {db_path}")
    return 0


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    if args.command == "start":
        return _cmd_start(args)
    if args.command == "admin":
        if args.admin_command == "clear":
            return _cmd_admin_clear(args)
        if args.admin_command == "reset":
            return _cmd_admin_reset(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())

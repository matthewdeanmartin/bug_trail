"""
Code-as-config for logging.
"""

import logging
import logging.config
from typing import Any

import bug_trail_core

bug_trail_config = bug_trail_core.read_config(config_path="pyproject.toml")


def configure_logging() -> dict[str, Any]:
    """Basic style"""
    logging_config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "standard": {"format": "[%(levelname)s] %(name)s: %(message)s"},
        },
        "handlers": {
            "default": {
                "level": "DEBUG",
                "formatter": "standard",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",  # Default is stderr
            },
            "bug_trail": {
                "level": "DEBUG",
                # "formatter": "standard",
                "class": "bug_trail_core.BugTrailHandler",
                "db_path": bug_trail_config.database_path,
                "minimum_level": logging.DEBUG,
            },
        },
        "loggers": {
            # root logger can capture too much
            "": {  # root logger
                "handlers": ["default", "bug_trail"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
    }

    debug_level_modules: list[str] = [
        "__main__",
    ]
    info_level_modules: list[str] = []
    warn_level_modules: list[str] = []

    for name in debug_level_modules:
        logging_config["loggers"][name] = {
            "handlers": ["default", "bug_trail"],
            "level": "DEBUG",
            "propagate": False,
        }

    for name in info_level_modules:
        logging_config["loggers"][name] = {
            "handlers": ["default", "bug_trail"],
            "level": "INFO",
            "propagate": False,
        }

    for name in warn_level_modules:
        logging_config["loggers"][name] = {
            "handlers": ["default", "bug_trail"],
            "level": "WARNING",
            "propagate": False,
        }
    return logging_config


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.config.dictConfig(configure_logging())

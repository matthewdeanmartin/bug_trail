"""
Generate some example code using a real code bases.
"""
import logging

import bug_trail_core

import fish_tank.__main__ as main

section = bug_trail_core.read_config(config_path="pyproject.toml")
handler = bug_trail_core.BugTrailHandler(section.database_path, minimum_level=logging.DEBUG)

logging.basicConfig(handlers=[handler], level=logging.DEBUG)

# Example usage
logger = logging.getLogger(__name__)

logger.error("If you can see this, error logging works")


if __name__ == "__main__":
    print("Running fish_tank.__main__")
    main.main()
else:
    print("what is up with this?")
    print(__name__)

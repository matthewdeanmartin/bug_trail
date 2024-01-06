"""Example usage

This is completely contrived.
"""

# Set up logging
import logging

import bug_trail
import bug_trail_core
section = bug_trail_core.read_config(config_path="pyproject.toml")
handler = bug_trail_core.BugTrailHandler(section.database_path, minimum_level=logging.WARNING)

logging.basicConfig(handlers=[handler], level=logging.ERROR)

# Example usage
logger = logging.getLogger(__name__)

logger.error("This is an error message")

logger.error("Some %(who)s like %(what)s.", {"who": "fools", "what": "this syntax"})

#
logger.warning("This is a warning 2.")

# Won't see these
logger.info("This is an info.")
logger.info("This is a debug.")


def run():
    # Example usage
    logger2 = logging.getLogger("adhoc")
    logger2.error("This is an ad hoc error message")

    logger.error("This is an error message")
    try:
        _ = 1 / 0
    except ZeroDivisionError as e:
        logger.exception(e)


run()

logger.error("Last message")

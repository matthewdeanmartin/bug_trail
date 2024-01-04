"""
Generate some example code using a real code bases.
"""
import logging
import multiprocessing
import threading

import bug_trail

# Example usage
logger = logging.getLogger(__name__)

section = bug_trail.read_config(config_path="pyproject.toml")
handler = bug_trail.BugTrailHandler(section.database_path, minimum_level=logging.DEBUG, single_threaded=False)

logging.basicConfig(handlers=[handler], level=logging.DEBUG)


def target():
    logger.info("This is", threading.current_thread().name)


def multiprocessing_target(what):
    logger.info("Another process - This is", threading.current_thread().name)


if __name__ == "__main__":
    # because the error message asked for it
    # freeze_support()

    logger.error("If you can see this, error logging works")

    for _ in range(4):
        threading.Thread(target=target).start()

    with multiprocessing.Pool(processes=4) as pool:
        print(pool.map(multiprocessing_target, range(10)))

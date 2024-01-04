import logging
import time

import bug_trail
from bug_trail.fs_utils import clear_data


def setup_logger(db_path):
    # Configure the logger
    logger = logging.getLogger("performance_test_logger")
    logger.setLevel(logging.DEBUG)
    handler = bug_trail.BugTrailHandler(db_path, minimum_level=logging.DEBUG)
    logger.addHandler(handler)
    return logger


def performance_test(logger, iterations):
    start_time = time.time()

    def throw_it():
        raise ValueError("To trigger call stack logic")

    for i in range(iterations):
        try:
            throw_it()
        except ValueError as ve:
            logger.exception(ve)
        logger.error("Error message %d", i)
        logger.info("Info message with string interpolation: %s", "test")
        if i % 2 == 0:
            logger.debug("Debug message for even number: %d", i)
        else:
            logger.warning("Warning message for odd number: %d", i)

    end_time = time.time()
    print(f"Test completed in {end_time - start_time} seconds")


def main():
    section = bug_trail.read_config(config_path="pyproject.toml")
    clear_data(section.report_folder, section.database_path)  # Clear the database before starting the test
    logger = setup_logger(section.database_path)
    performance_test(logger, 5000)
    logger.handlers[0].close()
    clear_data(section.report_folder, section.database_path)  # Clear the database before starting the test
    # logger.handlers[0].close()  # Properly close the handler


if __name__ == "__main__":
    main()

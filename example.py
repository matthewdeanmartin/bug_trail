"""
Attempt to raise a wide variety of exceptions.
"""

import os
import logging

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

# Custom Exception Class
class CustomError(Exception):
    def __init__(self, message):
        self.message = message

# Function to demonstrate IndexError
def demonstrate_index_error():
    sample_list = [1, 2, 3]
    try:
        # This will raise an IndexError as the index 3 is out of range
        print(sample_list[3])
    except IndexError as e:
        logger.error(e)

# Function to demonstrate ValueError
def demonstrate_value_error():
    try:
        # This will raise a ValueError as 'a' cannot be converted to an integer
        int('a')
    except ValueError as e:
        logger.error(e)

# Function to demonstrate TypeError
def demonstrate_type_error():
    try:
        # Adding integer and string will raise TypeError
        result = 1 + 'a'
    except TypeError as e:
        logger.error(e)

# Function to demonstrate KeyError
def demonstrate_key_error():
    sample_dict = {'a': 1, 'b': 2}
    try:
        # Trying to access a non-existing key in the dictionary
        print(sample_dict['c'])
    except KeyError as e:
        logger.error(e)

# Function to demonstrate custom exception
def demonstrate_custom_exception():
    try:
        raise CustomError("This is a custom error")
    except CustomError as e:
        logger.error(e)


# Function to demonstrate NotImplementedError
def demonstrate_not_implemented_error():
    class AbstractClass:
        def method_to_implement(self):
            raise NotImplementedError("This method should be overridden in a subclass")

    class ConcreteClass(AbstractClass):
        pass

    try:
        obj = ConcreteClass()
        obj.method_to_implement()
    except NotImplementedError as e:
        logger.error(e)

# Function to demonstrate NameError
def demonstrate_name_error():
    try:
        # This will raise NameError because variable 'undefined_var' is not defined
        print(undefined_var)
    except NameError as e:
        logger.error(e)

# Function to demonstrate StopIteration
def demonstrate_stop_iteration():
    try:
        it = iter([1, 2, 3])
        next(it)  # 1
        next(it)  # 2
        next(it)  # 3
        next(it)  # Raises StopIteration
    except StopIteration as e:
        logger.error(e)

# Function to demonstrate UnicodeError
def demonstrate_unicode_error():
    try:
        # This will raise UnicodeError because of incorrect decoding
        b'\x80'.decode("utf-8")
    except UnicodeError as e:
        logger.error(e)

# Function to demonstrate FileNotFoundError
def demonstrate_file_not_found_error():
    try:
        # Trying to open a non-existing file
        with open('non_existing_file.txt', 'r') as f:
            pass
    except FileNotFoundError as e:
        logger.error(e)

# Function to demonstrate NotADirectoryError
def demonstrate_not_a_directory_error():
    try:
        # This assumes that 'example.txt' exists and is a file, not a directory
        os.listdir('/nope/')
    except NotADirectoryError as e:
        # does not raise here on Windows (!)
        logger.error(e)
    except FileNotFoundError as e:
        logger.error(e)

# Main function to execute the demonstrations
def main():
    demonstrate_not_implemented_error()
    demonstrate_name_error()
    demonstrate_stop_iteration()
    demonstrate_unicode_error()
    demonstrate_file_not_found_error()
    demonstrate_not_a_directory_error()
    demonstrate_index_error()
    demonstrate_value_error()
    demonstrate_type_error()
    demonstrate_key_error()
    demonstrate_custom_exception()

if __name__ == "__main__":
    main()

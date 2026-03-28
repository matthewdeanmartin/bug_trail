"""
Reports all that ad hoc, folksonomy metadata that is used in Python packages and scripts.

There is no standard but could be useful for diagnostics.
"""

from __future__ import annotations

import inspect
import os
import re
import sys


def get_module(exception):
    """Get the module of the exception."""
    exception_class = exception.__class__
    module_name = exception_class.__module__
    module = sys.modules[module_name]
    return module


def get_module_file(module):
    """Get the file associated with a module."""
    return inspect.getfile(module)


def is_package(module):
    """Check if a module is a package."""
    module_file = get_module_file(module)
    return os.path.basename(module_file) == "__init__.py"


def get_init(module, source_file: str):
    """Get the __init__.py file of the module's package."""
    module_file = inspect.getfile(module)
    module_dir = os.path.dirname(module_file)

    # Check if the module itself is a package (__init__.py)

    if os.path.basename(module_file) == source_file:
        return module_file

    # Check for __init__.py in the module's directory
    init_file = os.path.join(module_dir, source_file)
    if os.path.isfile(init_file):
        return init_file
    return None


def get_meta(init_file):
    """Extract metadata from the __init__.py file or a module file."""
    metadata = {}

    if init_file and os.path.isfile(init_file):
        with open(init_file) as file:
            content = file.read()

        # Define a regex pattern to match metadata variables
        pattern = r"__(\w+)__\s*=\s*['\"]([^'\"]+)['\"]"
        matches = re.findall(pattern, content)

        for key, value in matches:
            metadata[key] = value
    return metadata


if __name__ == "__main__":

    class CustomError(Exception):
        """Custom exception for demonstration purposes."""

    def run():
        """Main function to demonstrate metadata extraction."""
        try:
            # ... some code that raises CustomError ...
            raise CustomError("An error occurred")
        except CustomError as ce:
            module = get_module(ce)
            # is_pkg = is_package(module) # returns false even though it is in a package!
            # if not is_pkg:
            # Gets file where declared.
            file = get_module_file(module)
            for candidate in ["__init__.py", "__about__.py", "about.py", "__meta__.py", file]:
                init_file = get_init(module, candidate)
                metadata = get_meta(init_file)
                if metadata:
                    break
            print(metadata)

    run()

"""
Highlight all python files in a directory and its subdirectories and save them as HTML files

pygmentize -g -O full,style=monokai,linenos=1 **/*.py
"""

import glob
import logging
import os

from pygments import highlight
from pygments.formatters import HtmlFormatter  # pylint: disable=no-name-in-module
from pygments.lexers import PythonLexer  # pylint: disable=no-name-in-module

logger = logging.getLogger(__name__)


def highlight_python_files(root_directory: str, output_directory: str, ctags_file: str) -> int:
    """
    Highlight all python files in a directory and its subdirectories and save them as HTML files
    Args:
        root_directory (str): The root directory to search for python files
        output_directory (str): The directory to save the HTML files
    Returns:
        int: The number of files highlighted
    """
    if not output_directory:
        logger.warning("No output directory provided, skipping highlighting.")
        return 0
    if not root_directory:
        logger.warning("No root directory provided, skipping highlighting.")
        return 0
    output_directory += "/src/"
    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Define the formatter with the desired options
    args = {
        "full": True,
        "style": "staroffice",  # Bad contrast! "monokai",
        "linenos": True,
        "lineanchors": "line",
        "anchorlinenos": True,
    }
    if ctags_file:
        args["tagsfile"] = ctags_file
        #  url = self.tagurlformat % {'path': base, 'fname': filename,
        #                                                'fext': extension}
        args["tagurlformat"] = "%(path)s%(fname)s%(fext)s"

    logger.info("Highlighting python files in %s", root_directory)
    for key, value in args.items():
        logger.debug("%s: %s", key, value)
    formatter = HtmlFormatter(**args)

    # Search for all .py files in the given directory and its subdirectories
    count = 0
    search_string = os.path.join(root_directory, "**", "*.py")
    for file_path in glob.glob(search_string, recursive=True):
        count += 1
        with open(file_path, encoding="utf-8") as file:
            code = file.read()
            # Highlight the code
            highlighted_code = highlight(code, PythonLexer(), formatter)

            # Define the output file path
            relative_path = os.path.relpath(file_path, root_directory)
            output_file_path = os.path.join(output_directory, relative_path + ".html")

            # Ensure the subdirectories in the output path exist
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

            logger.debug("Saving highlighted code to %s", output_file_path)
            # Save the highlighted code to the output file
            with open(output_file_path, "w", encoding="utf-8") as output_file:
                output_file.write(highlighted_code)
    if count == 0:
        print(f"No source files found, searched at {search_string}")
    return count

"""
Look up info on exceptions.
"""


def docstring_for(ex):
    """
    Retrieve the docstring of the exception class.

    Parameters:
    ex (Exception): The exception instance.

    Returns:
    str: The docstring of the exception class.
    """
    # Get the class of the exception
    ex_class = ex.__class__

    # Get the docstring of the class
    return ex_class.__doc__


def documentation_link_for(ex):
    """
    Generate a link to the Python standard library documentation for the given exception.

    Parameters:
    ex (Exception): The exception instance.

    Returns:
    str: A URL to the documentation of the exception.
    """
    base_url = "https://docs.python.org/3/library/"
    ex_class = ex.__class__
    module = ex_class.__module__

    if module == "builtins":
        return f"{base_url}exceptions.html#{ex_class.__name__}"

    # Replace underscores with hyphens in the module name for the URL
    module_url = module.replace("_", "-")
    return f"{base_url}{module_url}.html#{module}.{ex_class.__name__}"


if __name__ == "__main__":
    try:
        _ = 1 / 0
    except ZeroDivisionError as e:
        print(docstring_for(e))
        print(documentation_link_for(e))

# Programmer Usage

Bug Trail is designed for seamless integration with the standard Python `logging` module.

## Integration Basics

Integrate Bug Trail into your application with a few lines of code:

```python
import logging
import bug_trail_core

# Initialize the BugTrailHandler with the path to your SQLite database
handler = bug_trail_core.BugTrailHandler("error_log.db")

# Add the handler to your root logger
logging.basicConfig(handlers=[handler], level=logging.ERROR)

# Now, any error logged will be captured by Bug Trail
logger = logging.getLogger(__name__)
logger.error("Something went wrong!")
```

## Configuring Minimum Log Level

By default, the handler only captures `ERROR` level logs and above. You can customize this during initialization:

```python
# Capture WARNING level and above
handler = bug_trail_core.BugTrailHandler("error_log.db", minimum_level=logging.WARNING)
```

## Capturing Uncaught Exceptions

To ensure even the most unexpected crashes are logged, use Bug Trail with `sys.excepthook`:

```python
import sys
import logging
import bug_trail_core

# Set up the handler
handler = bug_trail_core.BugTrailHandler("error_log.db")
logging.basicConfig(handlers=[handler], level=logging.ERROR)
logger = logging.getLogger(__name__)

# Define the exception hook
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

# Register the hook
sys.excepthook = handle_exception
```

## Logging Additional Metadata (LLM Context)

The latest version of Bug Trail supports capturing unstructured metadata in a `user_data` JSON column. This is perfect for capturing the state of an LLM prompt or its output during an error:

```python
prompt = "What is the capital of France?"
try:
    # LLM call that might fail
    raise ConnectionError("LLM API timed out")
except Exception as e:
    # Use 'extra' to pass additional context
    logger.error("LLM call failed", exc_info=True, extra={"prompt": prompt, "model": "gpt-4"})
```

These "extra" fields will be captured and displayed in the "Additional Data" section of the error dashboard.

## Thread Safety

Bug Trail is thread-safe and can be used in multithreaded applications (e.g., within a ThreadPoolExecutor). It uses internal locking to ensure the SQLite database remains consistent.

For multithreaded applications, it is recommended to keep `single_threaded=True` (the default) to maintain high performance in highly concurrent environments.

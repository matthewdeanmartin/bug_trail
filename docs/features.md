# Dashboard Features

The Bug Trail dashboard provides a comprehensive view of captured errors.

## Main View (Dashboard)

The **Main View** lists all captured errors with their level (e.g., `ERROR`, `WARNING`), message, and source location (filename and line number). Errors are paginated for easy navigation.

- **Fast & Responsive**: The static files are highly optimized for fast loading.
- **Color Coding**: Visual cues for different log levels to quickly identify critical issues.

## Detail View

Selecting an error takes you to the **Detail View**, providing deep insights into the issue:

- **Full Traceback**: View the entire call stack to pinpoint where the error occurred.
- **Local Variable Inspection**: View the values of local variables (`f_locals`) at each frame of the traceback.
- **Source Link**: Quickly jump to the relevant line of code (if a source folder is specified).
- **System Information**: View operating system, CPU, memory, and disk space details at the time of the error.
- **Python Environment**: A complete list of installed libraries in the virtual environment.

## LLM Integration (Additional Data)

For LLM-driven applications, Bug Trail captures "extra" logging context, allowing you to view prompts and completions directly in the "Additional Data" section of the Detail View.

## Continuous Monitoring (`--watch` mode)

To use Bug Trail as a live development companion, use the `--watch` flag:

```bash
bug_trail --db my_errors.db --output ./error_report --watch
```

This will automatically update the dashboard whenever a new error is logged to the SQLite database.

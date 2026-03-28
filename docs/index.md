# Bug Trail

**Bug Trail** is a lightweight, local error logging and reporting tool for Python applications, inspired by ELMAH (Error Logging Modules and Handlers). 

It captures exceptions and log messages in a SQLite database during development and provides a static HTML dashboard to explore them, making it ideal for "in the dark" applications like background workers, LLM-driven agents, and multithreaded scripts.

## Key Features

- **Zero-Configuration UI**: Generate a full-featured error dashboard with a single command.
- **Rich Context**: Captures tracebacks, local variables (`f_locals`), system information, and virtual environment details.
- **LLM Ready**: Specifically designed to capture the "hidden" errors in LLM chains and autonomous agents.
- **Local First**: Keeps your error data on your machine. No cloud subscription required.
- **Static & Fast**: The viewer is a collection of static HTML files, making it easy to host or share.

## Quick Start

1. **Install**:
   ```bash
   pip install bug-trail
   ```

2. **Integrate**:
   ```python
   import logging
   import bug_trail_core
   
   handler = bug_trail_core.BugTrailHandler("errors.db")
   logging.basicConfig(handlers=[handler], level=logging.ERROR)
   ```

3. **View**:
   ```bash
   bug_trail --db errors.db --output ./error_report
   ```

   Then open `./error_report/index.html` in your browser.

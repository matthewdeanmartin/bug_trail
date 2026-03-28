# Installation

Bug Trail is split into two packages:
1.  **`bug-trail-core`**: The logging handler and data storage logic (lightweight).
2.  **`bug-trail`**: The static HTML generator and CLI tool (includes `bug-trail-core`).

## Installation Methods

### For the Full Experience (Recommended)

To use the logging handler and the static report generator, install `bug-trail`:

```bash
pip install bug-trail
```

### For Logging Only

If you only need the logging handler (e.g., in a production environment where you'll collect the SQLite DB and view it elsewhere), install `bug-trail-core`:

```bash
pip install bug-trail-core
```

## Python Version Support

Bug Trail requires **Python 3.12** or higher, leveraging modern features for better performance and type safety.

## Using with `uv` (Recommended)

If you're using the `uv` package manager:

```bash
uv add bug-trail
```

To run the CLI tool without installing it globally:

```bash
uv run bug_trail --db my_errors.db
```

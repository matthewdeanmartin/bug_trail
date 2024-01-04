# Bug Trail

This is a workstation logger to capture bugs encountered while you are writing code.

In other words, it is an HTML report writer for your logs, even if they aren't errors if that is your thing.

## Installation

```bash
pip install bug-trail
```

## Usage

Configuration is optional via a `pyproject.toml` file and the logging modules ordinary configuration options. See 
[example code-as-config](example_code_as_config.py)

This is the schema with the default values.
```toml
[tool.bug-trail]
app_name = "bug_trail"
app_author = "bug_trail"
report_folder = "logs"
database_path = "bug_trail.db"
```


```python
import bug_trail
import logging

section = bug_trail.read_config(config_path="../pyproject.toml")
handler = bug_trail.BugTrailHandler(section.database_path, minimum_level=logging.ERROR)
logging.basicConfig(handlers=[handler], level=logging.ERROR)

logger = logging.getLogger(__name__)
logger.error("This is an error message")
```

To generate to the log folder relative to the current working directory:

```bash
bug_trail --output logs --db error_log.db
```

## Picologging
If you want to use picologging, install it. Everything is the same except you use the `PicoBugTrailHandler`.

```python
import bug_trail
import logging

section = bug_trail.read_config(config_path="../pyproject.toml")
handler = bug_trail.PicoBugTrailHandler(
    section.database_path, minimum_level=logging.ERROR
)
logging.basicConfig(handlers=[handler], level=logging.ERROR)

logger = logging.getLogger(__name__)
logger.error("This is an error message")
```

## Do more with your data

```bash
pipx install datasette
datasette bug_trail.db
```

## Security
None. Do not publish your error log to the internet or to public Github. Add the log folder to your .gitignore file.

## Advanced
Get ctags from [here](https://github.com/universal-ctags/ctags)
```bash
./ctags -R -f fish_tank.tags fish_tank
```

## Prior Art
Inspired by elmah. `bug_trail` is much less ambitious, as this is just a browsable, static HTML report.

If you want logger for a website, hosted in your Flak or Django website:
- [Flask-ErrorsHandler](https://pypi.org/project/Flask-ErrorsHandler/)
- [django-elmah](https://pypi.org/project/django-elmah/)

These are the closest "write logs to HTML" projects I could find:
- [PyLog2html](https://pypi.org/project/PyLog2html/)
- Gist - https://gist.github.com/ColinDuquesnoy/8296508

If you want someone else to do it all for you
- [Sentry](https://sentry.io/)

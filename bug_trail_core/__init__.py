"""
Captures error logs to sqlite. Compansion CLI tool generates a static website.

Install bug_trail_core to your application. Pipx install bug_trail to avoid depencency
conflicts
"""
from bug_trail_core.config import BugTrailConfig, read_config
from bug_trail_core.handlers import BugTrailHandler, PicoBugTrailHandler

__all__ = ["BugTrailHandler", "PicoBugTrailHandler", "read_config", "BugTrailConfig"]

"""
Captures error logs to sqlite. CLI tool generates a static website.
"""
from bug_trail.config import BugTrailConfig, read_config
from bug_trail.handlers import BugTrailHandler, PicoBugTrailHandler

__all__ = ["BugTrailHandler", "PicoBugTrailHandler", "read_config", "BugTrailConfig"]

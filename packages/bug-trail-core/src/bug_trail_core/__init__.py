"""
Captures error logs to sqlite. Companion CLI tool generates a static website.

Install bug_trail_core to your application. Pipx install bug_trail to avoid dependency
conflicts
"""

from bug_trail_core.__about__ import __version__
from bug_trail_core.config import BugTrailConfig, read_config
from bug_trail_core.handlers import BugTrailHandler

__all__ = ["BugTrailHandler", "read_config", "BugTrailConfig", "__version__"]

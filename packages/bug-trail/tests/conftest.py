import logging
import os

import bug_trail_core

current_directory = os.path.dirname(__file__)
config_path = current_directory + "/../pyproject.toml"
section = bug_trail_core.read_config(config_path=config_path)
handler = bug_trail_core.BugTrailHandler(section.database_path, minimum_level=logging.WARNING)

logging.basicConfig(handlers=[handler], level=logging.ERROR)

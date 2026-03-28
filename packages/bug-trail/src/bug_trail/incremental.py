"""Incremental file watcher for database changes using watchdog."""

from __future__ import annotations

import time
from collections.abc import Callable

from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer


class DbChangedHandler(FileSystemEventHandler):
    """Event handler that triggers a target function when a .db file is modified."""

    def __init__(self, target):
        """
        Initialize the event handler with a target function to call when a .db file is modified.
        """
        self.target = target
        super().__init__()

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent):
        """
        Handle file modified events.

        Args:
            event (FileModifiedEvent): The event that triggered the handler.
        """
        if isinstance(event, FileModifiedEvent):
            if str(event.src_path).endswith(".db"):
                print(event)
                self.target()


def watch_for_changes(path: str, target: Callable[[], None]) -> None:
    """
    Watch for changes in a directory and trigger a target function when a .db file is modified.

    Args:
        path (str): The directory to watch for changes.
        target (Callable[[], None]): The function to call when a change is detected.
    """
    event_handler = DbChangedHandler(target)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

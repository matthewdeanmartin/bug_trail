"""Watchdog-backed DB change detector that notifies async SSE listeners."""

from __future__ import annotations

import asyncio
import logging
import threading
from typing import Any

from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


class _Handler(FileSystemEventHandler):
    def __init__(self, owner: DbWatcher, filename: str) -> None:
        super().__init__()
        self._owner = owner
        self._filename = filename

    def on_modified(self, event: Any) -> None:
        if not isinstance(event, FileModifiedEvent):
            return
        src = str(event.src_path)
        if src.endswith(self._filename) or src.endswith(".db") or src.endswith(".db-wal"):
            self._owner.notify()


class DbWatcher:
    """Watches a directory and broadcasts to async queues on change."""

    def __init__(self, watch_dir: str, filename: str) -> None:
        self.watch_dir = watch_dir
        self.filename = filename
        self._observer: Observer | None = None
        self._listeners: set[asyncio.Queue[str]] = set()
        self._listeners_lock = threading.Lock()
        self._loop: asyncio.AbstractEventLoop | None = None

    def start(self) -> None:
        self._loop = asyncio.get_event_loop()
        handler = _Handler(self, self.filename)
        obs = Observer()
        obs.schedule(handler, self.watch_dir, recursive=False)
        obs.start()
        self._observer = obs

    def stop(self) -> None:
        if self._observer is not None:
            self._observer.stop()
            self._observer.join(timeout=2.0)
            self._observer = None

    def subscribe(self) -> asyncio.Queue[str]:
        queue: asyncio.Queue[str] = asyncio.Queue()
        with self._listeners_lock:
            self._listeners.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[str]) -> None:
        with self._listeners_lock:
            self._listeners.discard(queue)

    def notify(self) -> None:
        """Called from a watchdog background thread."""
        if self._loop is None:
            return
        with self._listeners_lock:
            listeners = list(self._listeners)
        for queue in listeners:
            try:
                self._loop.call_soon_threadsafe(queue.put_nowait, "refresh")
            except RuntimeError:
                pass

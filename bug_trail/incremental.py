import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler, FileModifiedEvent


class DbChangedHandler(FileSystemEventHandler):
    def __init__(self, target):
        self.target = target
        super().__init__()
    def on_modified(self, event):
        if isinstance(event, FileModifiedEvent):
            if event.src_path.endswith(".db"):
                print(event)
                self.target()



def watch_for_changes(path: str, target):
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

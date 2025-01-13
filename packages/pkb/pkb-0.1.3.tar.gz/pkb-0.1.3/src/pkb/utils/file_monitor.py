import time
from pkb.utils.logging import getLogging
logging = getLogging()
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

class AllEventHandler(FileSystemEventHandler):
    def on_any_event(self, event: FileSystemEvent) -> None:
        # monitor dir and file (FileCreated, FileModified, FileMoved)
        print(event)

def get_observer(path):
    event_handler = AllEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    return observer

    # import time
    # from pkb.utils.monitor import get_observer
    # observer = get_observer('content')
    # observer.start()
    # try:
    #     while True:
    #         time.sleep(1)
    # finally:
    #     observer.stop()
    #     observer.join()
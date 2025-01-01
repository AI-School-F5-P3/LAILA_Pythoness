import os
import sass
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SCSSWatcher(FileSystemEventHandler):
    def __init__(self, scss_dir, css_dir):
        self.scss_dir = scss_dir
        self.css_dir = css_dir

    def on_modified(self, event):
        if event.src_path.endswith('.scss'):
            print(f"Detected change in {event.src_path}. Recompiling SCSS...")
            self.compile_scss()

    def compile_scss(self):
        try:
            sass.compile(dirname=(self.scss_dir, self.css_dir), output_style='compressed')
            print("SCSS compiled successfully!")
        except Exception as e:
            print(f"Error compiling SCSS: {e}")

def watch_scss(scss_dir, css_dir):
    event_handler = SCSSWatcher(scss_dir, css_dir)
    observer = Observer()
    observer.schedule(event_handler, path=scss_dir, recursive=True)
    observer.start()
    print(f"Watching {scss_dir} for changes...")
    try:
        while True:
            pass  # Keep the script running
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    scss_directory = "frontend/static/scss" 
    css_directory = "frontend/static/css" 
    watch_scss(scss_directory, css_directory)

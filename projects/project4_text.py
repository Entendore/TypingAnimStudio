"""Project 4: Text Typing Studio."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typingstudio.export import TextTypingWindow, launch_studio_app

class Project4Window(TextTypingWindow):
    SETTINGS_KEY = "project4_text"
    def __init__(self):
        super().__init__("Project 4: Text Typing Studio", self.SETTINGS_KEY)

if __name__ == "__main__":
    sys.exit(launch_studio_app("project4_text", Project4Window))

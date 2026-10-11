"""Project 5: Emoji & ASCII Art Studio."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typingstudio.export import TextTypingWindow, launch_studio_app

class Project5Window(TextTypingWindow):
    SETTINGS_KEY = "project5_emoji_ascii"
    def __init__(self):
        super().__init__("Project 5: Emoji & ASCII Art Studio", self.SETTINGS_KEY)

if __name__ == "__main__":
    sys.exit(launch_studio_app("project5_emoji_ascii", Project5Window))

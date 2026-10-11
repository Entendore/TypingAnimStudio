"""Project 2: Multi Window Studio."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typingstudio.export import BaseCodeExportWindow, launch_studio_app

class Project2Window(BaseCodeExportWindow):
    SETTINGS_KEY = "project2_multi_window"
    def __init__(self):
        super().__init__("Project 2: MultiWindow Studio", self.SETTINGS_KEY)

if __name__ == "__main__":
    sys.exit(launch_studio_app("project2_multi_window", Project2Window))

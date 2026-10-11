"""Project 1: Junior vs Senior Dev Studio."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typingstudio.export import BaseCodeExportWindow, launch_studio_app

class Project1Window(BaseCodeExportWindow):
    SETTINGS_KEY = "project1_jr_vs_sr"
    def __init__(self):
        super().__init__("Project 1: Jr vs Sr Dev Studio", self.SETTINGS_KEY)

if __name__ == "__main__":
    sys.exit(launch_studio_app("project1_jr_vs_sr", Project1Window))

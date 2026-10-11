"""Project 3: Code Typing Studio."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typingstudio.export import BaseCodeExportWindow, launch_studio_app

class Project3Window(BaseCodeExportWindow):
    SETTINGS_KEY = "project3_codetyping"
    def __init__(self):
        super().__init__("Project 3: Code Typing Studio", self.SETTINGS_KEY)

if __name__ == "__main__":
    sys.exit(launch_studio_app("project3_codetyping", Project3Window))

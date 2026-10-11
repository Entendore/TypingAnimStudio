"""TypingAnimStudio: Single Entry Point."""
import sys
from pathlib import Path

# Ensure the typingstudio package is discoverable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from typingstudio.export import launch_studio_app

if __name__ == "__main__":
    sys.exit(launch_studio_app())

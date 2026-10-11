"""State Machines, Orchestrators, and dynamic UI modes."""
from __future__ import annotations
from enum import Enum, auto
from typing import Optional, List, Dict
from dataclasses import dataclass
import sys, os
from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                                QPushButton, QLabel, QComboBox, QSpinBox, QFileDialog, 
                                QListWidget, QAbstractItemView)
from .core import (SettingsRepository, AppSettingsSchema, ThemeRegistry, THEMES, 
                   get_process_factory, log, setup_project_logging, CWD, INPUT_DIR, OUTPUT_DIR)
from .rendering import PreviewWidget
from .audio import SimpleSoundGen

class ExportState(Enum):
    IDLE = auto(); RENDERING = auto(); COMPLETED = auto(); FAILED = auto()

@dataclass(frozen=True, slots=True)
class ProjectMode:
    name: str
    settings_key: str
    supported_exts: frozenset
    output_suffix: str

# The 5 distinct project modes accessible via the dropdown
PROJECT_MODES: Dict[str, ProjectMode] = {
    "1: Jr vs Sr Dev Studio": ProjectMode("Jr vs Sr Dev Studio", "project1_jr_vs_sr", frozenset({".json"}), "_jr_vs_sr.mp4"),
    "2: MultiWindow Studio": ProjectMode("MultiWindow Studio", "project2_multi_window", frozenset({".py", ".js", ".cpp"}), "_multiwindow.mp4"),
    "3: YouTube Optimised Studio": ProjectMode("YouTube Optimised Studio", "project3_codetyping", frozenset({".py", ".js", ".cpp"}), "_youtube.mp4"),
    "4: Text Typing Studio": ProjectMode("Text Typing Studio", "project4_text", frozenset({".txt", ".csv", ".md"}), "_text.mp4"),
    "5: Emoji & ASCII Art Studio": ProjectMode("Emoji & ASCII Art Studio", "project5_emoji_ascii", frozenset({".emoji", ".emo", ".asc", ".ascii", ".art"}), "_emoji.mp4"),
}

class ExportOrchestrator(QObject):
    task_started = Signal(int, int)
    task_completed = Signal(int, str)
    task_failed = Signal(int, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._state = ExportState.IDLE
        
    def execute(self, mode: ProjectMode):
        log.info("Exporting project: %s", mode.name)
        self.task_started.emit(1, 1)
        self.task_completed.emit(0, str(OUTPUT_DIR / f"output{mode.output_suffix}"))

class BaseCodeExportWidget(QWidget):
    def __init__(self, mode_name: str, parent=None):
        super().__init__(parent)
        self.mode = PROJECT_MODES[mode_name]
        self.settings_repo = SettingsRepository(CWD / "settings.json")
        self._settings = self.settings_repo.get(self.mode.settings_key)
        self.orchestrator = ExportOrchestrator(self)
        
        self._build_ui()
        self._apply_settings(self._settings)
        self._scan_input_dir()
        
    def _build_ui(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        
        # Header / Settings
        h = QHBoxLayout()
        self.theme_cb = QComboBox(); self.theme_cb.addItems(ThemeRegistry.names())
        self.wpm_sp = QSpinBox(); self.wpm_sp.setRange(10, 500)
        self.export_btn = QPushButton("🎬 Export"); self.export_btn.clicked.connect(self._start_export)
        h.addWidget(QLabel("Theme:")); h.addWidget(self.theme_cb)
        h.addWidget(QLabel("WPM:")); h.addWidget(self.wpm_sp)
        h.addStretch(); h.addWidget(self.export_btn)
        v.addLayout(h)
        
        # File List
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.SingleSelection)
        v.addWidget(self.file_list, 1)
        
        # Preview
        self.preview = PreviewWidget()
        v.addWidget(self.preview, 2)
        
    def _apply_settings(self, s: AppSettingsSchema):
        self.theme_cb.setCurrentText(s.theme)
        self.wpm_sp.setValue(s.wpm)
        
    def _scan_input_dir(self):
        self.file_list.clear()
        if not INPUT_DIR.is_dir(): return
        for f in sorted(os.listdir(INPUT_DIR)):
            if os.path.splitext(f)[1].lower() in self.mode.supported_exts:
                self.file_list.addItem(f)
                
    def _start_export(self):
        self.orchestrator.execute(self.mode)
        
    def cleanup(self):
        self.settings_repo.save(self.mode.settings_key, AppSettingsSchema(
            theme=self.theme_cb.currentText(),
            wpm=self.wpm_sp.value()
        ))

def launch_studio_app() -> int:
    # Setup initial logging for the default app mode
    setup_project_logging("studio_launcher")
    log.info("Starting TypingAnimStudio Launcher...")
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    from PySide6.QtWidgets import QMainWindow
    main_win = QMainWindow()
    main_win.setWindowTitle("TypingAnimStudio")
    main_win.resize(1200, 800)
    
    central = QWidget()
    main_win.setCentralWidget(central)
    layout = QVBoxLayout(central)
    
    # Dropdown Menu for switching modes
    mode_layout = QHBoxLayout()
    mode_layout.addWidget(QLabel("Select Project Mode:"))
    mode_selector = QComboBox()
    mode_selector.addItems(list(PROJECT_MODES.keys()))
    mode_layout.addWidget(mode_selector, 1)
    layout.addLayout(mode_layout)
    
    # Container for the active mode
    studio_widget = BaseCodeExportWidget(mode_selector.currentText())
    layout.addWidget(studio_widget, 1)
    
    def on_mode_change(new_mode: str):
        nonlocal studio_widget
        # Cleanup and save old mode state
        studio_widget.cleanup()
        studio_widget.deleteLater()
        
        # Re-init logging for the new mode (mode='w' overwrites the specific log file)
        new_settings_key = PROJECT_MODES[new_mode].settings_key
        setup_project_logging(new_settings_key)
        log.info("Switched to mode: %s", new_mode)
        
        # Instantiate new mode widget
        studio_widget = BaseCodeExportWidget(new_mode)
        layout.addWidget(studio_widget, 1)
        main_win.setWindowTitle(f"TypingAnimStudio - {new_mode}")

    mode_selector.currentTextChanged.connect(on_mode_change)
    
    main_win.show()
    
    def on_close(event):
        studio_widget.cleanup()
        event.accept()
        
    main_win.closeEvent = on_close
    return app.exec()

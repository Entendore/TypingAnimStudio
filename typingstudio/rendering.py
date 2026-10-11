"""Reactive State Reducers and RAII UI Rendering."""
from __future__ import annotations
from dataclasses import dataclass, replace
from contextlib import contextmanager
from typing import Optional, Tuple
from PySide6.QtCore import Qt, QTimer, QElapsedTimer, Signal, QObject, QPointF
from PySide6.QtGui import QImage, QColor, QPainter, QFont, QFontMetrics, QPen, QBrush, QLinearGradient, QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QSizePolicy

@dataclass(frozen=True, slots=True)
class PreviewState:
    progress: float = 0.0
    anim_t: float = 0.0
    animating: bool = False
    loop: bool = False
    speed: float = 1.0
    target_duration: float = 5.0

def preview_reducer(state: PreviewState, action: Tuple[str, any]) -> PreviewState:
    action_type, payload = action
    match action_type:
        case "TICK":
            if not state.animating: return state
            dt = payload
            total = state.target_duration
            new_t = state.anim_t + (dt * state.speed)
            if new_t >= total:
                if state.loop: return replace(state, anim_t=0.0, progress=0.0)
                return replace(state, anim_t=total, progress=1.0, animating=False)
            return replace(state, anim_t=new_t, progress=new_t / total if total > 0 else 0.0)
        case "SEEK":
            p = max(0.0, min(1.0, payload))
            return replace(state, progress=p, anim_t=p * state.target_duration, animating=False)
        case "PLAY_PAUSE":
            return replace(state, animating=not state.animating)
    return state

@contextmanager
def qt_painter_context(target: QImage):
    p = QPainter(target)
    try:
        p.setRenderHint(QPainter.Antialiasing)
        p.save()
        yield p
    finally:
        p.restore()
        p.end()

class CodeRenderer:
    def __init__(self, width: int, height: int, theme_name: str = "Dracula"):
        from .core import THEMES
        self.w, self.h = width, height
        self.theme = THEMES[theme_name]
        
    def render_frame(self, progress: float, target: Optional[QImage] = None) -> QImage:
        img = target if target is not None else QImage(self.w, self.h, QImage.Format_RGB32)
        if target is None: img.fill(QColor(self.theme.background))
        
        with qt_painter_context(img) as p:
            p.setPen(QColor(self.theme.foreground))
            p.setFont(QFont("Consolas", 24))
            p.drawText(img.rect(), Qt.AlignCenter, f"Progress: {progress*100:.1f}%")
        return img

class PreviewController(QObject):
    state_changed = Signal(PreviewState)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._state = PreviewState(target_duration=5.0)
        self._timer = QTimer(self)
        self._timer.setTimerType(Qt.PreciseTimer)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._on_tick)
        self._clock = QElapsedTimer()

    def dispatch(self, action: Tuple[str, any]):
        self._state = preview_reducer(self._state, action)
        if not self._state.animating: self._timer.stop()
        else: self._clock.start(); self._timer.start()
        self.state_changed.emit(self._state)

    def _on_tick(self):
        dt = min(self._clock.restart() / 1000.0, 0.1)
        self.dispatch(("TICK", dt))

class PreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = PreviewController(self)
        self._scratch = QImage(640, 360, QImage.Format_RGB32)
        self._build_ui()
        self.controller.state_changed.connect(self._on_state_changed)
        
    def _build_ui(self):
        v = QVBoxLayout(self)
        self.label = QLabel("Ready")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background: black; color: white; font-size: 24px;")
        v.addWidget(self.label, 1)
        
        h = QHBoxLayout()
        self.play_btn = QPushButton("▶"); self.play_btn.clicked.connect(lambda: self.controller.dispatch(("PLAY_PAUSE", None)))
        self.slider = QSlider(Qt.Horizontal); self.slider.setRange(0, 1000)
        self.slider.valueChanged.connect(lambda v: self.controller.dispatch(("SEEK", v / 1000.0)))
        h.addWidget(self.play_btn); h.addWidget(self.slider, 1)
        v.addLayout(h)

    def _on_state_changed(self, state: PreviewState):
        self.slider.blockSignals(True)
        self.slider.setValue(int(state.progress * 1000))
        self.slider.blockSignals(False)
        self.play_btn.setText("⏸" if state.animating else "▶")
        
        renderer = CodeRenderer(640, 360, "Dracula")
        qimg = renderer.render_frame(state.progress, self._scratch)
        self.label.setPixmap(QPixmap.fromImage(qimg))

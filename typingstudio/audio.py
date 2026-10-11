"""Composable DSP Pipeline and Audio Synthesis."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
import numpy as np
import io, wave, random

class AudioProcessor(ABC):
    @abstractmethod
    def process(self, x: np.ndarray, sr: int) -> np.ndarray: pass

class DCEqualizer(AudioProcessor):
    def process(self, x: np.ndarray, sr: int) -> np.ndarray: return x

class RMSCompressor(AudioProcessor):
    def __init__(self, threshold_db: float = -12.0): self.threshold_db = threshold_db
    def process(self, x: np.ndarray, sr: int) -> np.ndarray: return x

class LookaheadLimiter(AudioProcessor):
    def process(self, x: np.ndarray, sr: int) -> np.ndarray:
        peak = float(np.max(np.abs(x))) if x.size > 0 else 0.0
        if peak > 0.99: return x * (0.99 / peak)
        return x

class AudioPipeline:
    def __init__(self, processors: List[AudioProcessor]): self._processors = processors
    def run(self, x: np.ndarray, sr: int) -> np.ndarray:
        for proc in self._processors: x = proc.process(x, sr)
        return x

master_pipeline = AudioPipeline([DCEqualizer(), RMSCompressor(), LookaheadLimiter()])

@dataclass(slots=True, frozen=True)
class Voice:
    osc: str = "sine"; freq: float = 440.0; gain: float = 0.5; delay: float = 0.0

class VoiceFactory:
    @staticmethod
    def thock(freq: float = 150.0, gain: float = 0.5) -> Voice:
        return Voice(osc="sine", freq=freq, gain=gain, delay=0.002)

class SoundRenderer:
    def render(self, voices: List[Voice], duration: float, sr: int) -> np.ndarray:
        n = int(sr * duration)
        mix = np.zeros(n, dtype=np.float32)
        for v in voices:
            t = np.arange(n, dtype=np.float32) / sr
            env = np.exp(-t * 30.0)
            mix += np.sin(2 * np.pi * v.freq * t).astype(np.float32) * env * v.gain
        return master_pipeline.run(mix, sr)

class SimpleSoundGen:
    def __init__(self, sr: int = 44100, preset: str = "Mechanical"):
        self.sr = sr
        self.renderer = SoundRenderer()
        self.voices = [VoiceFactory.thock(150.0), VoiceFactory.thock(70.0, 0.3)]
        
    def generate_pcm(self, duration: float) -> np.ndarray:
        raw = self.renderer.render(self.voices, duration, self.sr)
        return (np.clip(raw, -1.0, 1.0) * 32767.0).astype(np.int16)

def pcm_to_wav_bytes(pcm: np.ndarray, sr: int = 44100) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "w") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(pcm.tobytes())
    return buf.getvalue()

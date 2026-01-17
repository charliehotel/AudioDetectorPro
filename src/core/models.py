"""
Data Models for Audio Detector Pro
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class AnalysisResult:
    """Result of VAD analysis"""
    
    file_path: str
    file_name: str
    total_duration: float  # in seconds
    speech_duration: float  # in seconds
    silence_duration: float  # in seconds
    sample_rate: int
    sensitivity: int
    frame_duration: int
    speech_segments: list[tuple[float, float]] = None  # List of (start, end) times in seconds
    
    @property
    def speech_percentage(self) -> float:
        """Calculate speech percentage"""
        if self.total_duration <= 0:
            return 0.0
        return (self.speech_duration / self.total_duration) * 100
    
    @property
    def silence_percentage(self) -> float:
        """Calculate silence (non-speech) percentage"""
        return 100.0 - self.speech_percentage

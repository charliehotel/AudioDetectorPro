"""
VAD Analyzer - Voice Activity Detection using webrtcvad
"""

import os
import wave
import math
from typing import Optional

import webrtcvad

from src.core.models import AnalysisResult


class VADAnalyzer:
    """Voice Activity Detection analyzer using WebRTC VAD"""
    
    SUPPORTED_SAMPLE_RATES = [8000, 16000, 32000, 48000]
    SUPPORTED_FRAME_DURATIONS = [10, 20, 30]  # ms
    
    def __init__(self, sensitivity: int = 2, frame_duration: int = 30):
        """
        Initialize VAD analyzer
        
        Args:
            sensitivity: VAD sensitivity (0-3), higher = more sensitive
            frame_duration: Frame duration in ms (10, 20, or 30)
        """
        self.sensitivity = max(0, min(3, sensitivity))
        self.frame_duration = frame_duration if frame_duration in self.SUPPORTED_FRAME_DURATIONS else 30
    
    def analyze(self, file_path: str) -> AnalysisResult:
        """
        Analyze a WAV file for voice activity
        
        Args:
            file_path: Path to WAV file
            
        Returns:
            AnalysisResult with duration statistics
            
        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file does not exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        audio = wave.open(file_path, "rb")
        
        try:
            # Validate format
            channels = audio.getnchannels()
            sample_width = audio.getsampwidth()
            sample_rate = audio.getframerate()
            n_frames = audio.getnframes()
            
            if channels != 1:
                raise ValueError(f"Only mono audio is supported (got {channels} channels)")
            
            if sample_width != 2:
                raise ValueError(f"Only 16-bit audio is supported (got {sample_width * 8} bit)")
            
            if sample_rate not in self.SUPPORTED_SAMPLE_RATES:
                raise ValueError(f"Unsupported sample rate: {sample_rate}Hz. Supported: {self.SUPPORTED_SAMPLE_RATES}")
            
            # Initialize VAD
            vad = webrtcvad.Vad(self.sensitivity)
            
            # Calculate frame size
            frame_size = int(sample_rate * self.frame_duration / 1000)
            num_frames = math.ceil(n_frames / frame_size)
            
            # Analyze frames
            speech_frames = 0
            speech_segments = []
            is_speech_active = False
            segment_start = 0.0
            frame_duration_sec = self.frame_duration / 1000.0
            
            for i in range(num_frames):
                frame = audio.readframes(frame_size)
                
                # Pad if necessary
                if len(frame) < frame_size * 2:
                    frame = frame.ljust(frame_size * 2, b'\0')
                
                try:
                    is_speech = vad.is_speech(frame, sample_rate)
                    
                    if is_speech:
                        speech_frames += 1
                        if not is_speech_active:
                            is_speech_active = True
                            segment_start = i * frame_duration_sec
                    else:
                        if is_speech_active:
                            is_speech_active = False
                            segment_end = i * frame_duration_sec
                            speech_segments.append((segment_start, segment_end))
                            
                except Exception:
                    # Treat error as silence
                    if is_speech_active:
                        is_speech_active = False
                        segment_end = i * frame_duration_sec
                        speech_segments.append((segment_start, segment_end))
            
            # Close last segment if active
            if is_speech_active:
                segment_end = num_frames * frame_duration_sec
                speech_segments.append((segment_start, segment_end))
            
            # Calculate durations
            total_duration = n_frames / sample_rate
            speech_duration = speech_frames * frame_duration_sec
            silence_duration = total_duration - speech_duration
            
            # Ensure non-negative
            silence_duration = max(0, silence_duration)
            
            return AnalysisResult(
                file_path=file_path,
                file_name=os.path.basename(file_path),
                total_duration=total_duration,
                speech_duration=speech_duration,
                silence_duration=silence_duration,
                sample_rate=sample_rate,
                sensitivity=self.sensitivity,
                frame_duration=self.frame_duration,
                speech_segments=speech_segments
            )
            
        finally:
            audio.close()

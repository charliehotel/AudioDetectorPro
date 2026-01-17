"""
Analysis Worker Thread - Performs audio conversion and VAD analysis in background
"""

import os
from PyQt6.QtCore import QThread, pyqtSignal

from src.core.models import AnalysisResult
from src.core.vad_analyzer import VADAnalyzer
from src.core.audio_loader import AudioLoader
from src.core.ffmpeg_manager import FFmpegManager


class AnalysisWorker(QThread):
    """Background thread for audio analysis"""
    
    status_changed = pyqtSignal(str)  # Status message update
    progress_changed = pyqtSignal(float) # Progress percentage update
    finished = pyqtSignal(object)     # AnalysisResult
    error = pyqtSignal(str)           # Error message
    
    def __init__(self, file_path: str, analyzer: VADAnalyzer, ffmpeg_manager: FFmpegManager):
        super().__init__()
        self.file_path = file_path
        self.analyzer = analyzer
        self.ffmpeg_manager = ffmpeg_manager
        self.audio_loader = AudioLoader(self.ffmpeg_manager)
        self._is_running = True
        
    def run(self):
        wav_path = None
        try:
            # 1. Update status
            original_file_name = os.path.basename(self.file_path)
            
            # Check conversion
            if self.audio_loader.needs_conversion(self.file_path):
                self.status_changed.emit(f"Converting {original_file_name}...")
                
                # Conversion with progress callback
                def on_progress(p):
                    if self._is_running:
                        self.progress_changed.emit(p)
                        
                wav_path = self.audio_loader.load_as_wav(self.file_path, progress_callback=on_progress)
            else:
                wav_path = self.audio_loader.load_as_wav(self.file_path)
                
            if not self._is_running: return

            # 2. Analyze
            self.status_changed.emit("Analyzing audio...")
            result = self.analyzer.analyze(wav_path)
            
            # Override filename
            result.file_name = original_file_name
            
            if not self._is_running: return
            
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))
            
        finally:
            # Cleanup temp file
            if wav_path:
                self.audio_loader.cleanup_temp_file(wav_path, self.file_path)

    def stop(self):
        self._is_running = False

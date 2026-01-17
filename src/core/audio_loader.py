"""
Audio Loader - Load and convert audio files using pydub
"""

import os
import tempfile
from typing import Optional

from src.core.ffmpeg_manager import FFmpegManager


class AudioLoader:
    """Load and convert audio files to WAV format for VAD analysis"""
    
    SUPPORTED_FORMATS = ['wav', 'mp3', 'flac', 'ogg', 'm4a', 'aac', 'wma']
    
    def __init__(self, ffmpeg_manager: Optional[FFmpegManager] = None):
        self.ffmpeg_manager = ffmpeg_manager or FFmpegManager()
        self._pydub_configured = False
    
    def _get_audio_segment(self):
        """Get AudioSegment class with lazy import and configuration"""
        from pydub import AudioSegment
        
        if not self._pydub_configured:
            # Configure pydub with correct ffmpeg/ffprobe paths
            ffmpeg_path = self.ffmpeg_manager.find_ffmpeg()
            if ffmpeg_path:
                AudioSegment.converter = ffmpeg_path
            
            ffprobe_path = self.ffmpeg_manager.find_ffprobe()
            if ffprobe_path:
                AudioSegment.ffprobe = ffprobe_path
            
            self._pydub_configured = True
        
        return AudioSegment
    
    def is_supported(self, file_path: str) -> bool:
        """Check if the file format is supported"""
        ext = self._get_extension(file_path)
        return ext in self.SUPPORTED_FORMATS
    
    def needs_conversion(self, file_path: str) -> bool:
        """Check if the file needs to be converted to WAV"""
        ext = self._get_extension(file_path)
        return ext != 'wav'
    
    def load_as_wav(self, file_path: str, progress_callback=None) -> str:
        """
        Load audio file and convert to WAV if necessary.
        
        Args:
            file_path: Path to the audio file
            progress_callback: Optional callable(float) for progress percentage (0-100)
            
        Returns:
            Path to WAV file (original if already WAV, or temp file if converted)
        """
        ext = self._get_extension(file_path)
        
        if ext == 'wav':
            # Check if it's already in the correct format (16-bit, mono)
            return self._ensure_wav_format(file_path)
        
        # Convert to WAV with progress
        return self._convert_to_wav(file_path, progress_callback)
    
    def _get_extension(self, file_path: str) -> str:
        """Get file extension in lowercase"""
        return file_path.lower().split('.')[-1]
    
    def get_duration(self, file_path: str) -> float:
        """Get audio duration in seconds using ffprobe"""
        import subprocess
        
        ffprobe_path = self.ffmpeg_manager.find_ffprobe()
        if not ffprobe_path:
            return 0.0
            
        try:
            cmd = [
                ffprobe_path,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ]
            
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            return float(output.decode().strip())
        except Exception:
            return 0.0

    def _convert_to_wav(self, file_path: str, progress_callback=None) -> str:
        """Convert audio file to WAV format (16-bit mono) using ffmpeg subprocess"""
        import subprocess
        import re
        
        ffmpeg_path = self.ffmpeg_manager.find_ffmpeg()
        if not ffmpeg_path:
            raise RuntimeError("FFmpeg not found")
        
        # Get total duration for progress calculation
        total_duration = self.get_duration(file_path)
        
        # Output temp path
        temp_path = tempfile.mktemp(suffix='.wav')
        
        # FFmpeg command: convert to 16-bit mono WAV, 16kHz
        cmd = [
            ffmpeg_path,
            "-y",               # Overwrite output
            "-i", file_path,    # Input file
            "-ac", "1",         # Mono 
            "-ar", "16000",     # 16kHz
            "-acodec", "pcm_s16le", # 16-bit PCM
            temp_path           # Output file
        ]
        
        # Run ffmpeg and parse progress
        process = subprocess.Popen(
            cmd,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            encoding='utf-8' # Ensure encoding is specified
        )
        
        # Regex to extract time from log (e.g. time=00:00:10.50)
        time_pattern = re.compile(r"time=(\d{2}):(\d{2}):(\d{2}\.\d+)")
        
        while True:
            line = process.stderr.readline()
            if not line and process.poll() is not None:
                break
            
            if line:
                # Parse time
                match = time_pattern.search(line)
                if match and total_duration > 0 and progress_callback:
                    h, m, s = map(float, match.groups())
                    current_seconds = h * 3600 + m * 60 + s
                    percent = min(100, (current_seconds / total_duration) * 100)
                    progress_callback(percent)
        
        if process.returncode != 0:
            raise RuntimeError("FFmpeg conversion failed")
            
        return temp_path
    
    def _ensure_wav_format(self, file_path: str) -> str:
        """Ensure WAV file is in correct format (16-bit mono)"""
        AudioSegment = self._get_audio_segment()
        audio = AudioSegment.from_wav(file_path)
        
        # Check if conversion is needed
        needs_conversion = False
        
        if audio.channels != 1:
            audio = audio.set_channels(1)
            needs_conversion = True
        
        if audio.sample_width != 2:
            audio = audio.set_sample_width(2)
            needs_conversion = True
        
        if audio.frame_rate not in [8000, 16000, 32000, 48000]:
            audio = audio.set_frame_rate(16000)
            needs_conversion = True
        
        if needs_conversion:
            temp_path = tempfile.mktemp(suffix='.wav')
            audio.export(temp_path, format='wav')
            return temp_path
        
        return file_path
    
    def cleanup_temp_file(self, file_path: str, original_path: str):
        """Clean up temp file if it was created"""
        if file_path != original_path and os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except Exception:
                pass

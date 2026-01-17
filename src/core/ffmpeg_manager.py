"""
FFmpeg Manager - Detection, Download, and Installation
"""

import os
import sys
import shutil
import urllib.request
import zipfile
import tempfile
from typing import Optional
from pathlib import Path


class FFmpegManager:
    """Manages FFmpeg detection, download, and installation"""
    
    # Download URLs for static builds
    DOWNLOAD_URLS = {
        "darwin": {
            "ffmpeg": "https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip",
            "ffprobe": "https://evermeet.cx/ffmpeg/getrelease/ffprobe/zip"
        },
        "win32": {
            "ffmpeg": "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
            # Windows build includes ffprobe
        }
    }
    
    def __init__(self):
        self.app_data_dir = self._get_app_data_dir()
        self.bin_dir = os.path.join(self.app_data_dir, "bin")
        self._ensure_path()
        
    def _ensure_path(self):
        """Ensure common paths are in PATH environment variable"""
        common_paths = [
            "/opt/homebrew/bin",
            "/usr/local/bin",
            "/usr/bin",
            "/bin"
        ]
        
        current_path = os.environ.get("PATH", "")
        for path in common_paths:
            if path not in current_path and os.path.exists(path):
                os.environ["PATH"] = f"{path}:{current_path}"
                current_path = os.environ["PATH"]
    
    def _get_app_data_dir(self) -> str:
        """Get the application data directory based on platform"""
        if sys.platform == "darwin":  # macOS
            return os.path.expanduser("~/Library/Application Support/AudioDetectorPro")
        elif sys.platform == "win32":  # Windows
            return os.path.join(os.getenv("LOCALAPPDATA", ""), "AudioDetectorPro")
        else:  # Linux
            return os.path.expanduser("~/.config/AudioDetectorPro")
    
    def find_ffmpeg(self) -> Optional[str]:
        """
        Find FFmpeg executable.
        Search order: 1) App bin directory, 2) System PATH
        
        Returns:
            Path to ffmpeg executable, or None if not found
        """
        # 1. Check app's bin directory first
        if sys.platform == "win32":
            app_ffmpeg = os.path.join(self.bin_dir, "ffmpeg.exe")
        else:
            app_ffmpeg = os.path.join(self.bin_dir, "ffmpeg")
        
        if os.path.exists(app_ffmpeg) and os.access(app_ffmpeg, os.X_OK):
            return app_ffmpeg
        
        # 2. Check system PATH
        system_ffmpeg = shutil.which("ffmpeg")
        if system_ffmpeg:
            return system_ffmpeg
        
        return None
    
    def find_ffprobe(self) -> Optional[str]:
        """Find FFprobe executable"""
        # 1. Check app's bin directory first
        if sys.platform == "win32":
            app_ffprobe = os.path.join(self.bin_dir, "ffprobe.exe")
        else:
            app_ffprobe = os.path.join(self.bin_dir, "ffprobe")
        
        if os.path.exists(app_ffprobe) and os.access(app_ffprobe, os.X_OK):
            return app_ffprobe
        
        # 2. Check system PATH
        system_ffprobe = shutil.which("ffprobe")
        if system_ffprobe:
            return system_ffprobe
        
        return None
    
    def is_installed(self) -> bool:
        """Check if FFmpeg and FFprobe are available"""
        ffmpeg_path = self.find_ffmpeg()
        ffprobe_path = self.find_ffprobe()
        
        # print(f"DEBUG: Found ffmpeg at {ffmpeg_path}")
        # print(f"DEBUG: Found ffprobe at {ffprobe_path}")
        
        return (ffmpeg_path is not None) and (ffprobe_path is not None)
    
    def download_and_install(self, progress_callback=None) -> bool:
        """
        Download and install FFmpeg to the app's bin directory.
        
        Args:
            progress_callback: Optional callable(downloaded_bytes, total_bytes)
            
        Returns:
            True if successful, False otherwise
        """
        if sys.platform not in self.DOWNLOAD_URLS:
            raise RuntimeError(f"Unsupported platform: {sys.platform}")
        
        urls = self.DOWNLOAD_URLS[sys.platform]
        
        try:
            # Create bin directory if it doesn't exist
            os.makedirs(self.bin_dir, exist_ok=True)
            
            # Download ffmpeg
            ffmpeg_url = urls.get("ffmpeg") if isinstance(urls, dict) else urls
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                tmp_path = tmp.name
            
            self._download_file(ffmpeg_url, tmp_path, progress_callback)
            self._extract_ffmpeg(tmp_path, "ffmpeg")
            os.unlink(tmp_path)
            
            # Download ffprobe (macOS only, Windows build includes it)
            if sys.platform == "darwin" and "ffprobe" in urls:
                ffprobe_url = urls["ffprobe"]
                with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                    tmp_path = tmp.name
                
                self._download_file(ffprobe_url, tmp_path, None)  # Don't show progress for ffprobe
                self._extract_ffmpeg(tmp_path, "ffprobe")
                os.unlink(tmp_path)
            
            return True
            
        except Exception as e:
            print(f"FFmpeg download failed: {e}")
            return False
    
    def _download_file(self, url: str, dest: str, progress_callback=None):
        """Download a file with optional progress callback"""
        
        def reporthook(block_num, block_size, total_size):
            if progress_callback:
                downloaded = block_num * block_size
                progress_callback(downloaded, total_size)
        
        urllib.request.urlretrieve(url, dest, reporthook=reporthook)
    
    def _extract_ffmpeg(self, zip_path: str, binary_name: str = "ffmpeg"):
        """Extract FFmpeg/FFprobe binary from the downloaded zip"""
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Find the executable in the archive
            for name in zf.namelist():
                if sys.platform == "win32":
                    target = f"{binary_name}.exe"
                    if name.endswith(target):
                        with zf.open(name) as src:
                            dest_path = os.path.join(self.bin_dir, target)
                            with open(dest_path, 'wb') as dst:
                                dst.write(src.read())
                        break
                else:  # macOS / Linux
                    if name.endswith(binary_name) and not name.endswith("/"):
                        with zf.open(name) as src:
                            dest_path = os.path.join(self.bin_dir, binary_name)
                            with open(dest_path, 'wb') as dst:
                                dst.write(src.read())
                        # Make executable
                        os.chmod(dest_path, 0o755)
                        break
    
    def get_download_page_url(self) -> str:
        """Get the manual download page URL for the current platform"""
        if sys.platform == "darwin":
            return "https://evermeet.cx/ffmpeg/"
        elif sys.platform == "win32":
            return "https://www.gyan.dev/ffmpeg/builds/"
        else:
            return "https://ffmpeg.org/download.html"

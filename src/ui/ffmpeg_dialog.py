"""
FFmpeg Install Dialog - Prompts user to install FFmpeg
"""

import webbrowser
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from src.core.ffmpeg_manager import FFmpegManager


class FFmpegDownloadThread(QThread):
    """Background thread for downloading FFmpeg"""
    progress = pyqtSignal(int, int)  # downloaded, total
    finished = pyqtSignal(bool)  # success
    
    def __init__(self, manager: FFmpegManager):
        super().__init__()
        self.manager = manager
    
    def run(self):
        success = self.manager.download_and_install(
            progress_callback=lambda d, t: self.progress.emit(d, t)
        )
        self.finished.emit(success)


class FFmpegInstallDialog(QDialog):
    """Dialog for FFmpeg installation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = FFmpegManager()
        self.download_thread = None
        
        self.setWindowTitle("FFmpeg Required")
        self.setMinimumWidth(450)
        self.setModal(True)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Message
        msg = QLabel(
            "MP3, FLAC, OGG 등의 오디오 파일을 분석하려면 FFmpeg이 필요합니다.\n\n"
            "To analyze MP3, FLAC, OGG files, FFmpeg is required."
        )
        msg.setWordWrap(True)
        msg.setStyleSheet("font-size: 13px;")
        layout.addWidget(msg)
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Downloading... %p%")
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666666; font-size: 12px;")
        self.status_label.hide()
        layout.addWidget(self.status_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        # Auto install button
        self.auto_btn = QPushButton("🚀 Auto Install")
        self.auto_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078D4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106EBE;
            }
        """)
        self.auto_btn.clicked.connect(self.start_download)
        btn_layout.addWidget(self.auto_btn)
        
        # Manual install button
        self.manual_btn = QPushButton("📥 Manual Install")
        self.manual_btn.setStyleSheet("""
            QPushButton {
                background-color: #F0F0F0;
                color: #333333;
                border: 1px solid #CCCCCC;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #E5E5E5;
            }
        """)
        self.manual_btn.clicked.connect(self.open_download_page)
        btn_layout.addWidget(self.manual_btn)
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666666;
                border: none;
                padding: 10px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                color: #333333;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def start_download(self):
        """Start FFmpeg download in background"""
        self.auto_btn.setEnabled(False)
        self.manual_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.status_label.setText("Downloading FFmpeg...")
        self.status_label.show()
        
        self.download_thread = FFmpegDownloadThread(self.manager)
        self.download_thread.progress.connect(self.on_progress)
        self.download_thread.finished.connect(self.on_finished)
        self.download_thread.start()
    
    def on_progress(self, downloaded: int, total: int):
        """Update progress bar"""
        if total > 0:
            pct = int(downloaded / total * 100)
            self.progress_bar.setValue(pct)
    
    def on_finished(self, success: bool):
        """Handle download completion"""
        if success:
            self.status_label.setText("✅ FFmpeg installed successfully!")
            self.status_label.setStyleSheet("color: #107C10; font-size: 12px;")
            self.accept()  # Close dialog with success
        else:
            self.status_label.setText("❌ Download failed. Please try manual install.")
            self.status_label.setStyleSheet("color: #D13438; font-size: 12px;")
            self.auto_btn.setEnabled(True)
            self.manual_btn.setEnabled(True)
    
    def open_download_page(self):
        """Open FFmpeg download page in browser"""
        url = self.manager.get_download_page_url()
        webbrowser.open(url)
        self.reject()

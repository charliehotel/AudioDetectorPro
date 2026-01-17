"""
Main Window - Audio Detector Pro
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFileDialog, QMessageBox,
    QApplication
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QIcon

from src.ui.drop_zone import DropZone
from src.ui.result_panel import ResultPanel
from src.ui.ffmpeg_dialog import FFmpegInstallDialog
from src.core.vad_analyzer import VADAnalyzer
from src.core.ffmpeg_manager import FFmpegManager
from src.core.audio_loader import AudioLoader  # Keep for format check
from src.core.analysis_worker import AnalysisWorker


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, theme="light"):
        super().__init__()
        self.current_theme = theme
        self.ffmpeg_manager = FFmpegManager()
        self.audio_loader = AudioLoader(self.ffmpeg_manager)
        self.analyzer = VADAnalyzer()
        
        self.setWindowTitle("Audio Detector Pro")
        self.setMinimumSize(600, 500)
        self.resize(700, 550)
        
        self.setup_ui()
        self.apply_theme(self.current_theme)
    
    def setup_ui(self):
        """Setup the user interface"""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 16, 24, 20)
        layout.setSpacing(12)
        
        # Header with title and theme toggle
        header = QHBoxLayout()
        
        # Title
        title_layout = QVBoxLayout()
        title = QLabel("Audio Detector Pro")
        title.setObjectName("title")
        
        # Bilingual description
        desc_en = "Detects speech/non-speech segments using WebRTC VAD and visualizes results. Supports WAV natively; FFmpeg enables more formats."
        desc_ko = "WebRTC VAD로 음성/비음성 구간을 검출하고 시각화합니다. WAV를 기본으로 지원하며, FFmpeg 설치 시 다양한 포맷을 지원합니다."
        subtitle = QLabel(f"{desc_en}\n{desc_ko}")
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header.addLayout(title_layout, 1)  # stretch factor 1 to expand horizontally
        
        # Theme toggle button (no stretch before it, so it stays on the right)
        self.theme_btn = QPushButton("☀️" if self.current_theme == "light" else "🌙")
        self.theme_btn.setObjectName("themeToggle")
        self.theme_btn.setFixedSize(40, 40)
        self.theme_btn.clicked.connect(self.toggle_theme)
        header.addWidget(self.theme_btn, 0, Qt.AlignmentFlag.AlignTop)
        
        layout.addLayout(header)
        
        # Drop zone
        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self.on_file_selected)
        layout.addWidget(self.drop_zone)
        
        # Browse button
        browse_layout = QHBoxLayout()
        browse_layout.addStretch()
        self.browse_btn = QPushButton("Browse Files")
        self.browse_btn.setObjectName("browseBtn")
        self.browse_btn.clicked.connect(self.browse_file)
        browse_layout.addWidget(self.browse_btn)
        browse_layout.addStretch()
        layout.addLayout(browse_layout)
        
        # Result panel
        self.result_panel = ResultPanel()
        layout.addWidget(self.result_panel, 1)
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme(self.current_theme)
        
        # Save preference
        settings = QSettings("AudioDetectorPro", "preferences")
        settings.setValue("theme", self.current_theme)
        
        # Update button icon
        self.theme_btn.setText("☀️" if self.current_theme == "light" else "🌙")
    
    def apply_theme(self, theme):
        """Apply the specified theme"""
        if theme == "dark":
            self.setStyleSheet(DARK_THEME)
        else:
            self.setStyleSheet(LIGHT_THEME)
    
    def browse_file(self):
        """Open file dialog to select audio file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            "",
            "Audio Files (*.wav *.mp3 *.flac *.ogg *.m4a);;All Files (*)"
        )
        if file_path:
            self.on_file_selected(file_path)
    
    def on_file_selected(self, file_path: str):
        """Handle file selection"""
        self.drop_zone.set_file(file_path)
        self.analyze_file(file_path)
    
    def analyze_file(self, file_path: str):
        """Analyze the selected audio file"""
        # Check file extension
        ext = file_path.lower().split('.')[-1]
        
        # Check if format is supported
        if not self.audio_loader.is_supported(file_path):
            QMessageBox.warning(
                self,
                "Unsupported Format",
                f"지원하지 않는 파일 형식입니다: .{ext}"
            )
            self.drop_zone.reset()
            return
        
        # Non-WAV files need ffmpeg
        if ext != 'wav':
            if not self.ffmpeg_manager.is_installed():
                dialog = FFmpegInstallDialog(self)
                result = dialog.exec()
                
                if result == 0:
                    self.drop_zone.reset()
                    return
                
                if not self.ffmpeg_manager.is_installed():
                    QMessageBox.warning(
                        self,
                        "FFmpeg Not Found",
                        "FFmpeg가 설치되지 않았습니다.\n다시 시도해 주세요."
                    )
                    self.drop_zone.reset()
                    return
                
                # Re-configure audio loader with new ffmpeg path
                self.audio_loader = AudioLoader(self.ffmpeg_manager)
        
        # Prepare for analysis
        self.result_panel.show_loading()
        self.drop_zone.setEnabled(False)  # Disable drop zone during analysis
        
        # Create and start worker
        self.worker = AnalysisWorker(file_path, self.analyzer, self.ffmpeg_manager)
        self.worker.status_changed.connect(self.result_panel.show_converting_message)
        self.worker.progress_changed.connect(self.result_panel.show_converting_progress)
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.start()
    
    def on_analysis_finished(self, result):
        """Handle analysis completion"""
        self.result_panel.show_result(result)
        self.drop_zone.setEnabled(True)
        self.worker = None
        
    def on_analysis_error(self, error_msg):
        """Handle analysis error"""
        self.result_panel.show_error(error_msg)
        self.drop_zone.setEnabled(True)
        self.worker = None


# Theme Stylesheets
LIGHT_THEME = """
QMainWindow {
    background-color: #FFFFFF;
}

QLabel#title {
    font-size: 28px;
    font-weight: bold;
    color: #1a1a1a;
}

QLabel#subtitle {
    font-size: 13px;
    color: #666666;
}

QPushButton#themeToggle {
    background-color: transparent;
    border: 1px solid #E5E5E5;
    border-radius: 8px;
    font-size: 18px;
}

QPushButton#themeToggle:hover {
    background-color: #F5F5F5;
}

QPushButton#browseBtn {
    background-color: #0078D4;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 12px 32px;
    font-size: 14px;
    font-weight: bold;
}

QPushButton#browseBtn:hover {
    background-color: #106EBE;
}

QPushButton#browseBtn:pressed {
    background-color: #005A9E;
}

QProgressBar {
    border: none;
    background-color: #E0E0E0;
    border-radius: 4px;
    height: 24px;
    text-align: center;
    color: white;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: #0078D4;
    border-radius: 4px;
}
"""

DARK_THEME = """
QMainWindow {
    background-color: #1E1E1E;
}

QLabel#title {
    font-size: 28px;
    font-weight: bold;
    color: #E0E0E0;
}

QLabel#subtitle {
    font-size: 13px;
    color: #888888;
}

QPushButton#themeToggle {
    background-color: transparent;
    border: 1px solid #3C3C3C;
    border-radius: 8px;
    font-size: 18px;
}

QPushButton#themeToggle:hover {
    background-color: #2D2D2D;
}

QPushButton#browseBtn {
    background-color: #0078D4;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 12px 32px;
    font-size: 14px;
    font-weight: bold;
}

QPushButton#browseBtn:hover {
    background-color: #1084D9;
}

QPushButton#browseBtn:pressed {
    background-color: #006CBE;
}

QProgressBar {
    border: none;
    background-color: #333333;
    border-radius: 4px;
    height: 24px;
    text-align: center;
    color: white;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: #0078D4;
    border-radius: 4px;
}
"""

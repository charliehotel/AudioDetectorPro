"""
Main Window - Audio Detector Pro
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFileDialog, QMessageBox,
    QApplication, QComboBox, QFrame, QListView, QStyledItemDelegate, QStyle
)
from PyQt6.QtCore import Qt, QSettings, QRect
from PyQt6.QtGui import QIcon, QPalette, QColor, QPainter, QPen, QBrush



from src.ui.drop_zone import DropZone
from src.ui.result_panel import ResultPanel
from src.ui.ffmpeg_dialog import FFmpegInstallDialog
from src.core.vad_analyzer import VADAnalyzer
from src.core.ffmpeg_manager import FFmpegManager
from src.core.audio_loader import AudioLoader  # Keep for format check
from src.core.analysis_worker import AnalysisWorker


class ComboBoxDelegate(QStyledItemDelegate):
    """Custom delegate for QComboBox items with theme support"""
    
    def __init__(self, parent=None, is_dark=False):
        super().__init__(parent)
        self.is_dark = is_dark
    
    def set_dark_mode(self, is_dark):
        self.is_dark = is_dark
    
    def paint(self, painter, option, index):
        painter.save()
        
        # Get colors based on theme
        if self.is_dark:
            bg_normal = QColor("#3C3C3C")
            bg_hover = QColor("#505050")
            text_normal = QColor("#E0E0E0")
            text_hover = QColor("#FFFFFF")
        else:
            bg_normal = QColor("#FFFFFF")
            bg_hover = QColor("#E5F3FF")
            text_normal = QColor("#333333")
            text_hover = QColor("#333333")
        
        rect = option.rect
        
        # In QComboBox dropdown, mouse hover triggers State_Selected
        # So we treat both Selected and MouseOver as hover effect
        is_highlighted = (option.state & QStyle.StateFlag.State_Selected) or \
                        (option.state & QStyle.StateFlag.State_MouseOver)
        
        if is_highlighted:
            painter.fillRect(rect, bg_hover)
            text_color = text_hover
        else:
            painter.fillRect(rect, bg_normal)
            text_color = text_normal
        
        # Draw text
        painter.setPen(QPen(text_color))
        text = index.data(Qt.ItemDataRole.DisplayRole)
        text_rect = rect.adjusted(10, 0, -10, 0)  # Padding
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, text)
        
        painter.restore()

    
    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(32)  # Fixed height for items
        return size


class MainWindow(QMainWindow):

    """Main application window"""
    
    def __init__(self, theme="light"):
        super().__init__()
        self.current_theme = theme
        self.ffmpeg_manager = FFmpegManager()
        self.audio_loader = AudioLoader(self.ffmpeg_manager)
        self.analyzer = VADAnalyzer()
        
        self.setWindowTitle("Audio Detector Pro")
        self.setMinimumSize(650, 600)
        self.resize(750, 650)
        
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
        
        # Description
        desc = "Detects speech/non-speech segments using WebRTC VAD and visualizes results. Supports WAV natively; FFmpeg enables more formats."
        subtitle = QLabel(desc)
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
        
        # Configuration Section
        config_frame = QFrame()
        config_frame.setObjectName("configFrame")
        config_layout = QHBoxLayout(config_frame)
        config_layout.setContentsMargins(12, 8, 12, 8)
        config_layout.setSpacing(16)
        
        # Sensitivity
        sens_layout = QVBoxLayout()
        sens_label = QLabel("Sensitivity")
        sens_label.setObjectName("configLabel")
        self.sensitivity_combo = QComboBox()
        sens_view = QListView()
        self.sens_delegate = ComboBoxDelegate(self, is_dark=(self.current_theme == "dark"))
        sens_view.setItemDelegate(self.sens_delegate)
        self.sensitivity_combo.setView(sens_view)
        self.sensitivity_combo.addItems([
            "0: Low (Quiet environment)",
            "1: Normal",
            "2: High (Recommended)",
            "3: Max (Noisy environment)"
        ])
        self.sensitivity_combo.setCurrentIndex(2)
        sens_layout.addWidget(sens_label)
        sens_layout.addWidget(self.sensitivity_combo)
        config_layout.addLayout(sens_layout)
        
        # Frame Duration
        frame_layout = QVBoxLayout()
        frame_label = QLabel("Frame Duration")
        frame_label.setObjectName("configLabel")
        self.frame_duration_combo = QComboBox()
        frame_view = QListView()
        self.frame_delegate = ComboBoxDelegate(self, is_dark=(self.current_theme == "dark"))
        frame_view.setItemDelegate(self.frame_delegate)
        self.frame_duration_combo.setView(frame_view)
        self.frame_duration_combo.addItems([
            "10 ms: Precise (Short speech detection)",
            "20 ms: Balanced",
            "30 ms: Standard (Recommended)"
        ])
        self.frame_duration_combo.setCurrentIndex(2)
        frame_layout.addWidget(frame_label)
        frame_layout.addWidget(self.frame_duration_combo)
        config_layout.addLayout(frame_layout)



        
        layout.addWidget(config_frame)
        
        # Drop zone (click to browse, drag & drop to select)
        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self.on_file_selected)
        self.drop_zone.clicked.connect(self.browse_file)
        layout.addWidget(self.drop_zone)
        

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
        
        is_dark = (theme == "dark")
        
        # Update combo box delegates for theme
        if hasattr(self, 'sens_delegate'):
            self.sens_delegate.set_dark_mode(is_dark)
        if hasattr(self, 'frame_delegate'):
            self.frame_delegate.set_dark_mode(is_dark)
        
        # Update sub-widgets theme
        if hasattr(self, 'drop_zone'):
            self.drop_zone.set_theme(is_dark)
        if hasattr(self, 'result_panel'):
            self.result_panel.set_theme(is_dark)





    
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
        
        # Get configuration values from UI
        sensitivity = int(self.sensitivity_combo.currentText().split(":")[0])
        frame_duration = int(self.frame_duration_combo.currentText().split(" ")[0])
        
        # Create and start worker with configuration
        self.worker = AnalysisWorker(file_path, self.ffmpeg_manager, sensitivity, frame_duration)
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

QFrame#configFrame {
    background-color: #F5F5F5;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
}

QLabel#configLabel {
    font-size: 12px;
    font-weight: bold;
    color: #555555;
}

QComboBox {
    padding: 6px 10px;
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    background-color: white;
    font-size: 12px;
}

QComboBox:hover {
    border-color: #0078D4;
}

QComboBox::drop-down {
    border: none;
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
    background-color: #4A8A50;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 12px 32px;
    font-size: 14px;
    font-weight: bold;
}

QPushButton#browseBtn:hover {
    background-color: #5FAD65;
}

QPushButton#browseBtn:pressed {
    background-color: #3D7042;
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
    background-color: #5FAD65;
    border-radius: 4px;
}

QFrame#configFrame {
    background-color: #2D2D2D;
    border: 1px solid #3C3C3C;
    border-radius: 8px;
}

QLabel#configLabel {
    font-size: 12px;
    font-weight: bold;
    color: #AAAAAA;
}

QComboBox {
    padding: 6px 10px;
    border: 1px solid #555555;
    border-radius: 4px;
    background-color: #3C3C3C;
    color: #E0E0E0;
    font-size: 12px;
}

QComboBox:hover {
    border-color: #0078D4;
}

QComboBox::drop-down {
    border: none;
}
"""



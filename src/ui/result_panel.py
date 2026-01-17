"""
Result Panel - Display analysis results
"""

from src.ui.timeline_widget import TimelineWidget
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QProgressBar, QSizePolicy
)
from PyQt6.QtCore import Qt

from src.core.models import AnalysisResult

class ResultPanel(QWidget):
    """Panel to display VAD analysis results"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.show_empty()
    
    def setup_ui(self):
        """Setup the result panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Container frame
        self.container = QFrame()
        self.container.setObjectName("resultContainer")
        self.container.setStyleSheet("""
            QFrame#resultContainer {
                background-color: #FAFAFA;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(16, 12, 16, 12)
        container_layout.setSpacing(12)  # Increased spacing for timeline
        
        # Status label (for loading/empty/error states)
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #666666; font-size: 14px;")
        container_layout.addWidget(self.status_label)
        
        # Stats grid
        self.stats_widget = QWidget()
        stats_layout = QHBoxLayout(self.stats_widget)
        stats_layout.setSpacing(20)

        self.stats_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.stats_widget.setFixedHeight(100)
        
        # Total duration
        self.total_card = self.create_stat_card("Total Duration", "#333333")
        stats_layout.addWidget(self.total_card)
        
        # Speech duration
        self.speech_card = self.create_stat_card("Speech", "#0078D4")
        stats_layout.addWidget(self.speech_card)
        
        # Non-speech duration
        self.silence_card = self.create_stat_card("Non-Speech", "#666666")
        stats_layout.addWidget(self.silence_card)
        
        container_layout.addWidget(self.stats_widget)
        self.stats_widget.hide()
        
        # Timeline Visualization (NEW)
        self.timeline_widget = TimelineWidget()
        container_layout.addWidget(self.timeline_widget)
        self.timeline_widget.hide()
        
        # Progress bar visualization (kept for compatibility/loading)
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(24)
        # Style defined in main_window.py or QSS
        container_layout.addWidget(self.progress_bar)
        self.progress_bar.hide()
        
        # File name label
        self.file_label = QLabel()
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setStyleSheet("color: #888888; font-size: 11px;")
        container_layout.addWidget(self.file_label)
        self.file_label.hide()
        
        layout.addWidget(self.container)

    def create_stat_card(self, title: str, color: str) -> QWidget:
        """Create a statistics card widget"""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QFontMetrics

        card = QWidget()

        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 카드 내부 여백을 조금 줘서 퍼센트가 아래에서 잘리는 문제를 방지
        layout.setContentsMargins(10, 6, 10, 8)

        # 위젯 사이 간격은 layout spacing으로 통일 (QLabel margin에 의존하지 않기)
        layout.setSpacing(6)

        # Title
        title_label = QLabel(title)

        fm_title = QFontMetrics(title_label.font())
        title_label.setMinimumHeight(fm_title.height() + 4)

        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        title_label.setStyleSheet(
            "color: #888888;"
            "font-size: 11px;"
            "padding-bottom: 2px;"
        )
        layout.addWidget(title_label)
        layout.addSpacing(6)  # 4~8 사이에서 조절

        # Value
        value_label = QLabel("--:--")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setObjectName("value")
        value_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        # margin 대신 padding으로 아래 공간 확보
        value_label.setStyleSheet(
            f"color: {color};"
            "font-size: 28px;"
            "font-weight: bold;"
            "padding-bottom: 2px;"
        )

        # 폰트 메트릭 기준으로 최소 높이를 잡아 글자가 영역 밖으로 삐져나오지 않게
        fm_value = QFontMetrics(value_label.font())
        value_label.setMinimumHeight(fm_value.height() + 12)
        layout.addWidget(value_label)

        layout.addSpacing(10)   # value와 pct 사이 간격 (원하는 만큼만)

        # Percentage
        pct_label = QLabel("--%")
        pct_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pct_label.setObjectName("percentage")
        pct_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        # 아래 잘림 방지용 padding-bottom
        pct_label.setStyleSheet(
            "color: #888888;"
            "font-size: 14px;"
            "padding-top: 2px;"
            "padding-bottom: 2px;"
        )
        fm_pct = QFontMetrics(pct_label.font())
        pct_label.setMinimumHeight(fm_pct.height() + 8)
        layout.addWidget(pct_label)

        return card
    
    def format_time(self, seconds: float) -> str:
        """Format seconds to mm:ss.xx"""
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins:02d}:{secs:05.2f}"

    def show_empty(self):
        """Show empty state"""
        self.status_label.setText("Select an audio file to analyze")
        self.status_label.show()
        self.stats_widget.hide()
        self.timeline_widget.hide()
        self.progress_bar.hide()
        self.file_label.hide()
    
    def show_converting_message(self, message: str):
        """Show converting message (connected to worker signal)"""
        self.status_label.setText(message)
        self.status_label.show()
        self.stats_widget.hide()
        self.timeline_widget.hide()
        
        # Determinate mode for real-time progress
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Initializing...")
        self.progress_bar.show()
        self.file_label.hide()
        
    def show_converting_progress(self, percent: float):
        """Update progress bar with percentage"""
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(int(percent))
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Converting... %p%")
        self.progress_bar.show()
        
    def show_loading(self):
        """Show loading state"""
        self.status_label.setText("Analyzing audio...")
        self.status_label.show()
        self.stats_widget.hide()
        self.timeline_widget.hide()
        
        # Indeterminate mode
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.show()
        self.file_label.hide()
        
    def show_error(self, message: str):
        """Show error state"""
        self.status_label.setText(f"Error: {message}")
        self.status_label.show()
        self.stats_widget.hide()
        self.timeline_widget.hide()
        self.progress_bar.hide()
        self.file_label.hide()
    
    def show_result(self, result: AnalysisResult):
        """Display analysis results"""
        self.status_label.hide()
        
        # Update cards
        total_value = self.total_card.findChild(QLabel, "value")
        total_pct = self.total_card.findChild(QLabel, "percentage")
        total_value.setText(self.format_time(result.total_duration))
        total_pct.setText("100%")
        
        speech_value = self.speech_card.findChild(QLabel, "value")
        speech_pct = self.speech_card.findChild(QLabel, "percentage")
        speech_value.setText(self.format_time(result.speech_duration))
        speech_pct.setText(f"{result.speech_percentage:.1f}%")
        
        silence_value = self.silence_card.findChild(QLabel, "value")
        silence_pct = self.silence_card.findChild(QLabel, "percentage")
        silence_value.setText(self.format_time(result.silence_duration))
        silence_pct.setText(f"{result.silence_percentage:.1f}%")
        
        # Update Timeline
        if result.speech_segments:
            self.timeline_widget.set_data(result.speech_segments, result.total_duration)
            self.timeline_widget.show()
        else:
            self.timeline_widget.hide()
            
        # Hide progress bar (replaced by timeline in result view)
        self.progress_bar.hide()
        
        # Update file label
        self.file_label.setText(f"File: {result.file_name}")
        
        # Show all
        self.stats_widget.show()
        self.file_label.show()

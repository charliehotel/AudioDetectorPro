"""
Timeline Widget - Visualize speech/silence segments
"""

from PyQt6.QtWidgets import QWidget, QToolTip
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QBrush, QMouseEvent

class TimelineWidget(QWidget):
    """Widget to visualize audio segments as a timeline bar"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.segments = []  # List of (start, end) tuples
        self.total_duration = 0.0
        self.setFixedHeight(30)
        self.setMouseTracking(True)
        self.is_dark_theme = False
        
        # Default colors (light theme)
        self._update_colors()
    
    def set_theme(self, is_dark: bool):
        """Set the theme (dark or light)"""
        self.is_dark_theme = is_dark
        self._update_colors()
        self.update()
    
    def _update_colors(self):
        """Update colors based on theme"""
        if self.is_dark_theme:
            # Dark theme - green accent
            self.speech_color = QColor("#5FAD65")
            self.silence_color = QColor("#3C3C3C")
            self.hover_color = QColor("#4A8A50")
        else:
            # Light theme - blue accent
            self.speech_color = QColor("#0078D4")
            self.silence_color = QColor("#E0E0E0")
            self.hover_color = QColor("#005A9E")

        
    def set_data(self, segments: list[tuple[float, float]], total_duration: float):
        """Set segments data and redraw"""
        self.segments = segments
        self.total_duration = total_duration
        self.update()
        
    def paintEvent(self, event):
        """Draw the timeline"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background (silence)
        rect = self.rect()
        painter.fillRect(rect, self.silence_color)
        
        if self.total_duration <= 0:
            return
            
        # Draw speech segments
        width = rect.width()
        height = rect.height()
        
        painter.setBrush(QBrush(self.speech_color))
        painter.setPen(Qt.PenStyle.NoPen)
        
        for start, end in self.segments:
            x = (start / self.total_duration) * width
            w = ((end - start) / self.total_duration) * width
            
            # Ensure minimum width for visibility if duration is very small but non-zero
            if w < 1 and w > 0:
                w = 1
                
            painter.drawRect(QRectF(x, 0, w, height))
            
    def mouseMoveEvent(self, event: QMouseEvent):
        """Show tooltip with time info on hover"""
        if self.total_duration <= 0:
            return
            
        x = event.pos().x()
        width = self.width()
        
        # Calculate time at cursor
        time = (x / width) * self.total_duration
        time_str = self._format_time(time)
        
        # Check if inside a speech segment
        is_speech = False
        for start, end in self.segments:
            if start <= time <= end:
                is_speech = True
                break
        
        
        state = "Speech" if is_speech else "Silence"
        
        # Use mapToGlobal for reliable positioning
        global_pos = self.mapToGlobal(event.pos())
        QToolTip.showText(global_pos, f"{time_str} ({state})", self)
        
    def _format_time(self, seconds: float) -> str:
        """Format seconds to mm:ss"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"

    def enterEvent(self, event):
        """Ensure mouse tracking is active"""
        self.setMouseTracking(True)
        super().enterEvent(event)
        
    def showEvent(self, event):
        """Ensure mouse tracking is active when shown"""
        self.setMouseTracking(True)
        super().showEvent(event)
        
    def leaveEvent(self, event):
        """Hide tooltip when leaving widget"""
        QToolTip.hideText()
        super().leaveEvent(event)

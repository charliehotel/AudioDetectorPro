"""
Drop Zone Widget - Drag and Drop support for audio files
"""

import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QStyleOption, QStyle
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPainter


class DropZone(QWidget):
    """Widget for drag and drop file selection"""
    
    file_dropped = pyqtSignal(str)  # Signal emitted when file is dropped
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.setAcceptDrops(True)
        self.setMinimumHeight(150)
        self.setup_ui()
        self.update_style(False)
    
    def setup_ui(self):
        """Setup the drop zone UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icon label
        self.icon_label = QLabel("🎵")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 48px;")
        layout.addWidget(self.icon_label)
        
        # Text label
        self.text_label = QLabel("Drag & Drop audio file here")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setObjectName("dropText")
        layout.addWidget(self.text_label)
        
        # File name label
        self.file_label = QLabel("")
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setObjectName("fileName")
        self.file_label.hide()
        layout.addWidget(self.file_label)
    
    def paintEvent(self, event):
        """Override paintEvent to enable stylesheets on custom QWidget"""
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)
    
    def update_style(self, hovering: bool):
        """Update visual style based on drag state"""
        if hovering:
            self.setStyleSheet("""
                DropZone {
                    background-color: #CCE5FF;
                    border: 2px dashed #0078D4;
                    border-radius: 12px;
                }
                QLabel#dropText {
                    color: #0078D4;
                    font-size: 14px;
                }
            """)
        else:
            self.setStyleSheet("""
                DropZone {
                    background-color: #F5FAFF;
                    border: 2px dashed #80BFFF;
                    border-radius: 12px;
                }
                QLabel#dropText {
                    color: #0078D4;
                    font-size: 14px;
                }
                QLabel#fileName {
                    color: #333333;
                    font-size: 12px;
                    font-weight: bold;
                }
            """)
        self.repaint()  # Force repaint
    
    def set_file(self, file_path: str):
        """Set the current file and update display"""
        self.current_file = file_path
        file_name = os.path.basename(file_path)
        self.icon_label.setText("✅")
        self.text_label.setText("File selected:")
        self.file_label.setText(file_name)
        self.file_label.show()
    
    def reset(self):
        """Reset drop zone to initial state"""
        self.current_file = None
        self.icon_label.setText("🎵")
        self.text_label.setText("Drag & Drop audio file here")
        self.file_label.setText("")
        self.file_label.hide()
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            # Show hover effect immediately
            self.update_style(True)
            
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile():
                file_path = urls[0].toLocalFile()
                ext = file_path.lower().split('.')[-1]
                if ext in ['wav', 'mp3', 'flac', 'ogg', 'm4a']:
                    event.acceptProposedAction()
                    return
        event.ignore()
    
    def dragLeaveEvent(self, event):
        """Handle drag leave event"""
        self.update_style(False)
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event"""
        self.update_style(False)
        
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                self.file_dropped.emit(file_path)
                event.acceptProposedAction()
    
    def enterEvent(self, event):
        """Handle mouse enter event"""
        self.update_style(True)
    
    def leaveEvent(self, event):
        """Handle mouse leave event"""
        self.update_style(False)

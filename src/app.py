"""
Audio Detector Pro - Application Entry
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings
from src.ui.main_window import MainWindow


def run_app():
    """Initialize and run the application"""
    app = QApplication(sys.argv)
    app.setApplicationName("Audio Detector Pro")
    app.setOrganizationName("AudioDetectorPro")
    
    # Load saved theme preference
    settings = QSettings("AudioDetectorPro", "preferences")
    theme = settings.value("theme", "light")
    
    # Create and show main window
    window = MainWindow(theme=theme)
    window.show()
    
    return app.exec()

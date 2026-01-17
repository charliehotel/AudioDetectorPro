# Release Notes

## v1.0.0 (2025-01-17)

### 🎉 Initial Release

First official release of **Audio Detector Pro**.

### Key Features
- **Core Analysis**: WebRTC VAD integration for robust speech detection.
- **UI/UX**: Modern PyQt6 interface with Drag & Drop support and Result Visualization.
- **Visualization**: Interactive Timeline Widget showing speech (Blue) vs silence (Grey).
- **Format Support**:
  - Native: WAV (PCM)
  - Extended: MP3, FLAC, OGG, M4A (via FFmpeg)
- **FFmpeg Integration**: Automatic detection and downloader for seamless setup.
- **Theming**: System-wide Light/Dark mode toggle with persistence (QSettings).
- **Performance**: Threaded analysis worker for responsive UI execution.

### Improvements (UX)
- Fixed text clipping issues in result statistics cards.
- Optimized layout for various screen sizes.
- Added tooltips to the timeline for precise segment inspection.

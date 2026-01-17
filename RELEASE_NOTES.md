# Release Notes

## v1.1.0 (2025-01-18)

### ✨ New Features
- **VAD Configuration**: Added Sensitivity (0-3) and Frame Duration (10/20/30ms) settings for fine-tuned analysis.
- **Click-to-Browse**: DropZone now supports click to open file browser, in addition to drag & drop.

### 🎨 UI/UX Improvements
- **Dark Theme Enhancement**: Updated accent colors from blue to green for better visual harmony in dark mode.
- **Simplified Interface**: Removed separate Browse button for a cleaner, more intuitive layout.
- **English-only UI**: All labels and options are now in English for consistency.
- **Consistent Result Panel**: Fixed height for stable layout before/after analysis.

### 🔧 Technical Improvements
- **Cross-platform Styling**: Applied Fusion style for consistent appearance across platforms.
- **Custom ComboBox Delegate**: Implemented custom rendering for dropdown menus to fix styling issues on macOS.

---

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

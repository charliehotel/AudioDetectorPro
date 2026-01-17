# Audio Detector Pro 🎵

**Audio Detector Pro** is a desktop application that analyzes audio files to detect speech and non-speech segments using WebRTC VAD. It visualizes the results on an interactive timeline and supports various audio formats (WAV, MP3, FLAC, OGG, M4A) via FFmpeg.

<p align="center">
  <img src="screenshot%201.png" width="32%" alt="Screenshot 1">
  <img src="screenshot%202.png" width="32%" alt="Screenshot 2">
  <img src="screenshot%203.png" width="32%" alt="Screenshot 3">
</p>

## Features ✨

- **Speech Detection (VAD)**: Accurate speech/silence segmentation using WebRTC VAD.
- **Fine-grained Control**: Configurable Sensitivity and Frame Duration settings.
- **Timeline Visualization**: Interactive visualization of speech segments. (Speech: Green, Silence: Grey)
- **Multi-format Support**: Native WAV support + MP3, FLAC, OGG, M4A support (requires FFmpeg).
- **Auto FFmpeg Setup**: Automatically detects or downloads FFmpeg/ffprobe if missing.
- **Click & Drag**: Click to browse files or simply drag audio files into the window.
- **Dual Theme**: Dark mode 🌙 and Light mode ☀️ support with persistent settings.
- **Real-time Progress**: Visual progress bar for audio conversion and analysis status.

## Requirements 🛠️

- Python 3.10+
- PyQt6
- webrtcvad
- pydub
- requests

## Installation 📥

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/AudioDetectorPro.git
   cd AudioDetectorPro
   ```

2. **Create a virtual environment**
   ```bash
   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage 🚀

1. **Run the application**
   ```bash
   ./venv/bin/python main.py
   # or
   python main.py
   ```

2. **Analyze Audio**
   - **Click** the drop zone area to select a file via dialog.
   - Or **Drag & Drop** an audio file onto the window.
   - The analysis will start automatically.
   - Adjust **Sensitivity** and **Frame Duration** for better results if needed.

3. **View Results**
   - Check **Total Duration**, **Speech Duration**, and **Non-Speech Duration**.
   - Hover over the **Timeline** to see precise timestamps and segment types.
   - Toggle **Dark Mode** with the button in the top-right corner.

## Contributing 🤝

Contributions are welcome! Please fork the repository and submit a Pull Request.

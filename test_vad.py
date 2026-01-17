
import os
import sys
import wave
import struct

# Add src to python path
sys.path.append(os.getcwd())

from src.core.vad_analyzer import VADAnalyzer
from src.core.models import AnalysisResult

def create_dummy_wav(filename):
    # Create a 1-second silence + 1-second tone WAV
    sample_rate = 16000
    duration = 2.0
    n_frames = int(sample_rate * duration)
    
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        data = bytearray()
        for i in range(n_frames):
            # First half silence, second half noise/tone
            if i < n_frames // 2:
                sample = 0
            else:
                sample = 1000  # Small amplitude
            
            data.extend(struct.pack('<h', sample))
            
        wav_file.writeframes(data)
    
    return filename

def test_analyzer():
    filename = "test_audio.wav"
    try:
        create_dummy_wav(filename)
        print(f"Created {filename}")
        
        analyzer = VADAnalyzer()
        print("Analyzing...")
        result = analyzer.analyze(filename)
        
        print("Analysis complete!")
        print(f"Speech Segments: {len(result.speech_segments) if result.speech_segments else 0}")
        if result.speech_segments:
            for start, end in result.speech_segments:
                print(f"  - {start:.2f}s to {end:.2f}s")
                
    except Exception as e:
        print(f"CRASH: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    test_analyzer()

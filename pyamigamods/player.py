import os.path
import sys
import pyaudio
import sounddevice
sys.path.append(os.path.dirname(__file__))
import songtools as player

def playmod(module_path,frequency,subsong_index=-1):
    # Play audio and get the memory-backed stream
    capsule = player.play_audio(module_path, frequency, subsong_index)  # Replace with your file and frequency

    # Extract the buffer from the capsule
    buffer = player.get_buffer_content(capsule)

    # Play the buffer using pyaudio
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=2, rate=44100, output=True)
    stream.write(buffer)
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Clean up the capsule
    del capsule


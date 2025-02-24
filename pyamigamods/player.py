import cffi
import os
import sounddevice
import pyaudio
import threading
from pyamigamods.loadlibs import loadlibs

# Path to the raw audio file
raw_audio_file = "/tmp/myaudio.raw"


def playtofile(module_path):
    with open(raw_audio_file, "w") as file:
        C ,ffi=loadlibs()
        ffi.cdef("void cffi_songtools_cli_play(int frequency , char* fname,int subsong);")
        fd_stdout = os.dup(1)
        os.dup2(file.fileno(), 1)
        C.cffi_songtools_cli_play(48000, module_path.encode('utf-8'), 0)
        os.dup2(fd_stdout, 1)

def playmod(module_path):

    if(os.path.exists(raw_audio_file)):
        os.unlink(raw_audio_file)
    player_thread = threading.Thread(target=playtofile, name="Player", args=(module_path,))
    player_thread.start()

    from watchfiles import watch
    for changes in watch(raw_audio_file):
        break

    # Parameters for the raw audio file
    sample_rate = 48000  # Sample rate in Hz
    bit_depth = pyaudio.paInt16  # 16-bit audio
    channels = 2  # Mono audio
    chunk_size = 1024  # Number of frames per buffer
    # Open a stream
    p = pyaudio.PyAudio()
    stream = p.open(format=bit_depth,
                    channels=channels,
                    rate=sample_rate,
                    output=True)
    # Read and play the raw audio file
    with open(raw_audio_file, "rb") as f:
        data = f.read(chunk_size)
        while data:
            stream.write(data)
            data = f.read(chunk_size)
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        os.unlink(raw_audio_file)
        p.terminate()








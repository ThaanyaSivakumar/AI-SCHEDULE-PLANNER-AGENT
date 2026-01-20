import wave
import math
import struct

filename = "alarm.wav"
sample_rate = 44100
duration = 2      # seconds
frequency = 1000  # Hz
volume = 32767

wav = wave.open(filename, "w")
wav.setparams((1, 2, sample_rate, 0, "NONE", "not compressed"))

for i in range(int(sample_rate * duration)):
    value = int(volume * math.sin(2 * math.pi * frequency * i / sample_rate))
    data = struct.pack('<h', value)
    wav.writeframesraw(data)

wav.close()
print("alarm.wav created successfully")

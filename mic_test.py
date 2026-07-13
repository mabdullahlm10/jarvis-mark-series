import pyaudio

p = pyaudio.PyAudio()

stream = p.open(
    format=pyaudio.paInt16,   # 16-bit audio samples
    channels=1,               # mono
    rate=16000,               # 16,000 samples/second (what Gemini Live expects)
    input=True,               # this stream READS from the mic
    frames_per_buffer=512     # chunk size
)

print("Listening for 3 seconds... say something!")
loud = 0
for _ in range(int(16000 / 512 * 3)):     # ~3 seconds of chunks
    data = stream.read(512)
    # crude loudness check: count high-value bytes
    if max(data) > 200:
        loud += 1

stream.close()
p.terminate()

print(f"Done. Loud chunks detected: {loud}")
print("Mic works!" if loud > 0 else "Heard nothing - mic problem, tell Claude.")    
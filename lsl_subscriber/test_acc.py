import pylsl as lsl
import time
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
import mne

BUFFER_SIZE = 500

# first resolve an EEG stream on the lab network
print("looking for an EEG stream...")
streams = lsl.resolve_byprop("type", "ACC")

print(f"Streams found: {streams}")

# create a new inlet to read from the stream
inlet = lsl.StreamInlet(streams[0])
info = inlet.info()
n_channels = info.channel_count()

plt.ion()
fig, ax = plt.subplots()

lines = []
data_buffers = [deque([0.0] * BUFFER_SIZE, maxlen=BUFFER_SIZE) for _ in range(n_channels)]

ch_names = [f"Ch {i+1}" for i in range(n_channels)]

x = np.arange(BUFFER_SIZE)
for ch in range(n_channels):
    line, = ax.plot(x, [0]*BUFFER_SIZE, label=ch_names[ch])
    lines.append(line)

ax.set_ylim(-5000, 5000)
ax.set_xlim(0, BUFFER_SIZE)
ax.legend(loc='upper right')
plt.title("Exg ACC Reading")
plt.xlabel("Samples")
plt.ylabel("ACC Reading")

print(f"Connected to stream: {info.name()} with {n_channels} channels.")

raw_sample_buffer = []

n = 0
while True:
    sample, timestamp = inlet.pull_sample(timeout=1.0)
    n += 1

    if sample is None or timestamp is None:
        continue

    for ch in range(n_channels):
        data_buffers[ch].append(sample[ch])
        lines[ch].set_ydata(data_buffers[ch])

    if n % 10 == 0:
        plt.pause(.001)




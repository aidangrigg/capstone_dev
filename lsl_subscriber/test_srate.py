import pylsl as lsl
import time
import numpy as np

BUFFER_SIZE = 500

# first resolve an EEG stream on the lab network
print("looking for an EEG stream...")
streams = lsl.resolve_byprop("type", "EEG")

print(f"Streams found: {streams}")

# create a new inlet to read from the stream
inlet = lsl.StreamInlet(streams[0])
info = inlet.info()
n_channels = info.channel_count()

print(f"Connected to stream: {info.name()} with {n_channels} channels.")

raw_sample_buffer = []

start = time.time()

n = 0

try:
    while True:
        sample, timestamp = inlet.pull_sample(timeout=0.5)
        if sample is None or timestamp is None:
            continue

        n += 1
except:
    print(f"Time: '{time.time() - start}', Samples: '{n}', Hz: '{n / (time.time() - start)}'")




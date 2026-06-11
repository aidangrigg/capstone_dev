import pylsl as lsl
import time
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
import mne

print("looking for an marker stream...")
streams = lsl.resolve_byprop("type", "marker")

print(f"Streams found: {streams}")

# create a new inlet to read from the stream
inlet = lsl.StreamInlet(streams[0])
info = inlet.info()
n_channels = info.channel_count()


while True:
    sample, timestamp = inlet.pull_sample()
    print(sample)


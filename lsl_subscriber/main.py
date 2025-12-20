"""Example program to show how to read a multi-channel time series from LSL."""

import pylsl as lsl
import time
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
import mne

BUFFER_SIZE = 500          # Number of samples to show in the plot
UPDATE_INTERVAL = 1/250    # Seconds between plot updates

def create_mne_raw(data_array, ch_names):
    """Create an MNE RawArray from the numpy array."""
    info = mne.create_info(ch_names=ch_names, sfreq=250, ch_types='eeg')
    raw = mne.io.RawArray(data_array, info, verbose=False)
    return raw

def main():
    # first resolve an EEG stream on the lab network
    print("looking for an EEG stream...")
    streams = lsl.resolve_byprop("type", "EEG")

    # create a new inlet to read from the stream
    inlet = lsl.StreamInlet(streams[0])
    info = inlet.info()
    n_channels = info.channel_count()
    # n_channels = 1

    plt.ion()
    fig, ax = plt.subplots()

    lines = []
    data_buffers = [deque([0.0] * BUFFER_SIZE, maxlen=BUFFER_SIZE) for _ in range(n_channels)]

    ch_names = [f"Ch {i+1}" for i in range(n_channels)]

    x = np.arange(BUFFER_SIZE)
    for ch in range(n_channels):
        line, = ax.plot(x, [0]*BUFFER_SIZE, label=ch_names[ch])
        lines.append(line)

    ax.set_ylim(270000, 700000)  # Set according to your data range
    ax.set_xlim(0, BUFFER_SIZE)
    ax.legend(loc='upper right')
    plt.title("Real-time LSL Data Plot")
    plt.xlabel("Samples")
    plt.ylabel("Amplitude")

    print(f"Connected to stream: {info.name()} with {n_channels} channels.")

    raw_sample_buffer = []

    # while True:
    #     sample, timestamp = inlet.pull_sample(timeout=1.0)

    #     if sample is None:
    #         continue

    #     raw_sample_buffer.append(sample)

        # if len(raw_sample_buffer) >= BUFFER_SIZE:
        #     # Convert buffer to MNE RawArray
        #     data = np.array(raw_sample_buffer).T  # Shape: (n_channels, n_times)
        #     raw = create_mne_raw(data, ch_names)

        #     # Apply bandpass filter (e.g., 1–40 Hz)
        #     # filtered = mne.filter.filter_data(raw, 250, 1.0, 40.0)
        #     raw.filter(l_freq=1.0, h_freq=40.0, verbose=False)
        #     raw.plot()
        #     # filtered.plot()

        #     # # Get the filtered data
        #     # filtered_data = raw.get_data()

        #     # # Update the plot buffers and lines
        #     # for ch in range(n_channels):
        #     #     data_buffers[ch].extend(filtered_data[ch])
        #     #     lines[ch].set_ydata(data_buffers[ch])

        #     raw_sample_buffer.clear()
        # plt.pause(.001)

    n = 0
    while True:
        # get a new sample (you can also omit the timestamp part if you're not
        # interested in it)
        sample, timestamp = inlet.pull_sample(timeout=1.0)

        n += 1
        # print(sample)

        if sample is None or timestamp is None:
            return

        for ch in range(n_channels):
            data_buffers[ch].append(sample[ch])
            lines[ch].set_ydata(data_buffers[ch])

        # if n % BUFFER_SIZE == 0:
        #     minimum = 100000000
        #     maximum = 0
        #     for p in data_buffers[0]:
        #         if p <= minimum:
        #             minimum = p
        #         elif p >= maximum:
        #             maximum = p

        #     data_buffers[0].clear()
        #     ax.set_ylim(minimum, maximum)  # Set according to your data range

        if n % 10 == 0:
            plt.pause(.001)

if __name__ == "__main__":
    main()

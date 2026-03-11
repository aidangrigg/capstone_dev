import pylsl as lsl
import scipy.signal as sp
import numpy as np
from collections import deque
import time

class LSLDataSource():
    def __init__(self, window_length: float = 10.0):
        self.connected = False
        self._window_length = window_length
        self._butter_zi: list[float] | None = None
        self._notch_zi: list[float] | None = None

    def get_streams(self) -> list[lsl.StreamInfo]:
        return lsl.resolve_byprop("type", "EEG")

    def connect(self, stream: lsl.StreamInfo, timeout: float = 60.0) -> bool:
        self._inlet = lsl.StreamInlet(stream)
        try:
            self._info: lsl.StreamInfo = self._inlet.info(timeout)
            max_points = int(self._window_length * self._info.nominal_srate())
            channel_count = self._info.channel_count()
            self._queue = deque(np.zeros((max_points, channel_count)))
            self.buf = np.zeros((max_points, channel_count))
            self.connected = True
            self.channel_count = self._info.channel_count()
            self.sampling_rate = self._info.nominal_srate()
            return True
        except lsl.util.TimeoutError:
            return False
        except lsl.util.LostError:
            return False

    def _bandpass_sample(self, sample: list[float], bandpass):
        assert(self._butter_zi is not None)
        for ch in range(self.channel_count):
            y, zi  = sp.sosfilt(bandpass, [sample[ch]], zi=self._butter_zi[ch])
            sample[ch] = y[0]
            self._butter_zi[ch] = zi

    def _notch_sample(self, sample: list[float], b, a):
        assert(self._notch_zi is not None)
        for ch in range(self.channel_count):
            # y, zi  = sp.sosfilt(bandpass, [sample[ch]], zi=self._butter_zi[ch])
            y, zi = sp.lfilter(b, a, [sample[ch]], zi=self._notch_zi[ch])
            sample[ch] = y[0]
            self._notch_zi[ch] = zi

    def pull_samples(
        self,
        bandpass: tuple[float, float] | None = (1.0, 30.0),
        notch: float | None = 50.0
    ) -> int:
        """
        Pulls in samples from the LSL stream into buffer.

        Returns: the number of samples pulled in
        """
        if not self.connected:
            return 0

        if bandpass is not None:
            nyq = 0.5 * self.sampling_rate
            # TODO: configuring butterworth order
            sos_butter_filter = sp.butter(4, [bandpass[0] / nyq, bandpass[1] / nyq], btype='band', output='sos')
            if self._butter_zi is None:
                self._butter_zi = [sp.sosfilt_zi(sos_butter_filter) * [0] for ch in range(self.channel_count)]

        if notch is not None:
            notch_b, notch_a = sp.iirnotch(notch, 30, self.sampling_rate)
            if self._notch_zi is None:
                self._notch_zi = [sp.lfilter_zi(notch_b, notch_a) for ch in range(self.channel_count)]

        samples_read = 0
        sample, timestamp = self._inlet.pull_sample(timeout = 0.0)
        while sample is not None:
            samples_read += 1
            if bandpass is not None:
                self._bandpass_sample(sample, sos_butter_filter)
            if notch is not None:
                self._notch_sample(sample, notch_b, notch_a)
            self._queue.append(sample)
            self._queue.popleft()
            sample, timestamp = self._inlet.pull_sample(timeout = 0.0)

        self.buf = np.array(self._queue)
        return samples_read

    def welch(self, channel: int = 0) -> tuple[np.ndarray, np.ndarray]:
        return sp.welch(self.buf[:, channel], self._info.nominal_srate(), axis=0, nperseg=(2.5 * self.sampling_rate))

if __name__ == "__main__":
    datasource = LSLDataSource()
    streams = datasource.get_streams()
    datasource.connect(streams[0])

    while(True):
        time.sleep(1)
        print(f"samples: {datasource.pull_samples()}")


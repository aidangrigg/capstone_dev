from PySide6.QtCore import QObject, QTimer, Signal
from numpy.typing import NDArray
import pylsl as lsl
import numpy as np
import scipy.signal as sp
from collections import deque
import time

from brainground.application import BraingroundApplication

class LSLDataSource(QObject):
    samples_recieved = Signal(np.ndarray)

    def __init__(self, window_length: float = 10.0):
        super().__init__()

        self.connected = False
        self._window_length = window_length
        self._butter_zi: list[NDArray[np.float64]] | None = None
        self._notch_zi: list[NDArray[np.float64]] | None = None
        streams = self.get_streams()
        self.connect_stream(streams[0])

        self.timer = QTimer()
        self.timer.timeout.connect(self.run)
        self.timer.start(int(1000 / 100))

    def get_streams(self) -> list[lsl.StreamInfo]:
        return lsl.resolve_byprop("type", "EEG")

    def connect_stream(self, stream: lsl.StreamInfo, timeout: float = 60.0) -> bool:
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

            app = BraingroundApplication.get_app()
            app.settings.channel_count = self.channel_count
            app.settings.sampling_rate = self.sampling_rate

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
            y, zi = sp.lfilter(b, a, [sample[ch]], zi=self._notch_zi[ch])
            sample[ch] = y[0]
            self._notch_zi[ch] = zi

    def pull_samples(
        self,
        bandpass: tuple[float, float] | None = (1.0, 30.0),
        notch: float | None = 50.0
    ):
        """
        Pulls in samples from the LSL stream into buffer.

        Returns: the number of samples pulled in
        """
        if not self.connected:
            return 0

        sos_butter_filter = None
        notch_b, notch_a = None, None
        if bandpass is not None:
            nyq = 0.5 * self.sampling_rate
            sos_butter_filter = sp.butter(4, [bandpass[0] / nyq, bandpass[1] / nyq], btype='band', output='sos')
            if self._butter_zi is None:
                self._butter_zi = [sp.sosfilt_zi(sos_butter_filter) * [0] for _ in range(self.channel_count)]

        if notch is not None:
            notch_b, notch_a = sp.iirnotch(notch, 30, self.sampling_rate)
            if self._notch_zi is None:
                self._notch_zi = [sp.lfilter_zi(notch_b, notch_a) for _ in range(self.channel_count)]

        samples, timestamps = self._inlet.pull_chunk(timeout = 0.0)

        if timestamps and samples:
            for sample in samples:
                if bandpass is not None:
                    self._bandpass_sample(sample, sos_butter_filter)
                if notch is not None:
                    self._notch_sample(sample, notch_b, notch_a)
                self._queue.append(np.array(sample))
                self._queue.popleft()

        self.buf = np.array(self._queue)
        self.samples_recieved.emit(self.buf)

    def run(self):
        self.pull_samples()

if __name__ == "__main__":
    datasource = LSLDataSource()
    while(True):
        time.sleep(1)
        print(f"samples: {datasource.pull_samples()}")


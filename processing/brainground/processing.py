from typing import Any
from enum import Enum

from scipy.integrate import simpson
import scipy.signal as sp
import numpy as np
from PySide6.QtCore import QObject, QTimer, Signal

class Types(Enum):
    BANDPOWER = 1
    FAA = 2

FREQUENCY_BANDS = [
    (0.0, 3.0), # Delta
    (3.0, 7.0), # Theta
    (7.0, 12.0), # Alpha
    (12.0, 16.0), # SMR
    (12.0, 30.0), # Beta
    (30.0, 50.0), # Gamma
]

class NeurofeedbackProcessing(QObject):
    metric_computed = Signal(float)

    def __init__(self):
        super().__init__()

        self.type = Types.BANDPOWER
        self.active_channels = [True, False, False, False, False, False, False, False]
        self.active_bands = [True, False, False, False, False, False]
        self.timer = QTimer()
        self.timer.timeout.connect(self.run)
        self.timer.start(int(1000 / 20))

        max_points = int(10 * 250)
        self.channel_count = 8
        self.buffer = np.zeros((max_points, self.channel_count))
        self.sampling_rate = 250

    def update_buffer(self, buf: np.ndarray[Any, np.dtype[np.float64]]):
        self.buffer = buf

    def run(self):
        match self.type:
            case Types.BANDPOWER:
                self.metric_computed.emit(self.compute_bandpower_score())
            case Types.FAA:
                pass

    def welch(self, channel: int = 0) -> tuple[np.ndarray, np.ndarray]:
        return sp.welch(self.buffer[:, channel], self.sampling_rate, axis=0, nperseg=int(2.5 * self.sampling_rate))

    def compute_bandpower_score(self):
        psd_values = [[] for _ in range(self.channel_count)]
        for ch in range(self.channel_count):
            freqs, psd = self.welch(ch)
            freq_res = freqs[1] - freqs[0]

            for i, band in enumerate(FREQUENCY_BANDS):
                if not self.active_bands[i]:
                    continue
                idxs = np.logical_and(freqs >= band[0], freqs <= band[1])
                bp = simpson(psd[idxs], dx=freq_res)
                psd_values[ch].append(bp)

        psd_values = np.array(psd_values).transpose() # [:band [:channel]]

        arr = []
        for channels in psd_values:
            power_in_band = []
            for ch, power in enumerate(channels):
                if self.active_channels[ch]:
                    power_in_band.append(power)

            arr.append(np.mean(power_in_band))

        return np.mean(arr)

    def compute_faa_score(self):
        raise NotImplemented


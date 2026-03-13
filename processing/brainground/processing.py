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

AVG_TIME_WINDOW = 5

class NeurofeedbackProcessing(QObject):
    metric_computed = Signal(float)

    def __init__(self, channel_count: int, sampling_rate: float, window_length: float):
        super().__init__()

        self.refresh_rate = 1000 / 20

        self.channel_count = channel_count
        self.sampling_rate = sampling_rate
        self.window_length = window_length

        self.band_average: float | None = None
        self.computing_average = False
        self.psd_readings: list[float] = []
        self.psd_average_readings = (AVG_TIME_WINDOW * 1000) // self.refresh_rate

        self.type = Types.BANDPOWER
        self.active_channels = [False for _ in range(channel_count)]
        self.active_bands = [False for _ in range(len(FREQUENCY_BANDS))]
        self.timer = QTimer()
        self.timer.timeout.connect(self.run)
        self.timer.start(int(self.refresh_rate))

        max_points = int(self.window_length * self.sampling_rate)
        self.buffer = np.zeros((max_points, self.channel_count))

        self.psd = [np.empty(1) for _ in range(self.channel_count)]
        self.freqs = np.empty(1)

    def compute_average_bandpower(self):
        self.band_average = None
        self.psd_readings = []
        self.computing_average = True

    def set_active_channels(self, channels):
        self.band_average = None
        self.active_channels = channels

    def set_active_bands(self, band):
        self.band_average = None
        self.active_bands = band

    def update_buffer(self, buf: np.ndarray[Any, np.dtype[np.float64]]):
        self.buffer = buf

    def run(self):
        match self.type:
            case Types.BANDPOWER:
                if self.computing_average:
                    self.compute_band_average()
                elif self.band_average is not None:
                    self.metric_computed.emit(self.compute_bandpower_score() - self.band_average)
            case Types.FAA:
                pass

    def welch(self, channel: int = 0) -> tuple[np.ndarray, np.ndarray]:
        return sp.welch(self.buffer[:, channel], self.sampling_rate, axis=0, nperseg=int(2.5 * self.sampling_rate))

    def compute_band_average(self):
        p = self.compute_bandpower_score()
        self.psd_readings.append(p)

        if len(self.psd_readings) >= self.psd_average_readings:
            self.computing_average = False
            print(f"self.psd_readings = {self.psd_readings}")
            self.band_average = float(np.mean(self.psd_readings))

    def compute_bandpower_score(self) -> float:
        psd_values = [[] for _ in range(self.channel_count)]
        for ch in range(self.channel_count):
            self.freqs, self.psd[ch] = self.welch(ch)
            freq_res = self.freqs[1] - self.freqs[0]

            for i, band in enumerate(FREQUENCY_BANDS):
                if not self.active_bands[i]:
                    continue
                idxs = np.logical_and(self.freqs >= band[0], self.freqs <= band[1])
                bp = simpson(self.psd[ch][idxs], dx=freq_res)
                psd_values[ch].append(bp)

        psd_values = np.array(psd_values).transpose() # [:band [:channel]]

        arr = []
        for channels in psd_values:
            power_in_band = []
            for ch, power in enumerate(channels):
                if self.active_channels[ch]:
                    power_in_band.append(power)

            arr.append(np.mean(power_in_band))

        return float(np.mean(arr))

    def compute_faa_score(self):
        raise NotImplemented


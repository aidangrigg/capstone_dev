
import numpy as np
from scipy.integrate import simpson
from biomarker.base import Biomarker
from biomarker.types import FFT

class BandpowerSettings():
    channels: list[int] = [0, 1]
    band: tuple[int, int] = (7.0, 12.0)
    baseline: float = 100.0

class BandpowerBiomarker(Biomarker):
    settings = BandpowerSettings()

    score = 0.0

    def __init__(self, id: int):
        super().__init__(id)

    def update_settings(self, new_settings: BandpowerSettings):
        self.settings = new_settings

    def compute(self, buffer: np.ndarray, fft: FFT):
        idxs = np.logical_and(fft.freqs >= self.settings.band[0],  fft.freqs <= self.settings.band[1])

        bp_total = 0.0
        for channel in self.settings.channels:
            bp_total += simpson(fft.psd[channel][idxs], dx=fft.resolution)

        bp = bp_total / len(self.settings.channels)

        # TODO: compute difference from average
        self.score = bp - self.settings.baseline

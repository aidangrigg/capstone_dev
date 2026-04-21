
import numpy as np
from scipy.integrate import simpson
from brainground.biomarker.base import Biomarker
from brainground.biomarker.types import FFT, FrequencyBands

class BandpowerSettings():
    channels: list[int] = [0, 1]
    band: FrequencyBands = FrequencyBands.ALPHA
    baseline: float = 100.0

class BandpowerBiomarker(Biomarker):
    settings = BandpowerSettings()

    score = 0.0

    def __init__(self, id: int, name: str):
        super().__init__(id, name)

    def update_settings(self, new_settings: BandpowerSettings):
        self.settings = new_settings

    def compute(self, buffer: np.ndarray, fft: FFT):
        band_tuple = self.settings.band.value
        idxs = np.logical_and(fft.freqs >= band_tuple[0],  fft.freqs <= band_tuple[1])

        bp_total = 0.0
        for channel in self.settings.channels:
            bp_total += simpson(fft.psd[channel][idxs], dx=fft.resolution)

        bp = bp_total / len(self.settings.channels)

        # TODO: compute difference from average
        self.score = bp - self.settings.baseline

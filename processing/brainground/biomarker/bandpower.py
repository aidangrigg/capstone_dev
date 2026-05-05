
import logging
import numpy as np
from scipy.integrate import simpson
from brainground.biomarker.base import Biomarker
from brainground.biomarker.types import FFT, BiomarkerType, FrequencyBand

class BandpowerSettings():
    channels: list[int] = [0, 1]
    band: FrequencyBand = FrequencyBand.ALPHA
    baseline: float = 100.0
    relative: bool = False

class BandpowerBiomarker(Biomarker):
    settings = BandpowerSettings()

    score = 0.0

    def __init__(self, id: int, name: str, type: BiomarkerType):
        super().__init__(id, name, type)

    def update_settings(self, new_settings: BandpowerSettings):
        self.settings = new_settings

    def compute_relative_bandpower(self, fft: FFT) -> None:
        band_tuple = self.settings.band.value
        idxs = np.logical_and(fft.freqs >= band_tuple[0],  fft.freqs <= band_tuple[1])

        bp_sum = 0.0
        bp_total_sum = 0.0
        for channel in self.settings.channels:
            bp_sum += simpson(fft.psd[channel][idxs], dx=fft.resolution)
            bp_total_sum += fft.total_bandpower[channel]

        bp = bp_sum / len(self.settings.channels)
        total_bp = bp_total_sum / len(self.settings.channels)

        self.score = ((bp / total_bp) * 100) - self.settings.baseline

    def compute_absolute_bandpower(self, fft: FFT) -> None:
        band_tuple = self.settings.band.value
        idxs = np.logical_and(fft.freqs >= band_tuple[0],  fft.freqs <= band_tuple[1])

        bp_total = 0.0
        for channel in self.settings.channels:
            bp_total += simpson(fft.psd[channel][idxs], dx=fft.resolution)

        bp = bp_total / len(self.settings.channels)

        self.score = bp - self.settings.baseline
        logging.info("New bandpower score computed for %s, value: %d", self.iden.name(), self.score)

    def compute(self, buffer: np.ndarray, fft: FFT):
        if self.settings.relative:
            self.compute_relative_bandpower(fft)
        else:
            self.compute_absolute_bandpower(fft)


import logging
import numpy as np
from scipy.integrate import simpson

from brainground.biomarker.base import Biomarker
from brainground.biomarker.types import FFT, BiomarkerType, FrequencyBand

class AsymmetrySettings():
    left_channel: int = 0
    right_channel: int = 1
    band: FrequencyBand = FrequencyBand.ALPHA
    relative: bool = False

class AsymmetryBiomarker(Biomarker):
    settings = AsymmetrySettings()

    score = 0.0

    def __init__(self, id: int, name: str, type: BiomarkerType):
        super().__init__(id, name, type)

    def update_settings(self, new_settings: AsymmetrySettings):
        self.settings = new_settings

    def compute_relative_asymmetry(self, fft: FFT) -> None:
        band_range = self.settings.band.value
        idxs = np.logical_and(fft.freqs >= band_range[0],  fft.freqs <= band_range[1])

        left_bp = simpson(fft.psd[self.settings.left_channel][idxs], dx=fft.resolution)
        right_bp = simpson(fft.psd[self.settings.right_channel][idxs], dx=fft.resolution)

        total_left_bp = fft.total_bandpower[self.settings.left_channel]
        total_right_bp = fft.total_bandpower[self.settings.right_channel]

        rel_left_bp = (left_bp / total_left_bp) * 100.0
        rel_right_bp = (right_bp / total_right_bp) * 100.0

        self.score = rel_right_bp - rel_left_bp
        logging.info("New asymmetry score computed for %s, value: %d", self.iden.name(), self.score)

    def compute_absolute_asymmetry(self, fft: FFT) -> None:
        band_range = self.settings.band.value
        idxs = np.logical_and(fft.freqs >= band_range[0],  fft.freqs <= band_range[1])

        left_bp = simpson(fft.psd[self.settings.left_channel][idxs], dx=fft.resolution)
        right_bp = simpson(fft.psd[self.settings.right_channel][idxs], dx=fft.resolution)

        self.score = right_bp - left_bp
        logging.info("New asymmetry score computed for %s, value: %d", self.iden.name(), self.score)

    def compute(self, buffer: np.ndarray, fft: FFT):
        if self.settings.relative:
            self.compute_relative_asymmetry(fft)
        else:
            self.compute_absolute_asymmetry(fft)

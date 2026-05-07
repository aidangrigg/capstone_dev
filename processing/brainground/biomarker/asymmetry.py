
import logging
import numpy as np
from scipy.integrate import simpson

from brainground.biomarker.base import Biomarker
from brainground.biomarker.types import FFT, BiomarkerType, FrequencyBand

class AsymmetrySettings():
    left_channel: int = 0
    right_channel: int = 1
    band: FrequencyBand = FrequencyBand.ALPHA

class AsymmetryBiomarker(Biomarker):
    settings = AsymmetrySettings()

    score = 0.0

    def __init__(self, id: int, name: str, type: BiomarkerType):
        super().__init__(id, name, type)

    def update_settings(self, new_settings: AsymmetrySettings):
        self.settings = new_settings

    def compute(self, buffer: np.ndarray, fft: FFT):
        band_range = self.settings.band.value
        idxs = np.logical_and(fft.freqs >= band_range[0],  fft.freqs <= band_range[1])

        left_bp = simpson(fft.psd[self.settings.left_channel][idxs], dx=fft.resolution)
        right_bp = simpson(fft.psd[self.settings.right_channel][idxs], dx=fft.resolution)

        self.score = left_bp - right_bp
        logging.info("New asymmetry score computed for %s, value: %d", self.iden.name(), self.score)

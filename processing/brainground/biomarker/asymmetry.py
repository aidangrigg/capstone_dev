
import numpy as np
from scipy.integrate import simpson

from brainground.biomarker.base import Biomarker
from brainground.biomarker.types import FFT

class AsymmetrySettings():
    left_channel: int = 0
    right_channel: int = 1
    band: tuple[float, float] = (7.0, 12.0)

class AsymmetryBiomarker(Biomarker):
    settings = AsymmetrySettings()

    score = 0.0

    def __init__(self, id: int, name: str):
        super().__init__(id, name)

    def update_settings(self, new_settings: AsymmetrySettings):
        self.settings = new_settings

    def compute(self, buffer: np.ndarray, fft: FFT):
        idxs = np.logical_and(fft.freqs >= self.settings.band[0],  fft.freqs <= self.settings.band[1])

        left_bp = simpson(fft.psd[self.settings.left_channel][idxs], dx=fft.resolution)
        right_bp = simpson(fft.psd[self.settings.right_channel][idxs], dx=fft.resolution)

        self.score = right_bp - left_bp

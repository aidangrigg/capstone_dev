from enum import Enum
import numpy as np

class BiomarkerTypes(Enum):
    BANDPOWER = 1
    ASYMMETRY = 2

class FFT:
    freqs: np.ndarray
    psd: list[np.ndarray]
    resolution = 0.0

    def clear(self):
        self.freqs = np.empty(1)
        self.psd: list[np.ndarray] = []
        self.resolution = 0.0

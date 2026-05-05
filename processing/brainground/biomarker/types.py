from enum import Enum
import numpy as np

class FrequencyBand(Enum):
    DELTA = (0.0, 3.0)
    THETA = (3.0, 7.0)
    ALPHA = (7.0, 12.0)
    SMR = (12.0, 16.0)
    BETA = (12.0, 30.0)
    GAMMA = (30.0, 50.0)

class BiomarkerType(Enum):
    BANDPOWER = 1
    ASYMMETRY = 2

class FFT:
    freqs: np.ndarray
    psd: list[np.ndarray]
    resolution = 0.0
    total_bandpower: list[float] = []

    def clear(self):
        self.freqs = np.empty(1)
        self.psd: list[np.ndarray] = []
        self.resolution = 0.0
        self.total_bandpower = []

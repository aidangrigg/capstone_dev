
import numpy as np
from scipy.integrate import simpson
from biomarker.base import Biomarker
from biomarker.types import FFT

class BandpowerBiomarker(Biomarker):
    settings = {
        "channels": [0, 1],
        "band": (7.0, 12.0),
        "baseline": 100.0,
    }

    score = 0.0

    def __init__(self, id: int):
        super().__init__(id)

    def compute(self, buffer: np.ndarray, fft: FFT):
        idxs = np.logical_and(fft.freqs >= self.settings["band"][0],  fft.freqs <= self.settings["band"][1])

        bp_total = 0.0
        for channel in self.settings["channels"]:
            bp_total += simpson(fft.psd[channel][idxs], dx=fft.resolution)

        bp = bp_total / len(self.settings["channels"])

        # TODO: compute difference from average
        self.score = bp - self.settings["baseline"]


from abc import ABC, abstractmethod
from numpy import ndarray

from biomarker.types import FFT

class Biomarker(ABC):
    def __init__(self, id: int):
        self.id = id

    @abstractmethod
    def compute(self, buffer: ndarray, fft: FFT):
        pass

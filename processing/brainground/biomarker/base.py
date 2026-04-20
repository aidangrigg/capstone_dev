
from abc import ABC, abstractmethod
from PySide6.QtCore import Signal, QObject
from numpy import ndarray

from biomarker.types import FFT

class BiomarkerIdentifier(QObject):
    name_changed = Signal(str)

    def __init__(self, id: int, name: str):
        self.__id = id
        self.__name = name

    def name(self) -> str:
        return self.__name

    def id(self) -> int:
        return self.__id

    def set_name(self, name: str):
        self.__name = name
        self.name_changed.emit(name)

class Biomarker(ABC):
    def __init__(self, id: int, name: str):
        self.iden = BiomarkerIdentifier(id, name)
        self.score = 0

    @abstractmethod
    def compute(self, buffer: ndarray, fft: FFT):
        pass

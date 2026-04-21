
from abc import ABC, abstractmethod
from PySide6.QtCore import Signal, QObject
from numpy import ndarray

from brainground.biomarker.types import FFT, BiomarkerType

class BiomarkerIdentifier(QObject):
    name_changed = Signal(str)

    def __init__(self, id: int, name: str, type: BiomarkerType):
        super().__init__()
        self.__id = id
        self.__name = name
        self.__type = type

    def type(self) -> BiomarkerType:
        return self.__type

    def name(self) -> str:
        return self.__name

    def id(self) -> int:
        return self.__id

    def set_name(self, name: str):
        self.__name = name
        self.name_changed.emit(name)

class Biomarker(ABC):
    def __init__(self, id: int, name: str, type: BiomarkerType):
        self.iden = BiomarkerIdentifier(id, name, type)
        self.score = 0

    @abstractmethod
    def compute(self, buffer: ndarray, fft: FFT):
        pass

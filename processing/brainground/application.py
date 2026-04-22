
from typing import Sequence, cast
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication

from brainground.biomarker.base import BiomarkerIdentifier
from brainground.biomarker.types import BiomarkerType

class ApplicationSettings():
    channel_count: int = 4
    sampling_rate: float = 250.0
    window_size: float = 10.0

class BraingroundApplication(QApplication):
    request_biomarker_added = Signal(BiomarkerType, str)
    request_biomarker_deleted = Signal(int)

    biomarker_added = Signal(BiomarkerIdentifier)
    biomarker_deleted = Signal(int) # id

    settings = ApplicationSettings()

    def __init__(self, arguments: Sequence[str]):
        super().__init__(arguments)

    @classmethod
    def get_app(cls) -> "BraingroundApplication":
        inst = super().instance()
        assert inst is not None
        return cast("BraingroundApplication", inst)


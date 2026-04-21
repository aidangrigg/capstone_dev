
from typing import Sequence
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication

from brainground.biomarker.base import BiomarkerIdentifier
from brainground.biomarker.types import BiomarkerType


class BraingroundApplication(QApplication):
    request_biomarker_added = Signal(BiomarkerType, str)
    request_biomarker_deleted = Signal(int)

    biomarker_added = Signal(BiomarkerIdentifier)
    biomarker_deleted = Signal(int) # id

    def __init__(self, arguments: Sequence[str]):
        super().__init__(arguments)


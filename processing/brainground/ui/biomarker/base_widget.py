
from abc import ABC, abstractmethod

from PySide6.QtWidgets import QVBoxLayout, QWidget

from biomarker.base import Biomarker


class BaseBiomarkerWidget(ABC):
    def __init__(self, node: Biomarker):
        self.node = node
        self.base_widget = QWidget()
        self.layout = QVBoxLayout(self.base_widget)
        self.plot = None

    def id(self):
        return self.node.id

    @abstractmethod
    def update(self):
        pass



from abc import ABC, abstractmethod

from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QWidget

from biomarker.base import Biomarker


class BaseBiomarkerWidget(ABC):
    def __init__(self, node: Biomarker):
        self.node = node
        self.base_widget = QWidget()
        self.layout = QVBoxLayout(self.base_widget)

        self.header_bar = QWidget()
        self.header_layout = QHBoxLayout(self.header_bar)

        self.title_text = QLabel("Bandpower Widget")

        settings_button = QPushButton("Settings")
        settings_button.clicked.connect(self.create_settings_dialog)

        self.header_layout.addWidget(self.title_text)
        self.header_layout.addWidget(settings_button)

        self.layout.addWidget(self.header_bar)
        self.plot = None

    def settings_button_pressed(self):
        pass

    def id(self):
        return self.node.id

    @abstractmethod
    def create_settings_dialog(self):
        pass

    @abstractmethod
    def update(self):
        pass


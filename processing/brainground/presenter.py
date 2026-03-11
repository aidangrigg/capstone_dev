from PySide6.QtCore import QObject

from processing import NeurofeedbackProcessing
from view import MainView

class Presenter(QObject):
    def __init__(self, view: MainView, processing: NeurofeedbackProcessing):
        super().__init__()

        self.processing = processing
        self.view = view

        self.processing.metric_computed.connect(self.metric_computed)

    def metric_computed(self, delta: float):
        self.view.set_eeg_plot(self.processing.buffer)
        self.view.set_bandpower_delta_plot(delta)

    def update_processing(self):
        raise NotImplemented


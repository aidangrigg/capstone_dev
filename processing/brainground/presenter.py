from PySide6.QtCore import QObject, QTimer

from processing import NeurofeedbackProcessing
from view import MainView

class Presenter(QObject):
    def __init__(self, view: MainView, processing: NeurofeedbackProcessing):
        super().__init__()

        self.refresh_rate = 1000 / 20

        self.processing = processing
        self.view = view

        self.timer = QTimer()
        self.timer.timeout.connect(self.run)
        self.timer.start(int(self.refresh_rate))

        self.processing.metric_computed.connect(self.view.set_bandpower_delta_plot)
        self.view.active_bands_set.connect(self.processing.set_active_bands)
        self.view.active_channels_set.connect(self.processing.set_active_channels)
        self.view.compute_new_average.connect(self.processing.compute_average_bandpower)

    def run(self):
        self.view.set_eeg_plot(self.processing.buffer)
        self.view.set_psd_plot(self.processing.freqs, self.processing.psd)

    def update_processing(self):
        raise NotImplemented


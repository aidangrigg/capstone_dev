from enum import Enum

from PySide6.QtCore import QObject, QTimer
import numpy as np
from scipy.signal import welch

from biomarker.bandpower import BandpowerBiomarker
from biomarker.base import Biomarker
from biomarker.types import FFT
from lsl_datasource import LSLDataSource
from ui.biomarker.bandpower_widget import BandpowerWidget
from ui.biomarker.base_widget import BaseBiomarkerWidget
from ui.main_view import MainView2

class BiomarkerTypes(Enum):
    BANDPOWER = 1
    FAA = 2


class BiomarkerEntity:
    type: BiomarkerTypes
    node: Biomarker
    widget: BaseBiomarkerWidget

class BiomarkerManager(QObject):
    nextId = 1
    biomarkers: list[BiomarkerEntity] = []

    def __init__(self, lsl_node: LSLDataSource, view: MainView2):
        self.refresh_rate = int(1000 / 20)
        self.lsl_node = lsl_node
        self.fft = FFT()
        self.fft.psd = [np.empty(1)] * self.lsl_node.channel_count

        self.view = view

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_biomarkers)
        self.timer.start(int(self.refresh_rate))

    def compute_fft(self):
        self.fft.clear()

        for ch in range(self.lsl_node.channel_count):
            freqs, psd = welch(self.lsl_node.buf[:, ch], self.lsl_node.sampling_rate, axis=0, nperseg=int(2.5 * self.lsl_node.sampling_rate))
            self.fft.freqs = freqs
            self.fft.psd.append(psd)

        self.fft.resolution = self.fft.freqs[1] - self.fft.freqs[0]

    def update_biomarkers(self):
        self.compute_fft()
        for entity in self.biomarkers:
            entity.node.compute(self.lsl_node.buf, self.fft)
            entity.widget.update()

    def add_biomarker(self, type: BiomarkerTypes):
        node = None
        widget = None

        match type:
            case BiomarkerTypes.BANDPOWER:
                node = BandpowerBiomarker(self.nextId)
                widget = BandpowerWidget(node)
            case BiomarkerTypes.FAA:
                 raise NotImplemented

        self.nextId += 1

        entity = BiomarkerEntity()
        entity.node = node
        entity.type = type
        entity.widget = widget

        self.biomarkers.append(entity)

        self.view.add_biomarker_widget(entity.widget)


    def remove_biomarker(self, id: int):
        found_idx = -1

        for i, entity in enumerate(self.biomarkers):
            if entity.node.id == id:
                found_idx = i
                break

        if found_idx != -1:
            del self.biomarkers[found_idx]

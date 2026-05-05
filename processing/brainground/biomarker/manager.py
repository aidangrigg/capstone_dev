from PySide6.QtCore import QObject, QTimer
import numpy as np
from scipy.signal import welch
from scipy.integrate import simpson

from brainground.application import BraingroundApplication
from brainground.biomarker.bandpower import BandpowerBiomarker
from brainground.biomarker.base import Biomarker
from brainground.biomarker.types import FFT, BiomarkerType
from brainground.biomarker.asymmetry import AsymmetryBiomarker
from brainground.ui.biomarker.asymmetry_widget import AsymmetryWidget
from brainground.websocket import NeurofeedbackWebsocketServer
from brainground.lsl_datasource import LSLDataSource
from brainground.ui.biomarker.bandpower_widget import BandpowerWidget
from brainground.ui.biomarker.base_widget import BaseBiomarkerWidget
from brainground.ui.view import MainView

class BiomarkerEntity:
    type: BiomarkerType
    node: Biomarker
    widget: BaseBiomarkerWidget

class BiomarkerManager(QObject):
    nextId = 1
    biomarkers: list[BiomarkerEntity] = []

    def __init__(self, lsl_node: LSLDataSource, view: MainView, websocket: NeurofeedbackWebsocketServer):
        self.refresh_rate = int(1000 / 20)
        self.lsl_node = lsl_node
        self.fft = FFT()
        self.fft.psd = [np.empty(1)] * self.lsl_node.channel_count

        self.view = view

        app = BraingroundApplication.get_app()
        app.request_biomarker_added.connect(self.add_biomarker)
        app.request_biomarker_deleted.connect(self.remove_biomarker)

        self.ws = websocket

        self.timer = QTimer()
        self.timer.timeout.connect(self.run)
        self.timer.start(int(self.refresh_rate))

    def compute_fft(self):
        self.fft.clear()

        for ch in range(self.lsl_node.channel_count):
            freqs, psd = welch(self.lsl_node.buf[:, ch], self.lsl_node.sampling_rate, axis=0, nperseg=int(2.5 * self.lsl_node.sampling_rate))
            resolution = freqs[1] - freqs[0]
            self.fft.freqs = freqs
            self.fft.psd.append(psd)
            idxs = np.logical_and(freqs >= 0.0,  freqs <= 45.0)
            total_bandpower = simpson(self.fft.psd[ch][idxs], dx=resolution)
            self.fft.total_bandpower.append(total_bandpower)

        self.fft.resolution = self.fft.freqs[1] - self.fft.freqs[0]

    def send_websocket(self):
        if not self.biomarkers:
            return

        packet = {}

        for entity in self.biomarkers:
            name = entity.node.iden.name()
            delta = entity.node.score
            packet[name] = delta

        self.ws.send_packet(packet)

    def run(self):
        self.compute_fft()

        self.view.set_eeg_plot(self.lsl_node.buf)
        self.view.set_psd_plot(self.fft.freqs, self.fft.psd)

        for entity in self.biomarkers:
            entity.node.compute(self.lsl_node.buf, self.fft)
            entity.widget.update()

        self.send_websocket()

    def add_biomarker(self, type: BiomarkerType, name: str):
        node = None
        widget = None

        match type:
            case BiomarkerType.BANDPOWER:
                node = BandpowerBiomarker(self.nextId, name, type)
                widget = BandpowerWidget(node)
            case BiomarkerType.ASYMMETRY:
                node = AsymmetryBiomarker(self.nextId, name, type)
                widget = AsymmetryWidget(node)

        self.nextId += 1

        entity = BiomarkerEntity()
        entity.node = node
        entity.type = type
        entity.widget = widget

        self.biomarkers.append(entity)
        self.view.add_biomarker_widget(entity.widget)
        BraingroundApplication.get_app().biomarker_added.emit(node.iden)

    def remove_biomarker(self, id: int):
        found_idx = -1

        for i, entity in enumerate(self.biomarkers):
            if entity.node.iden.id() == id:
                found_idx = i
                break

        if found_idx != -1:
            entity = self.biomarkers[found_idx]
            # self.view.remove_biomarker_widget(entity.widget)
            del self.biomarkers[found_idx]
            BraingroundApplication.get_app().biomarker_deleted.emit(entity.node.iden.id())


from PySide6.QtWidgets import QDialog, QRadioButton, QGridLayout, QDialogButtonBox, QButtonGroup, QLabel, QVBoxLayout

from pyqtgraph import BarGraphItem, PlotWidget
from biomarker.bandpower import BandpowerBiomarker, BandpowerSettings
from ui.biomarker.base_widget import BaseBiomarkerWidget

FREQUENCY_BANDS = {
    "Delta": (0.0, 3.0),
    "Theta": (3.0, 7.0),
    "Alpha": (7.0, 12.0),
    "SMR": (12.0, 16.0),
    "Beta": (12.0, 30.0),
    "Gamma": (30.0, 50.0),
}

class BandpowerSettingsDialog(QDialog):
    def __init__(self, old_settings: BandpowerSettings):
        super().__init__()

        self.settings = old_settings
        self.setWindowTitle("Bandpower Settings")

        QBtn = QDialogButtonBox.Apply | QDialogButtonBox.Cancel

        self.freq_button_box = QButtonGroup()
        self.freq_button_layout = QGridLayout()
        i, j = 0, 0
        for band in FREQUENCY_BANDS.keys():
            radio_button = QRadioButton(band)
            self.freq_button_box.addButton(radio_button)
            self.freq_button_layout.addWidget(radio_button, i, j)
            i += 1
            if i >= 2:
                i = 0
                j += 1

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Something happened, is that OK?")
        self.layout.addWidget(message)
        self.layout.addLayout(self.freq_button_layout)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

class BandpowerWidget(BaseBiomarkerWidget):
    def __init__(self, node: BandpowerBiomarker):
        super().__init__(node)

        self.node = node

        # power plot
        plot_widget = PlotWidget()
        self.plot: BarGraphItem = BarGraphItem(x=[], height=[], width=0.8)
        plot_widget.showGrid(x=True, y=True, alpha=0.3)
        plot_widget.setLabels(left="Delta")
        plot_widget.setYRange(-100, 100)
        plot_widget.addItem(self.plot)
        self.layout.addWidget(plot_widget)

    def update(self):
        delta = self.node.score
        self.plot.setOpts(x=[0], height=[delta], brushes=('g' if delta > 0 else 'r'))

    def create_settings_dialog(self):
        dialog = BandpowerSettingsDialog(self.node.settings)

        if dialog.exec_():
            print("it worked")
        else:
            print("it didn't work")



import copy
from PySide6.QtWidgets import QDialog, QDoubleSpinBox, QFormLayout, QRadioButton, QGridLayout, QDialogButtonBox, QButtonGroup, QCheckBox

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

class GridLayout(QGridLayout):
    def __init__(self, columns: int, parent=None):
        super().__init__(parent)
        self.cols = columns
        self.i, self.j = 0, 0

    # TODO: better name for this
    def addWidgetCell(self, widget):
        self.addWidget(widget, self.j, self.i)
        self.i += 1
        if self.i >= self.cols:
            self.i = 0
            self.j += 1

class BandpowerSettingsDialog(QDialog):
    def __init__(self, old_settings: BandpowerSettings):
        super().__init__()

        self.settings = old_settings
        self.setWindowTitle("Bandpower Settings")

        self.form = QFormLayout()

        channel_button_layout = GridLayout(2)
        self.channel_buttons = []
        # TODO: work out a way to pass channel count to here
        for ch in range(4):
            checkbox = QCheckBox(f"{ch + 1}")
            checkbox.clicked.connect(self.channel_button_pressed)

            checkbox.setChecked(ch in old_settings.channels)

            channel_button_layout.addWidgetCell(checkbox)
            self.channel_buttons.append(checkbox)

        self.form.addRow("Channel", channel_button_layout)

        self.freq_button_group = QButtonGroup()
        freq_button_layout = GridLayout(2)
        for band, val in FREQUENCY_BANDS.items():
            radio_button = QRadioButton(band)
            radio_button.clicked.connect(self.freq_button_pressed)

            if val == old_settings.band:
                radio_button.setChecked(True)

            self.freq_button_group.addButton(radio_button)
            freq_button_layout.addWidgetCell(radio_button)


        self.form.addRow("Frequency Band", freq_button_layout)

        baseline_spinbox = QDoubleSpinBox()
        baseline_spinbox.setMinimum(float("-inf"))
        baseline_spinbox.setMaximum(float("inf"))
        baseline_spinbox.setValue(self.settings.baseline)
        baseline_spinbox.valueChanged.connect(self.baseline_value_changed)
        self.form.addRow("Baseline", baseline_spinbox)

        qbtn = QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Save
        self.button_box = QDialogButtonBox(qbtn)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.form.addRow(self.button_box)
        self.setLayout(self.form)

        self.adjustSize()

    def baseline_value_changed(self, val: float):
        self.settings.baseline = val

    def freq_button_pressed(self):
        self.settings.band = FREQUENCY_BANDS[self.freq_button_group.checkedButton().text()]

    def channel_button_pressed(self):
        self.settings.channels = []

        for btn in self.channel_buttons:
            if btn.isChecked():
                self.settings.channels.append(int(btn.text()) - 1)

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
        dialog = BandpowerSettingsDialog(copy.deepcopy(self.node.settings))

        if dialog.exec_():
            self.node.settings = dialog.settings


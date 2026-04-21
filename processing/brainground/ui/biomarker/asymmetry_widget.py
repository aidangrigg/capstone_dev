
from brainground.biomarker.asymmetry import AsymmetrySettings, AsymmetryBiomarker
from brainground.biomarker.types import FrequencyBand
from brainground.ui.biomarker.base_widget import BaseBiomarkerWidget

import copy
from PySide6.QtWidgets import QDialog, QFormLayout, QRadioButton, QGridLayout, QDialogButtonBox, QButtonGroup
from pyqtgraph import BarGraphItem, PlotWidget

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

class AsymmetrySettingsDialog(QDialog):
    def __init__(self, old_settings: AsymmetrySettings):
        super().__init__()

        self.settings = old_settings
        self.setWindowTitle("Bandpower Settings")

        self.form = QFormLayout()

        left_channel_layout = GridLayout(2)
        self.left_channel_buttons = []
        # TODO: work out a way to pass channel count to here
        for ch in range(4):
            checkbox = QRadioButton(f"{ch + 1}")
            checkbox.clicked.connect(self.left_channel_changed)

            checkbox.setChecked(ch == old_settings.left_channel)

            left_channel_layout.addWidgetCell(checkbox)
            self.left_channel_buttons.append(checkbox)

        self.form.addRow("Left Channel", left_channel_layout)

        right_channel_layout = GridLayout(2)
        self.right_channel_buttons = []
        # TODO: work out a way to pass channel count to here
        for ch in range(4):
            checkbox = QRadioButton(f"{ch + 1}")
            checkbox.clicked.connect(self.right_channel_changed)

            checkbox.setChecked(ch == old_settings.right_channel)

            right_channel_layout.addWidgetCell(checkbox)
            self.right_channel_buttons.append(checkbox)

        self.form.addRow("Right Channel", right_channel_layout)

        self.freq_button_group = QButtonGroup()
        freq_button_layout = GridLayout(2)
        for band in FrequencyBand:
            radio_button = QRadioButton(band.name.capitalize())
            radio_button.clicked.connect(self.freq_button_pressed)

            if band == old_settings.band:
                radio_button.setChecked(True)

            self.freq_button_group.addButton(radio_button)
            freq_button_layout.addWidgetCell(radio_button)


        self.form.addRow("Frequency Band", freq_button_layout)


        qbtn = QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Save
        self.button_box = QDialogButtonBox(qbtn)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.form.addRow(self.button_box)
        self.setLayout(self.form)

        self.adjustSize()

    def left_channel_changed(self):
        for btn in self.left_channel_buttons:
            if btn.isChecked():
                self.settings.left_channel = int(btn.text()) - 1

    def right_channel_changed(self):
        for btn in self.right_channel_buttons:
            if btn.isChecked():
                self.settings.right_channel = int(btn.text()) - 1

    def freq_button_pressed(self):
        for band in FrequencyBand:
            if band.name.lower() == self.freq_button_group.checkedButton().text().lower():
                self.settings.band = band
                return

class AsymmetryWidget(BaseBiomarkerWidget):
    def __init__(self, node: AsymmetryBiomarker):
        super().__init__(node)

        self.node = node

        # power plot
        plot_widget = PlotWidget()
        self.plot: BarGraphItem = BarGraphItem(x0=0, height=0.8, width=[], y=[])
        plot_widget.showGrid(x=True, y=True, alpha=0.3)
        plot_widget.setLabels(bottom="FAA Score")
        plot_widget.setXRange(-100, 100)
        plot_widget.addItem(self.plot)
        self.layout.addWidget(plot_widget)

        ax = plot_widget.getAxis("left")
        ax.setTicks([[]])

    def update(self):
        delta = self.node.score
        self.plot.setOpts(y=[0], width=[delta], brushes=('g' if delta > 0 else 'r'))

    def create_settings_dialog(self):
        dialog = AsymmetrySettingsDialog(copy.deepcopy(self.node.settings))

        if dialog.exec_():
            self.node.settings = dialog.settings


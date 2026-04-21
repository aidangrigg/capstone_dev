from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QMainWindow, QVBoxLayout, QWidget
import numpy as np
from pyqtgraph import PlotWidget

from brainground.application import BraingroundApplication
from brainground.biomarker.base import BiomarkerIdentifier
from brainground.ui.sidebar import Sidebar
from brainground.ui.biomarker.base_widget import BaseBiomarkerWidget

AMPLITUDE_LIMIT = 100

class MainView(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Brainground Neurofeedback Processing")
        container = QWidget()
        layout = QHBoxLayout(container)
        self.setCentralWidget(container)

        self.channel_count = 4
        self.time_window = 10
        self.sampling_rate = 250

        plot_layout = QVBoxLayout()

        # Voltage plot (leftmost, plots mV/t)
        voltage_widget: PlotWidget = PlotWidget()
        self.voltage_plot: PlotItem = voltage_widget.getPlotItem() # type: ignore
        self.voltage_plot.showGrid(x=True, y=True, alpha=0.3)
        self.voltage_plot.setLabels(left="Channels", bottom="Time (s)")
        self.voltage_plot.getViewBox().setMouseEnabled(x=False, y=False) # type: ignore
        self.voltage_plot.setYRange(0, self.channel_count)
        self.voltage_plot.setXRange(-self.time_window, 0)
        self.voltage_plot.getAxis("left").setTicks(
            [
                [
                    (self.channel_count - i - 0.5, f"CH{i + 1}")
                    for i in range(self.channel_count)
                ]
            ]
        )
        plot_layout.addWidget(voltage_widget)

        # PSD plot (center, plots (V^2/Hz))
        psd_widget = PlotWidget()
        self.psd_plot: PlotItem = psd_widget.getPlotItem() # type: ignore
        self.psd_plot.showGrid(x=True, y=True, alpha=0.3)
        self.psd_plot.setLabels(left="Power spectral density (V^2 / Hz)", bottom="frequency (Hz)")
        self.psd_plot.getViewBox().setMouseEnabled(x=False, y=False) # type: ignore
        self.psd_plot.setLimits(xMin=1, xMax=40, yMin=0, yMax=500) # type: ignore
        plot_layout.addWidget(psd_widget)
        layout.addLayout(plot_layout, 45)

        # Colour code each individual channel
        self.colors = "rgbycmwr"
        self.time_domain_curves = []
        self.freq_domain_curves = []
        for i in range(self.channel_count):
            # Each channel gets its own colored curve
            self.freq_domain_curves.append(
                self.psd_plot.plot(
                    pen=self.colors[i], width=1
                )
            )
            self.time_domain_curves.append(
                self.voltage_plot.plot(
                    pen=self.colors[i], width=1
                )
            )


        self.biomarkers_widget = QWidget()
        self.biomarkers_layout = QGridLayout(self.biomarkers_widget)
        layout.addWidget(self.biomarkers_widget, 45)

        self.biomarker_plots = {}

        self.sidebar = Sidebar()
        layout.addWidget(self.sidebar, 10)

        self.grid_idx = [0, 0]

        self.t_vec = np.arange(-self.time_window * self.sampling_rate, 0) / self.sampling_rate

        BraingroundApplication.instance().biomarker_deleted.connect(self.remove_biomarker_widget)

    def set_eeg_plot(self, data):
        for ch, curve in enumerate(self.time_domain_curves):
            offset = self.channel_count - ch - 0.5
            curve.setData(
                self.t_vec, data[:, ch] / AMPLITUDE_LIMIT / 2 + offset
            )

    def set_psd_plot(self, freqs, psd):
        for ch, curve in enumerate(self.freq_domain_curves):
            curve.setData(freqs, psd[ch])

    def remove_biomarker_widget(self, id: int):
        if id not in self.biomarker_plots:
            return

        widget = self.biomarker_plots[id]

        self.biomarkers_layout.removeWidget(widget.base_widget)
        widget.base_widget.setParent(None)
        self.biomarkers_layout.invalidate()
        self.biomarkers_layout.activate()

    def add_biomarker_widget(self, widget: BaseBiomarkerWidget):
        self.biomarker_plots[widget.id()] = widget

        self.biomarkers_layout.addWidget(widget.base_widget, self.grid_idx[0], self.grid_idx[1])
        self.grid_idx[1] += 1

        if self.grid_idx[1] >= 2:
            self.grid_idx[0] += 1
            self.grid_idx[1] = 0


import numpy as np

from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import Signal
from pyqtgraph import PlotWidget, PlotItem, BarGraphItem
from ui.channel_checkbox import Channel
from ui.freq_band_checkbox import FrequencyBand

AMPLITUDE_LIMIT = 100

class MainView(QMainWindow):
    active_bands_set = Signal(list)
    active_channels_set = Signal(list)
    compute_new_average = Signal()

    def __init__(self, channel_count: int, time_window: int, sampling_rate: float):
        super().__init__()

        self.channel_count = channel_count
        self.time_window = time_window
        self.sampling_rate = sampling_rate

        self.setWindowTitle("LSL Time Series Scope")
        container = QWidget()
        layout = QHBoxLayout(container)
        self.setCentralWidget(container)

        # Voltage plot (leftmost, plots mV/t)
        voltage_widget: PlotWidget = PlotWidget()
        self.voltage_plot: PlotItem = voltage_widget.getPlotItem() # type: ignore
        self.voltage_plot.showGrid(x=True, y=True, alpha=0.3)
        self.voltage_plot.setLabels(left="Channels", bottom="Time (s)")
        self.voltage_plot.getViewBox().setMouseEnabled(x=False, y=False) # type: ignore
        self.voltage_plot.setYRange(0, channel_count) # type: ignore
        self.voltage_plot.setXRange(0, self.time_window) # type: ignore
        self.voltage_plot.getAxis("left").setTicks(
            [
                [
                    (channel_count - i - 0.5, f"CH{i + 1}")
                    for i in range(channel_count)
                ]
            ]
        )
        layout.addWidget(voltage_widget)

        middle_plot = QWidget()
        psd_layout = QVBoxLayout(middle_plot)
        layout.addWidget(middle_plot)

        # PSD plot (center, plots (V^2/Hz))
        psd_widget = PlotWidget()
        self.psd_plot: PlotItem = psd_widget.getPlotItem() # type: ignore
        self.psd_plot.showGrid(x=True, y=True, alpha=0.3)
        self.psd_plot.setLabels(left="Power spectral density (V^2 / Hz)", bottom="frequency (Hz)")
        self.psd_plot.getViewBox().setMouseEnabled(x=False, y=False) # type: ignore
        self.psd_plot.setLimits(xMin=1, xMax=40, yMin=0, yMax=500) # type: ignore
        psd_layout.addWidget(psd_widget)

        # power plot
        self.power_widget = PlotWidget()
        self.power_plot: BarGraphItem = BarGraphItem(x=[], height=[], width=0.8)
        self.power_plot_ticks: list[str] = []
        self.power_widget.showGrid(x=True, y=True, alpha=0.3)
        self.power_widget.setLabels(left="Power delta (uV)", bottom="Frequency band")
        self.power_widget.setYRange(-100, 100)
        # self.power_widget.setLimits(yMin=-1, yMax=1)
        self.power_widget.addItem(self.power_plot)
        psd_layout.addWidget(self.power_widget)

        # Colour code each individual channel
        self.colors = "rgbycmwr"
        self.time_domain_curves = []
        self.freq_domain_curves = []
        for i in range(self.channel_count):
            # Each channel gets its own colored curve
            self.freq_domain_curves.append(
                self.psd_plot.plot( # type: ignore
                    pen=self.colors[i], width=1
                )
            )
            self.time_domain_curves.append(
                self.voltage_plot.plot(
                    pen=self.colors[i], width=1
                )
            )

        controls = QWidget()
        controls_layout = QVBoxLayout(controls)
        layout.addWidget(controls)

        self.frequency_bands = [
            FrequencyBand("Delta", 0, 3),
            FrequencyBand("Theta", 3, 7),
            FrequencyBand("Alpha", 7, 12),
            FrequencyBand("SMR", 12, 16),
            FrequencyBand("Beta", 12, 30),
            FrequencyBand("Gamma", 30, 50),
        ]

        frequency_checkbox_label = QLabel("Neurofeedback Frequency Bands")
        frequency_checkbox_label.setStyleSheet("font-weight: bold")
        controls_layout.addWidget(frequency_checkbox_label)

        for band in self.frequency_bands:
            controls_layout.addWidget(band)
            band.stateChanged.connect(self.active_bands_changed)

        self.channels = [
            Channel(i + 1) for i in range(self.channel_count)
        ]

        channel_label = QLabel("Active Channels")
        channel_label.setStyleSheet("font-weight: bold")
        controls_layout.addWidget(channel_label)

        for channel in self.channels:
            controls_layout.addWidget(channel)
            channel.stateChanged.connect(self.active_channels_changed)

        avg_button = QPushButton("Compute average... (takes 5s)")
        avg_button.clicked.connect(self.on_avg_button_pressed)
        controls_layout.addWidget(avg_button)

        self.avg_label: QLabel = QLabel()
        controls_layout.addWidget(self.avg_label)

        controls_layout.addStretch()

        self.t_vec = np.arange(self.time_window * self.sampling_rate) / self.sampling_rate

    def on_avg_button_pressed(self):
        self.compute_new_average.emit()
        self.avg_label.setText("computing average...")

    def active_bands_changed(self):
        self.active_bands_set.emit(list(map(lambda x: x.isChecked(), self.frequency_bands)))

    def active_channels_changed(self):
        self.active_channels_set.emit(list(map(lambda x: x.isChecked(), self.channels)))

    def set_eeg_plot(self, data):
        t_disp = self.t_vec[:]
        for ch, curve in enumerate(self.time_domain_curves):
            if not self.channels[ch].isChecked():
                curve.setData([], [])
                continue
            offset = self.channel_count - ch - 0.5
            curve.setData(
                t_disp, data[:, ch] / AMPLITUDE_LIMIT / 2 + offset
            )

    def set_psd_plot(self, freqs, psd):
        for ch, curve in enumerate(self.freq_domain_curves):
            if self.channels[ch].isChecked():
                curve.setData(freqs, psd[ch])
            else:
                curve.setData([], [])

    def set_bandpower_delta_plot(self, delta: float):
        self.avg_label.setText(f"Value = {delta}")
        self.power_plot.setOpts(x=[0], height=[delta], brushes=('g' if delta > 0 else 'r'))

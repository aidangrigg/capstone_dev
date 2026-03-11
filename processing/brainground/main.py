import os
os.environ["PYQTGRAPH_QT_LIB"] = "PySide6"

import numpy as np
import pyqtgraph as pg

from presenter import Presenter
from processing import NeurofeedbackProcessing
from view import MainView
# from brainground.view.freq_band_checkbox import FrequencyBand
# from brainground.view.channel_checkbox import Channel

from PySide6 import QtWidgets, QtCore
from lsl_datasource import LSLDataSource
from collections import deque
from scipy.integrate import simpson
import sys

TIME_WINDOW = 10
AMPLITUDE_LIMIT = 100

# class LSLTimeScope(QtWidgets.QMainWindow):
#     """Real-time LSL data visualization widget with multi-channel display."""

#     def __init__(self):
#         super().__init__()

#         self.datasource: LSLDataSource = LSLDataSource(TIME_WINDOW)
#         streams = self.datasource.get_streams()
#         self.datasource.connect(streams[0])

#         self.setWindowTitle("LSL Time Series Scope")
#         container = QtWidgets.QWidget()
#         layout = QtWidgets.QHBoxLayout(container)
#         self.setCentralWidget(container)

#         # Voltage plot (leftmost, plots mV/t)
#         voltage_widget = pg.PlotWidget()
#         self.voltage_plot = voltage_widget.getPlotItem()
#         self.voltage_plot.showGrid(x=True, y=True, alpha=0.3)
#         self.voltage_plot.getViewBox().setMouseEnabled(x=False, y=False)
#         self.voltage_plot.setLabels(left="Channels", bottom="Time (s)")
#         self.voltage_plot.setYRange(0, self.datasource.channel_count)
#         self.voltage_plot.getAxis("left").setTicks(
#             [
#                 [
#                     (self.datasource.channel_count - i - 0.5, f"CH{i + 1}")
#                     for i in range(self.datasource.channel_count)
#                 ]
#             ]
#         )
#         self.voltage_plot.setXRange(0, TIME_WINDOW)
#         layout.addWidget(voltage_widget)

#         middle_plot = QtWidgets.QWidget()
#         psd_layout = QtWidgets.QVBoxLayout(middle_plot)
#         layout.addWidget(middle_plot)

#         # PSD plot (center, plots (V^2/Hz))
#         psd_widget = pg.PlotWidget()
#         self.psd_plot = psd_widget.getPlotItem()
#         self.psd_plot.showGrid(x=True, y=True, alpha=0.3)
#         self.psd_plot.getViewBox().setMouseEnabled(x=False, y=False)
#         self.psd_plot.setLabels(left="Power spectral density (V^2 / Hz)", bottom="frequency (Hz)")
#         self.psd_plot.setLimits(xMin=1, xMax=40, yMin=0, yMax=500)
#         psd_layout.addWidget(psd_widget)

#         # power plot
#         self.power_widget = pg.PlotWidget()
#         self.power_plot: pg.BarGraphItem = pg.BarGraphItem(x=[], height=[], width=0.8)
#         self.power_plot_ticks: list[str] = []
#         self.power_widget.showGrid(x=True, y=True, alpha=0.3)
#         self.power_widget.setLabels(left="Power delta (uV)", bottom="Frequency band")
#         self.power_widget.setYRange(-100, 100)
#         # self.power_widget.setLimits(yMin=-1, yMax=1)
#         self.power_widget.addItem(self.power_plot)
#         psd_layout.addWidget(self.power_widget)

#         # Colour code each individual channel
#         self.colors = "rgbycmwr"
#         self.time_domain_curves = []
#         self.freq_domain_curves = []
#         for i in range(self.datasource.channel_count):
#             # Each channel gets its own colored curve
#             self.freq_domain_curves.append(
#                 self.psd_plot.plot(
#                     pen=self.colors[i], width=1
#                 )
#             )
#             self.time_domain_curves.append(
#                 self.voltage_plot.plot(
#                     pen=self.colors[i], width=1
#                 )
#             )

#         controls = QtWidgets.QWidget()
#         controls_layout = QtWidgets.QVBoxLayout(controls)
#         layout.addWidget(controls)

#         self.frequency_bands = [
#             FrequencyBand("Delta", 0, 3),
#             FrequencyBand("Theta", 3, 7),
#             FrequencyBand("Alpha", 7, 12),
#             FrequencyBand("SMR", 12, 16),
#             FrequencyBand("Beta", 12, 30),
#             FrequencyBand("Gamma", 30, 50),
#         ]

#         frequency_checkbox_label = QtWidgets.QLabel("Neurofeedback Frequency Bands")
#         frequency_checkbox_label.setStyleSheet("font-weight: bold")
#         controls_layout.addWidget(frequency_checkbox_label)

#         for band in self.frequency_bands:
#             controls_layout.addWidget(band)

#         self.channels = [
#             Channel(i + 1) for i in range(self.datasource.channel_count)
#         ]

#         channel_label = QtWidgets.QLabel("Active Channels")
#         channel_label.setStyleSheet("font-weight: bold")
#         controls_layout.addWidget(channel_label)

#         for channel in self.channels:
#             controls_layout.addWidget(channel.checkbox)

#         avg_button = QtWidgets.QPushButton("Compute average... (takes 5s)")
#         avg_button.clicked.connect(self.avg_button_on_click)
#         controls_layout.addWidget(avg_button)

#         self.avg_label: QtWidgets.QLabel = QtWidgets.QLabel()
#         controls_layout.addWidget(self.avg_label)

#         controls_layout.addStretch()

#         self.t_vec = np.arange(TIME_WINDOW * self.datasource.sampling_rate) / self.datasource.sampling_rate
#         self.computing_average: bool = False
#         self.update_rate = int(1000 / 20)
#         AVG_TIME_WINDOW = 5 # seconds
#         self.psd_recent_readings: list[list[float]] = []
#         self.psd_max_readings = (AVG_TIME_WINDOW * 1000) // self.update_rate
#         self.psd_avg = np.array((self.datasource.channel_count))
#         self.psd_avg_computed = False

#         self.timer = QtCore.QTimer()
#         self.timer.timeout.connect(self.update_plot)
#         self.timer.start(self.update_rate)

#     def set_avg_label(self):
#         label_text = "Averages:\n"

#         for i, band in enumerate(self.frequency_bands):
#             label_text += f"{band.name}: "
#             if self.psd_avg_computed:
#                 label_text += f"\t{self.psd_avg[i]: .2f}uV\n"
#             else:
#                 label_text += "\tNot calculated\n"

#         self.avg_label.setText(label_text)

#     def avg_button_on_click(self):
#         self.computing_average = True
#         self.psd_recent_readings = []
#         self.psd_avg_computed = False

#     def get_current_avg_power_per_band(self):
#         psd_values = [[] for _ in range(len(self.freq_domain_curves))]
#         for ch, curve in enumerate(self.freq_domain_curves):
#             freqs, psd = self.datasource.welch(ch)
#             freq_res = freqs[1] - freqs[0]

#             if self.channels[ch].active:
#                 curve.setData(freqs, psd)
#             else:
#                 curve.setData([], [])

#             for band in self.frequency_bands:
#                 idxs = np.logical_and(freqs >= band.start, freqs <= band.end)
#                 bp = simpson(psd[idxs], dx=freq_res)
#                 psd_values[ch].append(bp)

#         psd_values = np.array(psd_values).transpose()

#         arr = []
#         for channels in psd_values:
#             power_in_band = []
#             for ch, power in enumerate(channels):
#                 if self.channels[ch].active:
#                     power_in_band.append(power)

#             arr.append(np.mean(power_in_band))

#         return arr

#     def update_plot(self):
#         """
#         Update function for pyqtgraph. Pulls in any available samples from the LSL stream,
#         filters and processes them, and then updates the graph.
#         """
#         self.set_avg_label()
#         new_samples = self.datasource.pull_samples()
#         # print(f"Read in {new_samples} samples.")

#         # Obtain the PSD using welch's method and graph the values
#         # queue [[band, band, band (average across active channels)]]
#         # [ ch1: [delta: 0.1, alpha: 0.2], ch2: []]
#         power_per_band = self.get_current_avg_power_per_band()
#         if self.computing_average:
#             self.psd_recent_readings.append(power_per_band)

#             if len(self.psd_recent_readings) >= self.psd_max_readings:
#                 print(self.psd_max_readings)
#                 self.computing_average = False
#                 self.psd_avg = np.array([
#                     np.mean(np.array(self.psd_recent_readings)[:, i]) for i in range(len(self.frequency_bands))
#                 ])
#                 self.psd_avg_computed = True

#         # if self.psd_avg_computed:
#         #     power_plot_values = []
#         #     power_plot_ticks = []
#         #     power_plot_brushes = []
#         #     for i, band in enumerate(self.frequency_bands):
#         #         if not band.active:
#         #             continue

#         #         delta =  power_per_band[i] - self.psd_avg[i]
#         #         power_plot_values.append(delta)
#         #         power_plot_ticks.append(band.name)
#         #         power_plot_brushes.append('g' if delta > 0 else 'r')

#         #     if len(power_plot_values) > 0:
#         #         idxs = list(range(len(power_plot_values)))
#         #         self.power_plot.setOpts(x=idxs, height=power_plot_values, brushes=power_plot_brushes)

#         #         if len(self.power_plot_ticks) != len(power_plot_ticks):
#         #             ticks = list(zip(idxs, power_plot_ticks))
#         #             self.power_widget.getAxis("bottom").setTicks([ticks])
#         #             self.power_plot_ticks = power_plot_ticks

#         # Plot the reading
#         t_disp = self.t_vec[:]
#         for ch, curve in enumerate(self.time_domain_curves):
#             if not self.channels[ch].active:
#                 curve.setData([], [])
#                 continue
#             offset = self.datasource.channel_count - ch - 0.5
#             curve.setData(
#                 t_disp, self.datasource.buf[:, ch] / AMPLITUDE_LIMIT / 2 + offset
#             )

#         # # Update the ticks on the X axis
#         # offset = (self.sample_index // MAX_POINTS) * TIME_WINDOW
#         # if self.tick_offset != offset:
#         #     ticks = [(i, f"{i + offset}") for i in range(int(np.floor(TIME_WINDOW)) + 1)]
#         #     self.voltage_plot.getAxis("bottom").setTicks([ticks])
#         #     self.tick_offset = offset

if __name__ == "__main__":
    # Create Qt application and LSL visualization window
    # app = QtWidgets.QApplication(sys.argv)
    # window = LSLTimeScope()
    # window.resize(1000, 500)
    # window.show()
    # sys.exit(app.exec())

    app = QtWidgets.QApplication(sys.argv)
    lsl_node = LSLDataSource()
    nf_processing = NeurofeedbackProcessing()
    lsl_node.samples_recieved.connect(nf_processing.update_buffer)
    view = MainView(8, 10, 250)

    presenter = Presenter(view, nf_processing)
    view.show()
    sys.exit(app.exec())


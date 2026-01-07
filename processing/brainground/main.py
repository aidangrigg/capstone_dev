import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore
# from scipy.signal import butter, iirnotch, lfilter, lfilter_zi, sosfilt, sosfilt_zi, welch
from lsl_datasource import LSLDataSource
import sys

TIME_WINDOW = 2.5
AMPLITUDE_LIMIT = 100

FREQ_BANDS = {
    "delta": {
        "start": 0,
        "end": 3,
    },
    "theta": {
        "start": 3,
        "end": 7,
    },
    "alpha": {
        "start": 7,
        "end": 12,
    },
    "smr": {
        "start": 12,
        "end": 16,
    },
    "beta": {
        "start": 12,
        "end": 30,
    },
    "gamma": {
        "start": 30,
        "end": 50,
    },
}

class LSLTimeScope(QtWidgets.QMainWindow):
    """Real-time LSL data visualization widget with multi-channel display."""

    def __init__(self):
        super().__init__()

        self.datasource = LSLDataSource(TIME_WINDOW)
        streams = self.datasource.get_streams()
        self.datasource.connect(streams[0])

        self.setWindowTitle("LSL Time Series Scope")
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        self.setCentralWidget(container)

        # Voltage plot (leftmost, plots mV/t)
        voltage_widget = pg.PlotWidget()
        self.voltage_plot = voltage_widget.getPlotItem()
        self.voltage_plot.showGrid(x=True, y=True, alpha=0.3)
        self.voltage_plot.getViewBox().setMouseEnabled(x=False, y=False)
        self.voltage_plot.setLabels(left="Channels", bottom="Time (s)")
        self.voltage_plot.setYRange(0, self.datasource.channel_count)
        self.voltage_plot.getAxis("left").setTicks(
            [
                [
                    (self.datasource.channel_count - i - 0.5, f"CH{i + 1}")
                    for i in range(self.datasource.channel_count)
                ]
            ]
        )
        self.voltage_plot.setXRange(0, TIME_WINDOW)
        layout.addWidget(voltage_widget)

        # PSD plot (center, plots (V**2/something) vs f
        psd_widget = pg.PlotWidget()
        self.psd_plot = psd_widget.getPlotItem()
        self.psd_plot.showGrid(x=True, y=True, alpha=0.3)
        self.psd_plot.getViewBox().setMouseEnabled(x=False, y=False)
        self.psd_plot.setLabels(left="PSD", bottom="frequency [Hz]")
        self.psd_plot.setLimits(xMin=1, xMax=40, yMin=0, yMax=1e7)
        layout.addWidget(psd_widget)

        # Colour code each individual channel
        self.colors = "rgbycmwr"
        self.time_domain_curves = []
        self.freq_domain_curves = []
        for i in range(self.datasource.channel_count):
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

        controls = QtWidgets.QWidget()
        controls_layout = QtWidgets.QVBoxLayout(controls)
        layout.addWidget(controls)
        self.frequency_band_checkboxes = [
            QtWidgets.QCheckBox(band) for band in FREQ_BANDS.keys()
        ]

        for checkbox in self.frequency_band_checkboxes:
            controls_layout.addWidget(checkbox)

        self.t_vec = np.arange(TIME_WINDOW * self.datasource.sampling_rate) / self.datasource.sampling_rate

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(int(1000 / 20))

    def update_plot(self):
        """
        Update function for pyqtgraph. Pulls in any available samples from the LSL stream,
        filters and processes them, and then updates the graph.
        """
        new_samples = self.datasource.pull_samples()
        print(f"Read in {new_samples} samples.")

        # Obtain the PSD using welch's method and graph the values
        for ch, curve in enumerate(self.freq_domain_curves):
            freqs, psd = self.datasource.welch(ch)
            curve.setData(freqs, psd)

            # TODO: Graph this rather than printing to the terminal
            print(f"Ch {ch}: ", end='')
            for band, val in FREQ_BANDS.items():
                psd_values = []
                for f_idx in range(len(freqs)):
                    freq = freqs[f_idx]
                    if freq > val["end"] :
                        break
                    if freq > val["start"]:
                        psd_values.append(psd[f_idx])

                print(f"[{band}]: {np.mean(psd_values)} ", end='\t\n')

            print()

        # Plot the reading
        t_disp = self.t_vec[:]
        for i, curve in enumerate(self.time_domain_curves):
            offset = self.datasource.channel_count - i - 0.5
            curve.setData(
                t_disp, self.datasource.buf[:, i] / AMPLITUDE_LIMIT / 2 + offset
            )

        # # Update the ticks on the X axis
        # offset = (self.sample_index // MAX_POINTS) * TIME_WINDOW
        # if self.tick_offset != offset:
        #     ticks = [(i, f"{i + offset}") for i in range(int(np.floor(TIME_WINDOW)) + 1)]
        #     self.voltage_plot.getAxis("bottom").setTicks([ticks])
        #     self.tick_offset = offset

if __name__ == "__main__":
    # Create Qt application and LSL visualization window
    app = QtWidgets.QApplication(sys.argv)
    window = LSLTimeScope()
    window.resize(1000, 500)
    window.show()
    sys.exit(app.exec())

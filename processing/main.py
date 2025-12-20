import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore
from pylsl import StreamInlet, resolve_byprop
from scipy.signal import butter, iirnotch, lfilter, lfilter_zi, sosfilt, sosfilt_zi, welch
import sys

SAMPLING_RATE = 250
TIME_WINDOW = 10
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

MAX_POINTS = int(TIME_WINDOW * SAMPLING_RATE)

class LSLTimeScope(QtWidgets.QMainWindow):
    """Real-time LSL data visualization widget with multi-channel display."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LSL Time Series Scope")

        # Create container widget for multiple plots
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)

        # Create two independent plots
        self.plot_widget_left: pg.PlotWidget = pg.PlotWidget()
        self.plot_widget_right: pg.PlotWidget = pg.PlotWidget()

        # Add both plots to the layout
        layout.addWidget(self.plot_widget_left)
        layout.addWidget(self.plot_widget_right)

        self.setCentralWidget(container)

        self.left_plot_item = self.plot_widget_left.getPlotItem()
        self.left_plot_item.showGrid(x=True, y=True, alpha=0.3)
        self.left_plot_item.getViewBox().setMouseEnabled(x=False, y=False)

        self.right_plot_item = self.plot_widget_right.getPlotItem()
        self.right_plot_item.showGrid(x=True, y=True, alpha=0.3)
        self.right_plot_item.getViewBox().setMouseEnabled(x=False, y=False)

        # Connect to LSL stream
        print("Resolving LSL stream...")
        streams = resolve_byprop("type", "EEG")
        self.inlet = StreamInlet(streams[0])
        info = self.inlet.info()
        self.CHANNEL_COUNT = info.channel_count()

        # Configure plot layout and styling
        self.left_plot_item.setLabels(left="Channels", bottom="Time (s)")
        self.left_plot_item.setYRange(0, self.CHANNEL_COUNT)

        self.right_plot_item.setLabels(left="PSD", bottom="frequency [Hz]")
        self.right_plot_item.setLimits(xMin=1, xMax=40, yMin=0, yMax=1e7)

        # Create channel labels (CH1, CH2, etc.) on Y-axis
        self.left_plot_item.getAxis("left").setTicks(
            [
                [
                    (self.CHANNEL_COUNT - i - 0.5, f"CH{i + 1}")
                    for i in range(self.CHANNEL_COUNT)
                ]
            ]
        )
        self.left_plot_item.setXRange(-0.5, TIME_WINDOW + 0.5)  # Time axis range

        # Create individual plot curves for each channel
        self.colors = "rgbycmwr"
        self.time_domain_curves = []
        self.freq_domain_curves = []
        for i in range(self.CHANNEL_COUNT):
            # Each channel gets its own colored curve
            self.freq_domain_curves.append(
                self.right_plot_item.plot(
                    pen=self.colors[i], width=1
                )
            )
            self.time_domain_curves.append(
                self.left_plot_item.plot(
                    pen=self.colors[i], width=1
                )
            )

        self.t_vec = np.arange(MAX_POINTS) / SAMPLING_RATE
        self.raw_buffer = np.zeros((MAX_POINTS, self.CHANNEL_COUNT))
        self.filtered_buffer = np.zeros((MAX_POINTS, self.CHANNEL_COUNT))
        self.sample_index = 0
        self.tick_offset = -1

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(int(1000 / 20))

        # filters
        nyq = 0.5 * SAMPLING_RATE
        self.sos = butter(6, [1 / nyq, 30 / nyq], btype='band', output='sos') # bandpass: 1-30Hz, 6th order (potentially drop this)
        self.bandpass = {
            "zi": [sosfilt_zi(self.sos) * [0] for ch in range(self.CHANNEL_COUNT)]
        }

        n_b, n_a = iirnotch(50, 30, SAMPLING_RATE) # 50Hz notch filter
        self.notch = {
            "b": n_b,
            "a": n_a,
            "zi": [lfilter_zi(n_b, n_a) for ch in range(self.CHANNEL_COUNT)]
        }

    def notch_frame(self, frame):
        """Applies a 50Hz notch filter to the passed in frame"""
        filtered = frame
        for ch in range(self.CHANNEL_COUNT):
            y, zi = lfilter(self.notch["b"], self.notch["a"], [frame[0][ch]], zi=self.notch["zi"][ch])
            filtered[0][ch] = y[0]
            self.notch["zi"][ch] = zi
        return frame

    def bandpass_frame(self, frame):
        """Applies a 1-30Hz bandpass filter to the passed in frame"""
        bandpassed = frame
        for ch in range(self.CHANNEL_COUNT):
            y, zi  = sosfilt(self.sos, [frame[0][ch]], zi=self.bandpass["zi"][ch])
            bandpassed[0][ch] = y[0]
            self.bandpass["zi"][ch] = zi

        return bandpassed

    def update_plot(self):
        """
        Update function for pyqtgraph. Pulls in any available samples from the LSL stream,
        filters and processes them, and then updates the graph.
        """
        # Pull in all new samples from the LSL stream
        idx = self.sample_index % MAX_POINTS
        sample, timestamp = self.inlet.pull_sample(timeout=0.0)
        while sample is not None:
            frame = np.array(sample, dtype=np.float64).reshape((1, self.CHANNEL_COUNT))
            idx = self.sample_index % MAX_POINTS
            self.sample_index += 1
            self.raw_buffer[idx, :] = frame

            # Filter the newly obtained data
            filtered_frame = self.notch_frame(frame)
            filtered_frame = self.bandpass_frame(filtered_frame)
            self.filtered_buffer[idx, :] = filtered_frame

            sample, timestamp = self.inlet.pull_sample(timeout=0.0) # pull another sample

        # Obtain the PSD using welch's method and graph the values
        for ch, curve in enumerate(self.freq_domain_curves):
            freqs, psd = welch(self.filtered_buffer[:, ch], SAMPLING_RATE, axis=0)
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
            offset = self.CHANNEL_COUNT - i - 0.5
            curve.setData(
                t_disp, self.filtered_buffer[:, i] / AMPLITUDE_LIMIT / 2 + offset
            )

        # Update the ticks on the X axis
        offset = (self.sample_index // MAX_POINTS) * TIME_WINDOW
        if self.tick_offset != offset:
            ticks = [(i, f"{i + offset}") for i in range(int(np.floor(TIME_WINDOW)) + 1)]
            self.left_plot_item.getAxis("bottom").setTicks([ticks])
            self.tick_offset = offset

if __name__ == "__main__":
    # Create Qt application and LSL visualization window
    app = QtWidgets.QApplication(sys.argv)
    window = LSLTimeScope()
    window.resize(1000, 500)  # Set reasonable window size
    window.show()
    sys.exit(app.exec())  # Start Qt event loop

from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QMainWindow, QWidget
from pyqtgraph import PlotWidget

from ui.biomarker.base_widget import BaseBiomarkerWidget


class MainView2(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Brainground Neurofeedback Processing")
        container = QWidget()
        layout = QHBoxLayout(container)
        self.setCentralWidget(container)

        # Voltage plot (leftmost, plots mV/t)
        voltage_widget: PlotWidget = PlotWidget()
        self.voltage_plot: PlotItem = voltage_widget.getPlotItem() # type: ignore
        self.voltage_plot.showGrid(x=True, y=True, alpha=0.3)
        self.voltage_plot.setLabels(left="Channels", bottom="Time (s)")
        self.voltage_plot.getViewBox().setMouseEnabled(x=False, y=False) # type: ignore
        self.voltage_plot.setYRange(0, 4) # TODO: channel count
        self.voltage_plot.setXRange(0, 10) # TODO: time window
        self.voltage_plot.getAxis("left").setTicks(
            [
                [
                    (4 - i - 0.5, f"CH{i + 1}") # this is hardcoded to 4 channels
                    for i in range(4)
                ]
            ]
        )
        layout.addWidget(voltage_widget)

        self.biomarkers_widget = QWidget()
        self.biomarkers_layout = QGridLayout(self.biomarkers_widget)
        layout.addWidget(self.biomarkers_widget)

        self.grid_idx = [0, 0]


    def add_biomarker_widget(self, widget: BaseBiomarkerWidget):
        self.biomarkers_layout.addWidget(widget.base_widget, self.grid_idx[0], self.grid_idx[1])
        self.grid_idx[1] += 1

        if self.grid_idx[1] >= 2:
            self.grid_idx[0] += 1
            self.grid_idx[1] = 0




from pyqtgraph import BarGraphItem, PlotWidget
from biomarker.bandpower import BandpowerBiomarker
from ui.biomarker.base_widget import BaseBiomarkerWidget


class BandpowerWidget(BaseBiomarkerWidget):
    def __init__(self, node: BandpowerBiomarker):
        super().__init__(node)

        self.node = node

        # power plot
        self.widget = PlotWidget()
        self.plot: BarGraphItem = BarGraphItem(x=[], height=[], width=0.8)
        self.widget.showGrid(x=True, y=True, alpha=0.3)
        self.widget.setLabels(left="Delta")
        self.widget.setYRange(-100, 100)
        # self.widget.setLimits(yMin=-1, yMax=1)
        self.widget.addItem(self.plot)
        self.layout.addWidget(self.widget)

        # plot_widget = PlotWidget()
        # self.plot: PlotItem = psd_widget.getPlotItem() # type: ignore
        # self.plot.showGrid(x=True, y=True, alpha=0.3)
        # self.plot.setLabels(left="", bottom="frequency (Hz)")
        # self.plot.getViewBox().setMouseEnabled(x=False, y=False) # type: ignore
        # self.plot.setLimits(xMin=1, xMax=40, yMin=0, yMax=500) # type: ignore
        # self.layout.addWidget(plot_widget)

    def update(self):
        delta = self.node.score
        self.plot.setOpts(x=[0], height=[delta], brushes=('g' if delta > 0 else 'r'))


import os

os.environ["PYQTGRAPH_QT_LIB"] = "PySide6"

from websocket import NeurofeedbackWebsocketServer
from biomarker.types import BiomarkerTypes
from biomarker.manager import BiomarkerManager
from ui.main_view import MainView2
from presenter import Presenter
from processing import NeurofeedbackProcessing
from view import MainView

from PySide6 import QtWidgets
from lsl_datasource import LSLDataSource
import sys

TIME_WINDOW = 10
AMPLITUDE_LIMIT = 100

if __name__ == "__main__":
    # app = QtWidgets.QApplication(sys.argv)
    # lsl_node = LSLDataSource()
    # nf_processing = NeurofeedbackProcessing(lsl_node.channel_count, lsl_node.sampling_rate, TIME_WINDOW)
    # lsl_node.samples_recieved.connect(nf_processing.update_buffer)
    # view = MainView(lsl_node.channel_count, TIME_WINDOW, lsl_node.sampling_rate)

    # presenter = Presenter(view, nf_processing)
    # view.show()
    # sys.exit(app.exec())

    app = QtWidgets.QApplication(sys.argv)

    view = MainView2()
    lsl_node = LSLDataSource()
    ws = NeurofeedbackWebsocketServer()

    manager = BiomarkerManager(lsl_node, view, ws)

    # manager.add_biomarker(BiomarkerTypes.BANDPOWER)
    # manager.add_biomarker(BiomarkerTypes.BANDPOWER)
    # manager.add_biomarker(BiomarkerTypes.BANDPOWER)

    view.show()
    sys.exit(app.exec())


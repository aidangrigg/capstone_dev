import os

os.environ["PYQTGRAPH_QT_LIB"] = "PySide6"

from brainground.websocket import NeurofeedbackWebsocketServer
from brainground.biomarker.manager import BiomarkerManager
from brainground.ui.view import MainView
from brainground.lsl_datasource import LSLDataSource

from PySide6 import QtWidgets
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

    view = MainView()
    lsl_node = LSLDataSource()
    ws = NeurofeedbackWebsocketServer()

    manager = BiomarkerManager(lsl_node, view, ws)

    # manager.add_biomarker(BiomarkerTypes.BANDPOWER)
    # manager.add_biomarker(BiomarkerTypes.BANDPOWER)
    # manager.add_biomarker(BiomarkerTypes.BANDPOWER)

    view.show()
    sys.exit(app.exec())


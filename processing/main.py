import os

os.environ["PYQTGRAPH_QT_LIB"] = "PySide6"

from brainground.application import BraingroundApplication
from brainground.websocket import NeurofeedbackWebsocketServer
from brainground.biomarker.manager import BiomarkerManager
from brainground.ui.view import MainView
from brainground.lsl_datasource import LSLDataSource

import sys

TIME_WINDOW = 10
AMPLITUDE_LIMIT = 100

if __name__ == "__main__":
    app = BraingroundApplication(sys.argv)

    # TODO: currently lsl_node has to be initialized first
    # (as it gets the sampling rate/ channel count that MainView depends on)
    # Either make this clearer or remove this required ordering (make view able to dynamically update
    # to changing eeg channels
    lsl_node = LSLDataSource()
    view = MainView()
    ws = NeurofeedbackWebsocketServer()

    manager = BiomarkerManager(lsl_node, view, ws)

    view.show()
    sys.exit(app.exec())


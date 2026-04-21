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

    view = MainView()
    lsl_node = LSLDataSource()
    ws = NeurofeedbackWebsocketServer()

    manager = BiomarkerManager(lsl_node, view, ws)

    view.show()
    sys.exit(app.exec())


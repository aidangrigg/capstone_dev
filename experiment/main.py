import logging
import argparse
import json
from pylsl import StreamInfo, StreamOutlet, cf_string
from PySide6.QtCore import QObject, QProcess, QThread, Signal
from PySide6.QtNetwork import QHostAddress
from PySide6.QtWebSockets import QWebSocketServer, QWebSocket

class ExperimentWsServer(QObject):
    sockets: list[QWebSocket] = []

    def __init__(self, addr: QHostAddress | QHostAddress.SpecialAddress = QHostAddress.SpecialAddress.LocalHost, port: int = 42069):
        super().__init__()

        logging.debug("Initialising websocket server at <%s:%d>", addr, port)

        self.server = QWebSocketServer("Experiment WS Server", QWebSocketServer.SslMode.NonSecureMode, self)
        if not self.server.listen(addr, port):
            return

        logging.debug("Websocket server successfully initialised!")
        self.server.newConnection.connect(self.on_new_connection)

    def on_new_connection(self):
        socket = self.server.nextPendingConnection()
        if socket is not None and socket.isValid():
            logging.debug("New connection to websocket server!")
            self.sockets.append(socket)

    def send_packet(self, packet: dict):
        logging.debug("Sending packet over websocket %s", packet)
        self.sockets = list(filter(lambda s: s.isValid(), self.sockets))

        str_packet = json.dumps(packet)

        for socket in self.sockets:
            socket.sendTextMessage(str_packet)

class ControlThread(QThread):
    command_ready = Signal(dict)

    def __init__(self, instructions: dict, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self.info = StreamInfo('ExperimentMarkers', 'marker', 1, 0, cf_string, 'exp_markers_001')
        self.outlet = StreamOutlet(self.info)

        self.instructions = instructions

    def speak(self, text: str) -> None:
        logging.debug("Trying to run espeak-ng with the following text: \"%s\"", text)
        proc = QProcess()
        proc.start(f"espeak-ng", [text])
        proc.waitForFinished()
        if proc.exitStatus() == QProcess.ExitStatus.NormalExit:
            logging.debug("espeak-ng succeeded!")
        else:
            logging.error(
                "espeak-ng failed to run. This is likely because it is not installed. stderr: %s",
                proc.readAllStandardError().toStdString()
            )
            app.quit()

    def run(self) -> None:
        for key, instruction in self.instructions.items():
            logging.info(f'Playing instruction "{key}"')

            self.speak(instruction["text"])

            logging.debug("Sending marker \"%s\" via LSL", instruction["lsl_marker_name"])
            self.outlet.push_sample([instruction["lsl_marker_name"]])

            for command in instruction["unity_commands"]:
                logging.debug("Sending command: %s", command)
                self.command_ready.emit(command)

            logging.debug("Sleeping for %d seconds...", instruction["delay"])
            self.sleep(instruction["delay"])

        logging.info("Reached end of instructions. Exiting...")
        app.quit()

if __name__ == "__main__":
    import sys, signal
    from PySide6.QtCore import QTimer, QCoreApplication

    parser = argparse.ArgumentParser(description="A helper script for managing experiments using Brainground.")
    parser.add_argument("-i", "--input", help="The experiment config file", required=True)
    parser.add_argument("-d", "--debug", help="Debug logging level", action="store_true")
    args = parser.parse_args()

    logging_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.getLogger("pylsl").setLevel(logging.FATAL)

    assert(args.input is not None)

    with open(args.input, "r") as fptr:
        instructions = json.loads(fptr.read())

    logging.info("Instructions loaded")
    logging.info(json.dumps(instructions, indent=4))

    app = QCoreApplication(sys.argv)
    ws = ExperimentWsServer()
    control_thread = ControlThread(instructions)
    control_thread.command_ready.connect(ws.send_packet)

    signal.signal(signal.SIGINT, lambda sig, frame: app.quit())

    # this is to periodically wake up so we can handle the signal
    timer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    input("Press any key to begin...")
    control_thread.start()
    sys.exit(app.exec())


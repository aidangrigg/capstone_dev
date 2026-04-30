import logging
from PySide6.QtCore import QJsonDocument, QJsonValue, QObject
from PySide6.QtNetwork import QHostAddress
from PySide6.QtWebSockets import QWebSocketServer, QWebSocket

WS_SERVER_NAME = "Neurofeedback Score WS Server"

class NeurofeedbackWebsocketServer(QObject):
    sockets: list[QWebSocket] = []

    def __init__(self, addr: QHostAddress | QHostAddress.SpecialAddress = QHostAddress.SpecialAddress.LocalHost, port: int = 1234):
        super().__init__()

        logging.debug("Initialising websocket server at <%s:%d>", addr, port)

        self.server = QWebSocketServer(WS_SERVER_NAME, QWebSocketServer.SslMode.NonSecureMode, self)
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

        json_doc: dict[str, QJsonValue] = {}

        for key, value in packet.items():
            json_doc[key] = QJsonValue(value)

        json = QJsonDocument(json_doc)

        str_packet = json.toJson(QJsonDocument.JsonFormat.Compact).toStdString()

        for socket in self.sockets:
            socket.sendTextMessage(str_packet)

if __name__ == "__main__":
    import sys
    from PySide6.QtCore import QTimer, QCoreApplication

    app = QCoreApplication(sys.argv)
    ws = NeurofeedbackWebsocketServer()

    timer = QTimer()
    timer.timeout.connect(lambda: ws.send_packet({"alpha": 10}))
    timer.start(1000)

    sys.exit(app.exec())


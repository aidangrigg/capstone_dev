from PySide6.QtCore import QJsonDocument, QJsonValue, QObject
from PySide6.QtNetwork import QHostAddress
from PySide6.QtWebSockets import QWebSocketServer, QWebSocket

WS_SERVER_NAME = "Neurofeedback Score WS Server"

class NeurofeedbackWebsocketServer(QObject):
    sockets: list[QWebSocket] = []

    def __init__(self):

        super().__init__()

        self.server = QWebSocketServer(WS_SERVER_NAME, QWebSocketServer.SslMode.NonSecureMode, self)

        if not self.server.listen(QHostAddress.SpecialAddress.LocalHost, 1234):
            return
        self.server.newConnection.connect(self.on_new_connection)

    def on_new_connection(self):
        socket = self.server.nextPendingConnection()
        if socket is not None and socket.isValid():
            self.sockets.append(socket)

    def send_packet(self, packet: dict):
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


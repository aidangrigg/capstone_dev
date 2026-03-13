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
            print("FAILED TO CREATE SERVER")
            return
        self.server.newConnection.connect(self.on_new_connection)

    def on_new_connection(self):
        print("new connection")
        socket = self.server.nextPendingConnection()
        if socket is not None and socket.isValid():
            self.sockets.append(socket)

    def send_packet(self, delta: float):
        self.sockets = list(filter(lambda s: s.isValid(), self.sockets))

        json = QJsonDocument({
            "delta": QJsonValue(delta)
        })

        packet = json.toJson(QJsonDocument.JsonFormat.Compact).toStdString()

        print(f"number of sockets: {len(self.sockets)}")
        for socket in self.sockets:
            socket.sendTextMessage(packet)

if __name__ == "__main__":
    import sys
    from PySide6.QtCore import QTimer, QCoreApplication

    app = QCoreApplication(sys.argv)
    ws = NeurofeedbackWebsocketServer()

    timer = QTimer()
    timer.timeout.connect(lambda: ws.send_packet(10))
    timer.start(1000)

    sys.exit(app.exec())


from typing import Optional, Any, TYPE_CHECKING

from PySide2.QtCore import (QObject, QDataStream, QTime)
from PySide2.QtNetwork import (QTcpSocket, QHostAddress)

from net.chess_server import ServerThread

if TYPE_CHECKING:
    from qt_windows.main_window import MainWindow
else:
    MainWindow = Any


class ChessClient(QObject):
    def __init__(self, ip: str, port: int, parent: MainWindow) -> None:
        super().__init__(parent)
        self.mainWindow: MainWindow = parent
        self.serverThread: Optional[ServerThread] = None
        self.playerNick: Optional[str] = None

        # Initialize client socket
        self.socket = QTcpSocket()
        self.socket.connected.connect(self.connected)
        self.socket.disconnected.connect(self.disconnected)
        self.socket.errorOccurred.connect(self.errorOccurred)
        self.socket.readyRead.connect(self.receiveData)

        # Establish a connection to the host
        self.ip, self.port = QHostAddress(ip), port
        self.socket.connectToHost(self.ip, self.port)

    def connected(self) -> None:
        print("Connected to server!")
        self.mainWindow.errorLabel.setText("Connected to server!")
        self.mainWindow.errorLabel.setStyleSheet("color:rgb(0, 170, 0)")

    def disconnected(self) -> None:
        print("Disconnected from server...")
        self.mainWindow.errorLabel.setText("Disconnected from server...")
        self.mainWindow.errorLabel.setStyleSheet("color:rgb(227, 11, 92)")

    def errorOccurred(self, error: Any) -> None:
        if error == QTcpSocket.ConnectionRefusedError:
            print("The server is not running! Starting the server...")
            self.mainWindow.errorLabel.setText(
                "The server is not running! Starting the server...")
            self.mainWindow.errorLabel.setStyleSheet("color:rgb(0, 170, 0)")

            # Launch server
            self.serverThread = ServerThread(self.ip, self.port,
                                             self.mainWindow)
            self.serverThread.start()
            self.socket.connectToHost(self.ip, self.port)
        else:
            print(f"Error: {error}")

    def receiveData(self) -> None:
        stream = QDataStream(self.socket)
        stream.setVersion(QDataStream.Qt_5_0)

        while self.socket.bytesAvailable() > 0:
            data = stream.readQString()

            if data.startswith("set_nick:"):
                self.playerNick = data.split(':')[1]
                print(f"Your side: {self.playerNick}.")

                if self.playerNick == "light":
                    self.mainWindow.errorLabel.setText(
                        f"Wait for another player... Invite your friend! \
                            Network: {self.ip.toString()}:{self.port}")
                    self.mainWindow.errorLabel.setStyleSheet(
                        "color:rgb(0, 170, 0)")
            elif data == "server_full":
                print("The server is full! Cannot join the game...")
                self.socket.disconnectFromHost()
            elif data == "start":
                print("Start!")
                self.mainWindow.errorLabel.setText("Start!")
                self.mainWindow.errorLabel.setStyleSheet(
                    "color:rgb(0, 170, 0)")

                self.mainWindow.setClocks()
                self.mainWindow.board.logic.activePlayer = "light"
                self.mainWindow.netActivePlayer = "light"
            elif data.startswith("time:"):
                time = map(int, data.split(":")[1:])

                if self.playerNick == "light":
                    self.mainWindow.clock2.leftTime = QTime(*time)
                    self.mainWindow.clock2.update()
                elif self.playerNick == "dark":
                    self.mainWindow.clock1.leftTime = QTime(*time)
                    self.mainWindow.clock1.update()
            else:
                # Perform move
                startX, startY, newX, newY = map(int, data[:4])
                promotionPiece = data[4] if len(data) > 4 else None
                sanMove = self.mainWindow.board.logic.coordsToSAN(
                    startX, startY, newX, newY, promotionPiece)
                self.mainWindow.board.textMove(sanMove)
                print(f"Received: {data} ({sanMove})")

                # Change active player and set clocks
                player = self.mainWindow.board.logic.activePlayer
                self.mainWindow.board.changeActivePlayer(player)
                self.mainWindow.netActivePlayer = "light" \
                    if self.mainWindow.netActivePlayer == "dark" else "dark"

                self.mainWindow.errorLabel.setText("Your turn!")
                self.mainWindow.errorLabel.setStyleSheet(
                    "color:rgb(0, 170, 0)")

    def sendData(self, data: str) -> None:
        stream = QDataStream(self.socket)
        stream.setVersion(QDataStream.Qt_5_0)
        stream.writeQString(data)

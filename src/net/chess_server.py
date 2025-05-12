import sys
from typing import Optional, Any, List

from PySide2.QtCore import (QObject, QDataStream, QThread)
from PySide2.QtNetwork import (QTcpServer, QHostAddress)


class ChessServer(QObject):
    def __init__(self, ip: str, port: int, parent: Any = None) -> None:
        super().__init__(parent)
        self.mainWindow = parent

        # Initialize server
        self.server = QTcpServer()
        self.server.newConnection.connect(self.newConnection)

        # Establish a connection
        self.ip, self.port = QHostAddress(ip), port
        if not self.server.listen(self.ip, self.port):
            print("Server could not start...")
            sys.exit(1)
        else:
            print(f"Server running on {self.ip.toString()}:{self.port}.")

        # Players (clients) info
        self.playerSocket: List[Optional[QTcpServer]] = [None, None]
        self.playerNick: List[Optional[str]] = [None, None]

    def newConnection(self) -> None:
        if None not in self.playerSocket:
            print("There are already two players! Rejecting connection...")
            newSocket = self.server.nextPendingConnection()
            stream = QDataStream(newSocket)
            stream.setVersion(QDataStream.Qt_5_0)
            stream.writeQString("server_full")
            newSocket.disconnectFromHost()
            return

        playerInd = 0 if self.playerSocket[0] is None else 1

        # Initialize new socket
        newSocket = self.server.nextPendingConnection()
        newSocket.readyRead.connect(
            lambda: self.receiveData(playerInd))
        newSocket.disconnected.connect(
            lambda: self.playerDisconnected(playerInd))

        # Refresh info about players (sockets and nicknames)
        self.playerSocket[playerInd] = newSocket
        playerNick = 'light' if playerInd == 0 else 'dark'
        self.playerNick[playerInd] = playerNick
        self.sendData(playerInd, f"set_nick:{playerNick}")
        print(f"Player ({playerNick}) joined the game!")

        # Check if two players are connected
        if None not in self.playerSocket:
            self.sendData(playerInd, "start")
            self.sendData(1 - playerInd, "start")

    def playerDisconnected(self, playerInd: int) -> None:
        print(f"Player ({self.playerNick[playerInd]}) is disconnected...")

        self.playerSocket[playerInd].deleteLater()
        self.playerSocket[playerInd] = None
        self.playerNick[playerInd] = None

    def receiveData(self, playerInd: int) -> None:
        socket = self.playerSocket[playerInd]
        stream = QDataStream(socket)
        stream.setVersion(QDataStream.Qt_5_0)

        while socket.bytesAvailable() > 0:
            data = stream.readQString()

            otherPlayerInd = 1 - playerInd
            self.sendData(otherPlayerInd, data)

    def sendData(self, playerInd: int, data: str) -> None:
        socket = self.playerSocket[playerInd]
        if socket is not None:
            stream = QDataStream(socket)
            stream.setVersion(QDataStream.Qt_5_0)
            stream.writeQString(data)


class ServerThread(QThread):
    def __init__(self, ip: str, port: int, parent: Any = None) -> None:
        self.server = None
        self.mainWindow = parent
        self.ip, self.port = ip, port

    def run(self) -> None:
        self.server = ChessServer(self.ip, self.port, self.mainWindow)
        self.exec_()

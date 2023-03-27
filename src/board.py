from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QBrush, QPixmap
from PyQt5.QtWidgets import QGraphicsScene
import itertools

from data import resources_rc
from board_tile import BoardTile
from board_pieces import Piece
from chess_logic import ChessLogic
from clock import Clock


class Board(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(QBrush(QPixmap(":/board/wood/light")))
        self.mainWindow = parent

        self.boardSize = QSize(8, 8)
        self.tileSize = 100

        self.chessboard = ChessLogic()
        self.printTextBoard()
        self.createTiles()
        self.createPieces()

        self.clock1 = Clock(self.endPlayer1Move)
        self.clock1.setOpacity(1.0)
        self.mainWindow.clock1View.scene().addItem(self.clock1)
        self.clock2 = Clock(self.endPlayer2Move)
        self.clock2.setOpacity(0.5)
        self.mainWindow.clock2View.scene().addItem(self.clock2)

    def createTiles(self):
        [self.addItem(BoardTile(self.tileSize, i, j))
         for i, j in itertools.product(range(self.boardSize.width()), range(self.boardSize.height()))]

    def createPieces(self):
        self.createSide("light", 7, 6)
        self.createSide("dark", 0, 1)

    def createSide(self, side, firstRow, secondRow):
        piece = "R" if side == "light" else "r"
        self.addItem(Piece(piece, side, 0, firstRow, self.tileSize))
        piece = "N" if side == "light" else "n"
        self.addItem(Piece(piece, side, 1, firstRow, self.tileSize))
        piece = "B" if side == "light" else "b"
        self.addItem(Piece(piece, side, 2, firstRow, self.tileSize))
        piece = "Q" if side == "light" else "q"
        self.addItem(Piece(piece, side, 3, firstRow, self.tileSize))
        piece = "K" if side == "light" else "k"
        self.addItem(Piece(piece, side, 4, firstRow, self.tileSize))
        piece = "B" if side == "light" else "b"
        self.addItem(Piece(piece, side, 5, firstRow, self.tileSize))
        piece = "N" if side == "light" else "n"
        self.addItem(Piece(piece, side, 6, firstRow, self.tileSize))
        piece = "R" if side == "light" else "r"
        self.addItem(Piece(piece, side, 7, firstRow, self.tileSize))

        piece = "P" if side == "light" else "p"
        [self.addItem(Piece(piece, side, x, secondRow, self.tileSize))
         for x in range(self.boardSize.width())]

    def printTextBoard(self):
        self.mainWindow.outputBoard.clear()

        self.mainWindow.outputBoard.append("     " + " ".join("abcdefgh"))
        self.mainWindow.outputBoard.append("     " + "- " * 8)
        for i, row in enumerate(self.chessboard.textBoard):
            self.mainWindow.outputBoard.append(f' {8 - i} | ' + ' '.join(row))

    def endPlayer1Move(self, event):
        if event.button() == Qt.LeftButton:
            if self.chessboard.activePlayer == "light":
                self.changeActivePlayer()

                self.clock1.setOpacity(0.5)
                self.clock2.setOpacity(1.0)

        super().mousePressEvent(event)

    def endPlayer2Move(self, event):
        if event.button() == Qt.LeftButton:
            if self.chessboard.activePlayer == "dark":
                self.changeActivePlayer()

                self.clock2.setOpacity(0.5)
                self.clock1.setOpacity(1.0)

        super().mousePressEvent(event)

    def changeActivePlayer(self):
        self.chessboard.playerMoved = False

        if self.chessboard.activePlayer == "light":
            self.chessboard.activePlayer = "dark"
            self.mainWindow.playerInput.setPlaceholderText("Input | Player №2")
        else:
            self.chessboard.activePlayer = "light"
            self.mainWindow.playerInput.setPlaceholderText("Input | Player №1")

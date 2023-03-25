from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont, QBrush, QPixmap
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsTextItem

from data import resources_rc
from board_tile import BoardTile
from board_pieces import Piece
from chess_logic import ChessLogic


class Board(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(QBrush(QPixmap(":/board/wood/light")))

        self.boardSize = QSize(8, 8)
        self.tileSize = 100

        self.chessboard = ChessLogic()
        self.createTiles()
        self.createPieces()
        self.createLabels()

    def createTiles(self):
        _ = [self.addItem(BoardTile(self.tileSize, i, j))
             for i in range(self.boardSize.width())
             for j in range(self.boardSize.height())]

    def createPieces(self):
        self.createSide("light", 7, 6)
        self.createSide("dark", 0, 1)

    def createSide(self, side, firstRow, secondRow):
        self.addItem(Piece("rook", side, 0, firstRow, self.tileSize, self.chessboard))
        self.addItem(Piece("knight", side, 1, firstRow, self.tileSize, self.chessboard))
        self.addItem(Piece("bishop", side, 2, firstRow, self.tileSize, self.chessboard))
        self.addItem(Piece("queen", side, 3, firstRow, self.tileSize, self.chessboard))
        self.addItem(Piece("king", side, 4, firstRow, self.tileSize, self.chessboard))
        self.addItem(Piece("bishop", side, 5, firstRow, self.tileSize, self.chessboard))
        self.addItem(Piece("knight", side, 6, firstRow, self.tileSize, self.chessboard))
        self.addItem(Piece("rook", side, 7, firstRow, self.tileSize, self.chessboard))

        _ = [self.addItem(Piece("pawn", side, x, secondRow, self.tileSize, self.chessboard))
             for x in range(self.boardSize.width())]

    def createLabels(self):
        fontSize = self.tileSize // 7
        font = QFont("Roboto", fontSize, QFont.Bold)

        for i in range(self.boardSize.width()):
            labelHT = QGraphicsTextItem(chr(65 + i))
            labelHT.setFont(font)
            labelHT.setPos(i * self.tileSize + self.tileSize / 2 - labelHT.boundingRect().width() / 2,
                           -labelHT.boundingRect().height())

            labelHB = QGraphicsTextItem(chr(65 + i))
            labelHB.setFont(font)
            labelHB.setPos(i * self.tileSize + self.tileSize / 2 - labelHB.boundingRect().width() / 2,
                           8 * self.tileSize)

            labelVL = QGraphicsTextItem(str(self.boardSize.width() - i))
            labelVL.setFont(font)
            labelVL.setPos(-1.5 * labelVL.boundingRect().width(),
                           i * self.tileSize + self.tileSize / 2 - labelVL.boundingRect().height() / 2)

            labelVR = QGraphicsTextItem(str(self.boardSize.width() - i))
            labelVR.setFont(font)
            labelVR.setPos(8 * self.tileSize + labelVR.boundingRect().width() / 2,
                           i * self.tileSize + self.tileSize / 2 - labelVR.boundingRect().height() / 2)

            self.addItem(labelHT)
            self.addItem(labelHB)
            self.addItem(labelVL)
            self.addItem(labelVR)

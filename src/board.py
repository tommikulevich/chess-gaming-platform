from PyQt5.QtCore import QSize
from PyQt5.QtGui import QBrush, QPixmap
from PyQt5.QtWidgets import QGraphicsScene
import itertools

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

    def createTiles(self):
        [self.addItem(BoardTile(self.tileSize, i, j))
         for i, j in itertools.product(range(self.boardSize.width()), range(self.boardSize.height()))]

    def createPieces(self):
        self.createSide("light", 7, 6)
        self.createSide("dark", 0, 1)

    def createSide(self, side, firstRow, secondRow):
        piece = "R" if side == "light" else "r"
        self.addItem(Piece(piece, side, 0, firstRow, self.tileSize, self.chessboard))
        piece = "N" if side == "light" else "n"
        self.addItem(Piece(piece, side, 1, firstRow, self.tileSize, self.chessboard))
        piece = "B" if side == "light" else "b"
        self.addItem(Piece(piece, side, 2, firstRow, self.tileSize, self.chessboard))
        piece = "Q" if side == "light" else "q"
        self.addItem(Piece(piece, side, 3, firstRow, self.tileSize, self.chessboard))
        piece = "K" if side == "light" else "k"
        self.addItem(Piece(piece, side, 4, firstRow, self.tileSize, self.chessboard))
        piece = "B" if side == "light" else "b"
        self.addItem(Piece(piece, side, 5, firstRow, self.tileSize, self.chessboard))
        piece = "N" if side == "light" else "n"
        self.addItem(Piece(piece, side, 6, firstRow, self.tileSize, self.chessboard))
        piece = "R" if side == "light" else "r"
        self.addItem(Piece(piece, side, 7, firstRow, self.tileSize, self.chessboard))

        piece = "P" if side == "light" else "p"
        [self.addItem(Piece(piece, side, x, secondRow, self.tileSize, self.chessboard))
         for x in range(self.boardSize.width())]

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap
import resources_rc     # don't remove it!


class Piece(QGraphicsPixmapItem):
    def __init__(self, color, x, y, tileSize, parent=None):
        super().__init__(parent)
        self.x = x
        self.y = y
        self.color = color
        self.tileSize = tileSize
        self.setPos(x * self.tileSize, y * self.tileSize)

    def loadTexture(self, pieceName):
        texturePath = f":/pieces/{self.color}/{pieceName}.png"
        piecePixmap = QPixmap(texturePath)
        self.setPixmap(piecePixmap.scaled(self.tileSize, self.tileSize, Qt.KeepAspectRatio, Qt.SmoothTransformation))


class Pawn(Piece):
    def __init__(self, color, x, y, parent=None):
        super().__init__(color, x, y, parent)
        self.loadTexture("pawn")


class Rook(Piece):
    def __init__(self, color, x, y, parent=None):
        super().__init__(color, x, y, parent)
        self.loadTexture("rook")


class Knight(Piece):
    def __init__(self, color, x, y, parent=None):
        super().__init__(color, x, y, parent)
        self.loadTexture("knight")


class Bishop(Piece):
    def __init__(self, color, x, y, parent=None):
        super().__init__(color, x, y, parent)
        self.loadTexture("bishop")


class Queen(Piece):
    def __init__(self, color, x, y, parent=None):
        super().__init__(color, x, y, parent)
        self.loadTexture("queen")


class King(Piece):
    def __init__(self, color, x, y, parent=None):
        super().__init__(color, x, y, parent)
        self.loadTexture("king")

from PyQt5.QtCore import QRectF, QSize
from PyQt5.QtGui import QImage, QBrush, QPen
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItem
from pieces import Pawn, Rook, Knight, Bishop, Queen, King
import resources_rc     # don't remove it!


class ChessBoard(QGraphicsScene):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.boardSize = QSize(8, 8)
        self.tileSize = 128
        self.createBoard()

    def createBoard(self):
        self.createTiles()
        self.createPieces()

    def createTiles(self):
        for i in range(self.boardSize.width()):
            for j in range(self.boardSize.height()):
                tile = ChessTile(self.tileSize, i, j)
                self.addItem(tile)

    def createPieces(self):
        for color in ["light", "dark"]:
            y = 0 if color == "light" else 7

            self.addItem(Rook(color, 0, y, self.tileSize))
            self.addItem(Knight(color, 1, y, self.tileSize))
            self.addItem(Bishop(color, 2, y, self.tileSize))
            self.addItem(Queen(color, 3, y, self.tileSize))
            self.addItem(King(color, 4, y, self.tileSize))
            self.addItem(Bishop(color, 5, y, self.tileSize))
            self.addItem(Knight(color, 6, y, self.tileSize))
            self.addItem(Rook(color, 7, y, self.tileSize))

            y = 1 if color == "light" else 6
            for x in range(8):
                self.addItem(Pawn(color, x, y, self.tileSize))


class ChessTile(QGraphicsItem):

    def __init__(self, tile_size, x, y, parent=None):
        super().__init__(parent)
        self.x = x
        self.y = y
        self.tile_size = tile_size
        self.setPos(x * tile_size, y * tile_size)

        self.lightTexture = None
        self.darkTexture = None
        self.loadTexture()

    def loadTexture(self):
        self.darkTexture = QImage(":/board/dark_square")
        self.lightTexture = QImage(":/board/light_square")

    def boundingRect(self):
        return QRectF(0, 0, self.tile_size, self.tile_size)

    def paint(self, painter, option, widget):
        if (self.x + self.y) % 2 == 0:
            painter.drawImage(self.boundingRect(), self.lightTexture)
        else:
            painter.drawImage(self.boundingRect(), self.darkTexture)

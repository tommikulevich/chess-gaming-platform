from PyQt5.QtCore import QRectF, QSize, QObject
from PyQt5.QtGui import QImage, QFont, QBrush, QPixmap
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItem, QMenu, QAction, QGraphicsTextItem
from math import floor
from pieces import Piece, Pawn, Rook, Knight, Bishop, Queen, King
from src import resources_rc


class ChessBoard(QGraphicsScene):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.boardSize = QSize(8, 8)
        self.tileSize = 100

        self.createTiles()
        self.createPieces()
        self.createLabels()

        self.setBackgroundBrush(QBrush(QPixmap(":/board/wood/light")))

    def createTiles(self):
        _ = [self.addItem(ChessTile(self.tileSize, i, j))
             for i in range(self.boardSize.width())
             for j in range(self.boardSize.height())]

    def createPieces(self):
        for side in ["lightSide", "darkSide"]:
            y = 0 if side == "lightSide" else 7

            self.addItem(Rook(side, 0, y, self.tileSize))
            self.addItem(Knight(side, 1, y, self.tileSize))
            self.addItem(Bishop(side, 2, y, self.tileSize))
            self.addItem(Queen(side, 3, y, self.tileSize))
            self.addItem(King(side, 4, y, self.tileSize))
            self.addItem(Bishop(side, 5, y, self.tileSize))
            self.addItem(Knight(side, 6, y, self.tileSize))
            self.addItem(Rook(side, 7, y, self.tileSize))

            y = 1 if side == "lightSide" else 6
            for x in range(self.boardSize.width()):
                self.addItem(Pawn(side, x, y, self.tileSize))

    def createLabels(self):
        fontSize = floor(self.tileSize / 7)
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

            labelVL = QGraphicsTextItem(str(i + 1))
            labelVL.setFont(font)
            labelVL.setPos(-1.5 * labelVL.boundingRect().width(),
                           i * self.tileSize + self.tileSize / 2 - labelVL.boundingRect().height() / 2)

            labelVR = QGraphicsTextItem(str(i + 1))
            labelVR.setFont(font)
            labelVR.setPos(8 * self.tileSize + labelVR.boundingRect().width() / 2,
                           i * self.tileSize + self.tileSize / 2 - labelVR.boundingRect().height() / 2)

            self.addItem(labelHT)
            self.addItem(labelHB)
            self.addItem(labelVL)
            self.addItem(labelVR)


class ChessTile(QGraphicsItem, QObject):

    def __init__(self, tileSize, x, y, parent=None):
        super().__init__(parent)
        self.x = x
        self.y = y
        self.tileSize = tileSize
        self.setPos(x * tileSize, y * tileSize)

        self.boardStyleDark = ":/board/standard/dark"
        self.boardStyleLight = ":/board/standard/light"
        self.darkTexture = None
        self.lightTexture = None
        self.loadTexture()

    def loadTexture(self):
        self.darkTexture = QImage(self.boardStyleDark)
        self.lightTexture = QImage(self.boardStyleLight)

    def boundingRect(self):
        return QRectF(0, 0, self.tileSize, self.tileSize)

    def paint(self, painter, option, widget):
        texture = self.lightTexture if (self.x + self.y) % 2 == 0 else self.darkTexture
        painter.drawImage(self.boundingRect(), texture)

    def contextMenuEvent(self, event):
        menu = QMenu()

        boardStyleMenu = QMenu("Change Board Style", menu)
        standardBoardAction = QAction("Standard", boardStyleMenu)
        rockBoardAction = QAction("Rock", boardStyleMenu)
        woodBoardAction = QAction("Wood", boardStyleMenu)

        boardStyleMenu.addAction(standardBoardAction)
        boardStyleMenu.addAction(rockBoardAction)
        boardStyleMenu.addAction(woodBoardAction)
        menu.addMenu(boardStyleMenu)

        standardBoardAction.triggered.connect(lambda: self.changeTileTexture("standard"))
        rockBoardAction.triggered.connect(lambda: self.changeTileTexture("rock"))
        woodBoardAction.triggered.connect(lambda: self.changeTileTexture("wood"))

        menu.exec_(event.screenPos())

    def changeTileTexture(self, boardStyle):
        for item in self.scene().items():
            if isinstance(item, ChessTile):
                item.boardStyleDark = f":/board/{boardStyle}/dark"
                item.boardStyleLight = f":/board/{boardStyle}/light"

                item.loadTexture()
                item.update()

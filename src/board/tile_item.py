from PySide2.QtCore import (QPointF, QRect, QSize)
from PySide2.QtGui import (QColor, QPen, QFont, QPixmap)
from PySide2.QtWidgets import (QGraphicsItem, QMenu, QAction)


class Tile(QGraphicsItem):
    def __init__(self, size, x, y, parent=None):
        super().__init__(parent)

        # Position parameters
        self.x = x
        self.y = y
        self.size = size
        self.setPos(x * size, y * size)

        # Texture parameters
        self.boardStyleDark = ":/board/standard/dark"
        self.boardStyleLight = ":/board/standard/light"

        self.darkTexture = None
        self.lightTexture = None
        self.loadTexture()

        self.showValid = False
        self.validTexture = QPixmap(QSize(self.size, self.size))
        self.validTexture.fill(QColor(122, 183, 100))

        self.showCheck = False
        self.checkTexture = QPixmap(QSize(self.size, self.size))
        self.checkTexture.fill(QColor(227, 11, 92))

    # ------------------
    # Texture components
    # ------------------

    def loadTexture(self):
        self.darkTexture = QPixmap(self.boardStyleDark)
        self.lightTexture = QPixmap(self.boardStyleLight)

    def boundingRect(self):
        return QRect(0, 0, self.size, self.size)

    def paint(self, painter, option, widget=None):
        # Choose the texture depending on the flags
        texture = (self.validTexture if self.showValid
                   else self.checkTexture if self.showCheck
                   else self.lightTexture if (self.x + self.y) % 2 == 0
                   else self.darkTexture)
        painter.drawPixmap(self.boundingRect(), texture)

        pen = QPen()
        pen.setWidth(1)
        pen.setColor(QColor(0, 0, 0))
        painter.setPen(pen)
        painter.drawRect(self.boundingRect())

        font = QFont()
        font.setPointSize(int(self.size / 12.5))
        painter.setFont(font)
        painter.setPen(QColor(210, 4, 45))

        # Draw A-H files
        if self.y == 0:
            painter.drawText(QPointF(self.size - 19, self.size / 5 + 1),
                             chr(65 + self.x))

        # Draw 1-8 ranks
        if self.x == 0:
            painter.drawText(QPointF(6, self.size / 5 + 1), str(8 - self.y))

    def changeTileTexture(self, boardStyle):
        [self.updateTileItem(item, boardStyle) for item in self.scene().items()
         if isinstance(item, Tile)]

    @staticmethod
    def updateTileItem(tile, boardStyle):
        tile.boardStyleDark = f":/board/{boardStyle}/dark"
        tile.boardStyleLight = f":/board/{boardStyle}/light"
        tile.darkTexture = tile.boardStyleDark
        tile.lightTexture = tile.boardStyleLight

        tile.update()

    def contextMenuEvent(self, event):
        # Right-click menu with options to change texture
        menu = QMenu()

        boardStyleMenu = QMenu("Change Board Style", menu)
        standardBoardAction = QAction("Standard", boardStyleMenu)
        rockBoardAction = QAction("Rock", boardStyleMenu)
        woodBoardAction = QAction("Wood", boardStyleMenu)

        boardStyleMenu.addAction(standardBoardAction)
        boardStyleMenu.addAction(rockBoardAction)
        boardStyleMenu.addAction(woodBoardAction)
        menu.addMenu(boardStyleMenu)

        standardBoardAction.triggered.connect(
            lambda: self.changeTileTexture("standard"))
        rockBoardAction.triggered.connect(
            lambda: self.changeTileTexture("rock"))
        woodBoardAction.triggered.connect(
            lambda: self.changeTileTexture("wood"))

        menu.exec_(event.screenPos())

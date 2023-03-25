from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QImage, QColor, QPen
from PyQt5.QtWidgets import QGraphicsItem, QMenu, QAction

from data import resources_rc


class BoardTile(QGraphicsItem):
    def __init__(self, size, x, y, parent=None):
        super().__init__(parent)
        self.x = x
        self.y = y
        self.size = size
        self.setPos(x * size, y * size)

        self.boardStyleDark = ":/board/standard/dark"
        self.boardStyleLight = ":/board/standard/light"

        self.darkTexture = None
        self.lightTexture = None
        self.validTexture = None
        self.showValid = False

        self.loadTexture()

    def loadTexture(self):
        if not self.showValid:
            self.darkTexture = QImage(self.boardStyleDark)
            self.lightTexture = QImage(self.boardStyleLight)
        else:
            self.validTexture = QImage(self.size, self.size, QImage.Format_RGB32)
            self.validTexture.fill(QColor(122, 183, 100))

    def boundingRect(self):
        return QRectF(0, 0, self.size, self.size)

    def paint(self, painter, option, widget):
        texture = self.lightTexture if (self.x + self.y) % 2 == 0 else self.darkTexture
        texture = self.validTexture if self.showValid else texture
        painter.drawImage(self.boundingRect(), texture)

        pen = QPen()
        pen.setWidth(1)
        pen.setColor(QColor(0, 0, 0))
        painter.setPen(pen)
        painter.drawRect(self.boundingRect())

    def changeTileTexture(self, boardStyle):
        for item in self.scene().items():
            if isinstance(item, BoardTile):
                item.boardStyleDark = f":/board/{boardStyle}/dark"
                item.boardStyleLight = f":/board/{boardStyle}/light"

                item.loadTexture()
                item.update()

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

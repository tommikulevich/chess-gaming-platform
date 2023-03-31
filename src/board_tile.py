from PySide2.QtCore import QRectF, QPointF
from PySide2.QtGui import QImage, QColor, QPen, QFont
from PySide2.QtWidgets import QGraphicsItem, QMenu, QAction

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
        self.checkTexture = None
        self.showValid = False
        self.showCheck = False

        self.loadTexture()

    def loadTexture(self):
        if self.showValid:
            self.validTexture = QImage(self.size, self.size, QImage.Format_RGB32)
            self.validTexture.fill(QColor(122, 183, 100))
        elif self.showCheck:
            self.checkTexture = QImage(self.size, self.size, QImage.Format_RGB32)
            self.checkTexture.fill(QColor(227, 11, 92))
        else:
            self.darkTexture = QImage(self.boardStyleDark)
            self.lightTexture = QImage(self.boardStyleLight)

    def boundingRect(self):
        return QRectF(0, 0, self.size, self.size)

    def paint(self, painter, option, widget):
        texture = self.lightTexture if (self.x + self.y) % 2 == 0 else self.darkTexture
        texture = self.checkTexture if self.showCheck else texture
        texture = self.validTexture if self.showValid else texture
        painter.drawImage(self.boundingRect(), texture)

        pen = QPen()
        pen.setWidth(1)
        pen.setColor(QColor(0, 0, 0))
        painter.setPen(pen)
        painter.drawRect(self.boundingRect())

        font = QFont()
        font.setPointSize(8)
        painter.setFont(font)
        painter.setPen(QColor(210, 4, 45))

        if self.y == 0:
            painter.drawText(QPointF(81, 21), chr(65 + self.x))

        if self.x == 0:
            painter.drawText(QPointF(6, 21), str(8 - self.y))

    def changeTileTexture(self, boardStyle):
        tileItems = [item for item in self.scene().items() if isinstance(item, BoardTile)]
        [self.updateTileItem(item, boardStyle) for item in tileItems]

    @staticmethod
    def updateTileItem(item, boardStyle):
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

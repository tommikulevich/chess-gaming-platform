from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import QGraphicsPixmapItem, QMenu, QAction, QMessageBox, QStyle, QApplication
from PyQt5.QtGui import QPixmap, QIcon

from board_tile import BoardTile
from data import resources_rc


class Piece(QGraphicsPixmapItem):
    def __init__(self, fullPieceName, side, x, y, pieceSize, chessboard, parent=None):
        super().__init__(parent)

        # For Game Logic
        self.fullPieceName = fullPieceName
        self.side = side
        self.pieceName = self.getNotation()

        self.chessboard = chessboard
        self.validMoves = []

        # For GUI
        self.setCursor(Qt.OpenHandCursor)
        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemSendsGeometryChanges, True)

        self.pieceSize = pieceSize
        self.startPos = self.gridToXY(x, y)
        self.setPos(self.startPos)

        self.pieceStyle = f":/pieces/{self.side}/{self.fullPieceName}"
        self.pieceLightSideStyle = f":/pieces/light/{self.fullPieceName}"
        self.pieceDarkSideStyle = f":/pieces/dark/{self.fullPieceName}"
        self.loadTexture()

    def getNotation(self):
        pieceDict = {'pawn': 'P', 'rook': 'R', 'knight': 'N', 'bishop': 'B', 'queen': 'Q', 'king': 'K'}
        notation = pieceDict[self.fullPieceName].lower() if self.side == "dark" else pieceDict[self.fullPieceName]

        return notation

    def loadTexture(self):
        piecePixmap = QPixmap(self.pieceStyle)
        self.setPixmap(piecePixmap.scaled(self.pieceSize, self.pieceSize, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def changePieceTexture(self, pieceStyle, side):
        for item in self.scene().items():
            if isinstance(item, Piece):
                newStyle = f":/pieces/{pieceStyle}/{self.fullPieceName}"

                if (side == "light" and newStyle == item.pieceDarkSideStyle) or \
                   (side == "dark" and newStyle == item.pieceLightSideStyle):
                    msg = QMessageBox()
                    msg.setWindowIcon(QIcon(QApplication.instance().style().standardPixmap(QStyle.SP_MessageBoxWarning)))
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText("You can't choose this style because someone have it!")
                    msg.setWindowTitle("Warning")
                    msg.exec_()

                    break

                if side == item.side:
                    if pieceStyle == self.side:
                        item.pieceStyle = f":/pieces/{item.side}/{item.fullPieceName}"
                    else:
                        item.pieceStyle = f":/pieces/{pieceStyle}/{item.fullPieceName}"

                    item.loadTexture()
                    item.update()

                if side == "light":
                    item.pieceLightSideStyle = newStyle
                else:
                    item.pieceDarkSideStyle = newStyle

    def changeTileTexture(self, isClick):
        for item in self.scene().items():
            if isinstance(item, BoardTile):
                itemX, itemY = self.xyToGrid(item.pos().x(), item.pos().y())

                if [itemX, itemY] in self.validMoves:
                    item.showValid = isClick
                    item.loadTexture()
                    item.update()

    def xyToGrid(self, x, y):
        gridX = round(x / self.pieceSize)
        gridY = round(y / self.pieceSize)

        return gridX, gridY

    def gridToXY(self, gridX, gridY):
        x = gridX * self.pieceSize
        y = gridY * self.pieceSize

        return QPointF(x, y)

    def contextMenuEvent(self, event):
        menu = QMenu()

        piecesStyleMenu = QMenu("Change Piece Style", menu)
        standardPiecesAction = QAction("Standard (b/w)", piecesStyleMenu)
        bluePiecesAction = QAction("Blue", piecesStyleMenu)
        greenPiecesAction = QAction("Green", piecesStyleMenu)
        redPiecesAction = QAction("Red", piecesStyleMenu)
        yellowPiecesAction = QAction("Yellow", piecesStyleMenu)

        piecesStyleMenu.addAction(standardPiecesAction)
        piecesStyleMenu.addAction(bluePiecesAction)
        piecesStyleMenu.addAction(greenPiecesAction)
        piecesStyleMenu.addAction(redPiecesAction)
        piecesStyleMenu.addAction(yellowPiecesAction)
        menu.addMenu(piecesStyleMenu)

        standardPiecesAction.triggered.connect(lambda: self.changePieceTexture(self.side, self.side))
        bluePiecesAction.triggered.connect(lambda: self.changePieceTexture("blue", self.side))
        greenPiecesAction.triggered.connect(lambda: self.changePieceTexture("green", self.side))
        redPiecesAction.triggered.connect(lambda: self.changePieceTexture("red", self.side))
        yellowPiecesAction.triggered.connect(lambda: self.changePieceTexture("yellow", self.side))

        menu.exec_(event.screenPos())

    def mousePressEvent(self, event):
        self.setCursor(Qt.ClosedHandCursor)

        self.startPos = self.pos()
        startX, startY = self.xyToGrid(self.startPos.x(), self.startPos.y())
        self.validMoves = self.chessboard.getPossibleMoves(self.pieceName, startX, startY)
        self.changeTileTexture(True)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        newPos = self.pos()

        if 0 < newPos.x() < 7 * self.pieceSize and 0 < newPos.y() < 7 * self.pieceSize:
            gridPos = self.gridToXY(*self.xyToGrid(newPos.x(), newPos.y()))
            self.setPos(gridPos)
        else:
            self.setPos(self.startPos)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)

        newPos = self.pos()
        endX, endY = self.xyToGrid(newPos.x(), newPos.y())
        startX, startY = self.xyToGrid(self.startPos.x(), self.startPos.y())

        if [endX, endY] in self.validMoves:
            startBit = self.chessboard.xyToBit(startX, startY)
            endBit = self.chessboard.xyToBit(endX, endY)
            self.chessboard.movePiece(self.pieceName, startBit, endBit)

            self.setPos(self.gridToXY(endX, endY))
            self.chessboard.printBoard()
        else:
            self.setPos(self.startPos)

        self.changeTileTexture(False)
        super().mouseReleaseEvent(event)

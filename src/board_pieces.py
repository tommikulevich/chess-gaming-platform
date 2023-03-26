from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import QGraphicsPixmapItem, QMenu, QAction, QMessageBox, QStyle, QApplication
from PyQt5.QtGui import QPixmap, QIcon

from data import resources_rc
from board_tile import BoardTile


class Piece(QGraphicsPixmapItem):
    def __init__(self, pieceName, side, x, y, pieceSize, chessboard, parent=None):
        super().__init__(parent)

        # For Game Logic
        self.side = side
        self.pieceName = pieceName

        self.chessboard = chessboard
        self.validMoves = []
        self.isCheckL = False
        self.isCheckD = False

        # For GUI
        self.setCursor(Qt.OpenHandCursor)
        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemSendsGeometryChanges, True)

        self.pieceSize = pieceSize
        self.startPos = self.gridToXY(x, y)
        self.setPos(self.startPos)

        self.pieceStyle = f":/pieces/{self.side}/{self.pieceName.lower()}"
        self.pieceLightSideStyle = f":/pieces/light/{self.pieceName.lower()}"
        self.pieceDarkSideStyle = f":/pieces/dark/{self.pieceName.lower()}"
        self.loadTexture()

    def loadTexture(self):
        piecePixmap = QPixmap(self.pieceStyle)
        self.setPixmap(piecePixmap.scaled(self.pieceSize, self.pieceSize, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def changePieceTexture(self, pieceStyle, side):
        pieceItems = [item for item in self.scene().items() if isinstance(item, Piece)]
        for item in pieceItems:
            newStyle = f":/pieces/{pieceStyle}/{self.pieceName}"

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
                    item.pieceStyle = f":/pieces/{item.side}/{item.pieceName.lower()}"
                else:
                    item.pieceStyle = f":/pieces/{pieceStyle}/{item.pieceName.lower()}"

                item.loadTexture()
                item.update()

            if side == "light":
                item.pieceLightSideStyle = newStyle
            else:
                item.pieceDarkSideStyle = newStyle

    def changeValidTileTexture(self, isClick):
        tileItems = [item for item in self.scene().items() if isinstance(item, BoardTile)]
        for item in tileItems:
            itemX, itemY = self.xyToGrid(item.pos().x(), item.pos().y())

            if [itemX, itemY] in self.validMoves:
                item.showValid = isClick
                item.loadTexture()
                item.update()

    def changeCheckKingTexture(self):
        if self.isCheckL:
            kingPosX, kingPosY = self.chessboard.getKingPos(True)
            kingTile = self.scene().itemAt(self.gridToXY(kingPosX, kingPosY), self.transform())

            kingTile.showCheck = True
            kingTile.loadTexture()
            kingTile.update()
        else:
            kingPosX, kingPosY = self.chessboard.getKingPos(True)
            kingTile = self.scene().itemAt(self.gridToXY(kingPosX, kingPosY), self.transform())

            kingTile.showCheck = False
            kingTile.loadTexture()
            kingTile.update()

        if self.isCheckD:
            kingPosX, kingPosY = self.chessboard.getKingPos(False)
            kingTile = self.scene().itemAt(self.gridToXY(kingPosX, kingPosY), self.transform())

            kingTile.showCheck = True
            kingTile.loadTexture()
            kingTile.update()
        else:
            kingPosX, kingPosY = self.chessboard.getKingPos(False)
            kingTile = self.scene().itemAt(self.gridToXY(kingPosX, kingPosY), self.transform())

            kingTile.showCheck = False
            kingTile.loadTexture()
            kingTile.update()

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

    def playerMove(self):
        newPos = self.pos()

        if not (0 < newPos.x() < 7 * self.pieceSize and 0 < newPos.y() < 7 * self.pieceSize):
            self.setPos(self.startPos)

        endX, endY = self.xyToGrid(newPos.x(), newPos.y())
        startX, startY = self.xyToGrid(self.startPos.x(), self.startPos.y())

        if [endX, endY] in self.validMoves:
            self.chessboard.movePiece(startX, startY, endX, endY)

            targetItem = [item for item in self.scene().items(self.gridToXY(endX, endY), self.pieceSize, self.pieceSize)
                          if (isinstance(item, Piece) and item is not self)]
            if targetItem:
                self.scene().removeItem(targetItem[0])

            self.setPos(self.gridToXY(endX, endY))
            self.chessboard.printBoard()
        else:
            self.setPos(self.startPos)

        self.isCheckL = self.chessboard.isInCheck(True)
        self.isCheckD = self.chessboard.isInCheck(False)

        self.changeValidTileTexture(False)
        self.changeCheckKingTexture()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)

            self.startPos = self.pos()
            startX, startY = self.xyToGrid(self.startPos.x(), self.startPos.y())
            self.validMoves = self.chessboard.getLegalMoves(startX, startY)

            self.changeValidTileTexture(True)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.OpenHandCursor)
            self.playerMove()

        super().mouseReleaseEvent(event)

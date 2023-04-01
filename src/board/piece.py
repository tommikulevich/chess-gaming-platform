from PySide2.QtCore import Qt, QPointF, QRectF
from PySide2.QtWidgets import QGraphicsPixmapItem, QMenu, QAction, QMessageBox, QStyle, QApplication, QGridLayout, \
    QDialog, QLabel, QPushButton, QVBoxLayout
from PySide2.QtGui import QPixmap, QIcon
from functools import partial

from data import resources_qrc
from src.board.tile import Tile


class Piece(QGraphicsPixmapItem):
    def __init__(self, pieceName, side, x, y, pieceSize, parent=None):
        super().__init__(parent)

        # For Game Logic
        self.side = side
        self.pieceName = pieceName

        self.legalMoves = []
        self.isCheckLocal = False

        # For GUI
        self.setCursor(Qt.OpenHandCursor)
        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemSendsGeometryChanges, True)

        self.pieceSize = pieceSize
        self.startPos = self.gridToXY(x, y)
        self.setPos(self.startPos)

        self.pieceTheme = self.side
        self.pieceStyle = f":/pieces/{self.pieceTheme}/{self.pieceName.lower()}"
        self.pieceLightSideStyle = f":/pieces/light/{self.pieceName.lower()}"
        self.pieceDarkSideStyle = f":/pieces/dark/{self.pieceName.lower()}"
        self.loadTexture()

    def loadTexture(self):
        piecePixmap = QPixmap(self.pieceStyle)
        self.setPixmap(piecePixmap.scaled(self.pieceSize, self.pieceSize, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def changePieceTexture(self, pieceStyle, side):
        self.pieceTheme = pieceStyle
        pieceItems = [item for item in self.scene().items() if isinstance(item, Piece)]
        newStyle = f":/pieces/{self.pieceTheme}/{self.pieceName.lower()}"

        conflict = any((side == "light" and newStyle == item.pieceDarkSideStyle) or
                       (side == "dark" and newStyle == item.pieceLightSideStyle)
                       for item in pieceItems)

        if conflict:
            msg = QMessageBox(self.scene().mainWindow.ui)
            msg.setWindowIcon(QIcon(QApplication.instance().style().standardPixmap(QStyle.SP_MessageBoxWarning)))
            msg.setIcon(QMessageBox.Warning)
            msg.setText("You can't choose this style because another side have it!")
            msg.setWindowTitle("Warning")
            msg.exec_()
        else:
            updatePieces = partial(self.updatePiecesStyle, side=side, newStyle=newStyle)
            list(map(updatePieces, pieceItems))

    def updatePiecesStyle(self, item, side, newStyle):
        if side == item.side:
            if self.pieceTheme == self.side:
                item.pieceStyle = f":/pieces/{item.side}/{item.pieceName.lower()}"
            else:
                item.pieceStyle = f":/pieces/{self.pieceTheme}/{item.pieceName.lower()}"

            item.loadTexture()
            item.update()

            if side == "light":
                item.pieceLightSideStyle = newStyle
            else:
                item.pieceDarkSideStyle = newStyle

    def changeValidTileTexture(self, isClick):
        tileItems = [item for item in self.scene().items() if isinstance(item, Tile)]

        updateValidTileWithClick = partial(self.updateValidTile, isClick=isClick)
        list(map(updateValidTileWithClick, tileItems))

    def updateValidTile(self, tile, isClick):
        tileX, tileY = self.xyToGrid(tile.pos().x(), tile.pos().y())

        if [tileX, tileY] in self.legalMoves:
            tile.showValid = isClick
            tile.update()

    def changeCheckKingTexture(self, startX, startY, kingPosX, kingPosY, isCheck):
        if self.pieceName.lower() == 'k':
            kingTile = self.scene().itemAt(self.gridToXY(startX, startY), self.transform())
        else:
            kingTile = self.scene().itemAt(self.gridToXY(kingPosX, kingPosY), self.transform())

        if isCheck:
            kingTile.showCheck = True
            kingTile.loadTexture()
            kingTile.update()
        else:
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

    def showPromotionDialog(self):
        pieces = {'q': 'Queen', 'r': 'Rook', 'n': 'Knight', 'b': 'Bishop'}

        promotionDialog = QDialog(self.scene().views()[0])
        promotionDialog.setWindowTitle("Promote Pawn")
        layout = QGridLayout()

        addPieceToLabel = partial(self.addPieceChoice, promotionDialog=promotionDialog, layout=layout)
        list(map(lambda x: addPieceToLabel(*x), enumerate(pieces.items())))

        promotionDialog.setLayout(layout)
        promotionDialog.exec_()

    def addPieceChoice(self, index, pieceName, promotionDialog, layout):
        piece, name = pieceName
        pieceStyle = f":/pieces/{self.side}/{piece.lower()}"

        icon = QPixmap(pieceStyle)
        icon = icon.scaled(self.pieceSize, self.pieceSize, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        pieceLabel = QLabel()
        pieceLabel.setPixmap(icon)

        button = QPushButton(name)
        button.clicked.connect(lambda p=piece, s=pieceStyle: (self.promotePiece(p, s), promotionDialog.accept()))

        layout.addWidget(pieceLabel, index, 0)
        layout.addWidget(button, index, 1)

    def promotePiece(self, newPieceName, newPieceStyle):
        self.pieceName = newPieceName
        self.pieceStyle = newPieceStyle
        self.loadTexture()
        self.update()

        x, y = self.xyToGrid(self.x(), self.y())
        self.scene().chessboard.promotePawn(x, y, newPieceName)

    def playerMove(self, startX, startY, endX, endY, text=False):
        if [endX, endY] in self.legalMoves:
            self.scene().chessboard.movePiece(startX, startY, endX, endY)
            if not text and self.scene().chessboard.isPromotion(endX, endY):
                self.showPromotionDialog()

            castlingPerformed = self.scene().chessboard.isCastling()
            if castlingPerformed[0]:
                rookOldX, rookNewX = castlingPerformed[1]
                field = QRectF(self.gridToXY(rookOldX, endY).x(), self.gridToXY(rookOldX, endY).y(), self.pieceSize, self.pieceSize)
                rookItem = [item for item in self.scene().items(field) if (isinstance(item, Piece) and item is not self)]

                rookItem[0].setPos(self.gridToXY(rookNewX, endY))

            enPassantPerformed = self.scene().chessboard.isEnPassant()
            if enPassantPerformed[0]:
                x, y = enPassantPerformed[1]
                field = QRectF(self.gridToXY(x, y).x(), self.gridToXY(x, y).y(), self.pieceSize, self.pieceSize)
                targetItem = [item for item in self.scene().items(field) if (isinstance(item, Piece) and item is not self)]
            else:
                field = QRectF(self.gridToXY(endX, endY).x(), self.gridToXY(endX, endY).y(), self.pieceSize, self.pieceSize)
                targetItem = [item for item in self.scene().items(field) if (isinstance(item, Piece) and item is not self)]

            if targetItem:
                self.scene().removeItem(targetItem[0])

            self.setPos(self.gridToXY(endX, endY))
            self.scene().chessboard.playerMoved = True

            self.changeCheckKingTexture(startX, startY, *self.scene().chessboard.isCheck("light"))
            self.changeCheckKingTexture(startX, startY, *self.scene().chessboard.isCheck("dark"))

            isCheckmate = self.scene().chessboard.isCheckmate(not self.scene().chessboard.activePlayer == "light")
            if isCheckmate:
                self.scene().clock1.timer.stop()
                self.scene().clock2.timer.stop()

                msg = QMessageBox(self.scene().views()[0])
                msg.setWindowIcon(QIcon(QApplication.instance().style().standardPixmap(QStyle.SP_FileDialogInfoView)))
                msg.setIcon(QMessageBox.Information)
                msg.setText(f"Winner: {self.scene().chessboard.activePlayer} side!")
                msg.setWindowTitle("Game over")
                msg.show()

                self.scene().clock1.setOpacity(1.0)
                self.scene().clock2.setOpacity(1.0)
                self.scene().playerInput.setPlaceholderText("Game over!")
                self.scene().chessboard.activePlayer = None
        else:
            self.setPos(self.startPos)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.scene().chessboard.activePlayer == self.side:
                if not self.scene().chessboard.playerMoved:
                    self.setCursor(Qt.ClosedHandCursor)

                    self.startPos = self.pos()
                    startX, startY = self.xyToGrid(self.startPos.x(), self.startPos.y())

                    if not self.legalMoves:
                        self.legalMoves = self.scene().chessboard.getLegalMoves(startX, startY)

                    self.changeValidTileTexture(True)

                    super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.scene().chessboard.activePlayer == self.side:
            if not self.scene().chessboard.playerMoved:
                self.setOpacity(0.7)

                super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.scene().chessboard.activePlayer == self.side:
                if not self.scene().chessboard.playerMoved:
                    self.setCursor(Qt.OpenHandCursor)

                    newPos = self.pos()
                    endX, endY = self.xyToGrid(newPos.x(), newPos.y())
                    startX, startY = self.xyToGrid(self.startPos.x(), self.startPos.y())
                    self.playerMove(startX, startY, endX, endY)

                    self.setOpacity(1)
                    self.changeValidTileTexture(False)

                    super().mouseReleaseEvent(event)

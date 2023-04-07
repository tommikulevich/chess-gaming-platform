from PySide2.QtCore import Qt, QPointF, QRectF
from PySide2.QtWidgets import QGraphicsPixmapItem, QMenu, QAction, QMessageBox, QStyle, QApplication, QGridLayout, \
    QDialog, QLabel, QPushButton
from PySide2.QtGui import QPixmap, QIcon

from board.tile_item import Tile


class Piece(QGraphicsPixmapItem):
    def __init__(self, pieceName, side, x, y, pieceSize, parent=None):
        super().__init__(parent)

        # Parameters for game logic
        self.side = side
        self.pieceName = pieceName

        self.legalMoves = []
        self.isCheckLocal = False

        # Configuring graphical pieces
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

    # ---------------- Texture components ----------------

    def loadTexture(self):
        piecePixmap = QPixmap(self.pieceStyle)
        self.setPixmap(piecePixmap.scaled(self.pieceSize, self.pieceSize, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def changePieceTexture(self, pieceStyle, side):
        self.pieceTheme = pieceStyle
        pieceItems = [item for item in self.scene().items() if isinstance(item, Piece)]
        newStyle = f":/pieces/{self.pieceTheme}/{self.pieceName.lower()}"

        # Check if the player tries to set the same color as the opponent
        conflict = any((side == "light" and newStyle == item.pieceDarkSideStyle) or
                       (side == "dark" and newStyle == item.pieceLightSideStyle)
                       for item in pieceItems)

        if conflict:
            self.showColorConflictWindow()
            return

        [self.updatePiecesStyle(piece, side, newStyle) for piece in pieceItems]

    def updatePiecesStyle(self, item, side, newStyle):
        if side != item.side:   # If the piece is of another player
            return

        item.pieceTheme = self.pieceTheme
        item.pieceStyle = f":/pieces/{self.pieceTheme}/{item.pieceName.lower()}"
        item.loadTexture()
        item.update()

        if side == "light":
            item.pieceLightSideStyle = newStyle
        else:
            item.pieceDarkSideStyle = newStyle

    def changeValidTileTexture(self, isClick):
        [self.updateValidTile(tile, isClick) for tile in self.scene().items() if isinstance(tile, Tile)]

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

        kingTile.showCheck = isCheck
        kingTile.loadTexture()
        kingTile.update()

    def contextMenuEvent(self, event):
        # Right-click menu with options to change texture
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

    # ---------------- Additional windows ----------------

    def showColorConflictWindow(self):
        msg = QMessageBox(self.scene().mainWindow)
        msg.setWindowIcon(QIcon(QApplication.instance().style().standardPixmap(QStyle.SP_MessageBoxWarning)))
        msg.setIcon(QMessageBox.Warning)
        msg.setText("You can't choose this style because another side have it!")
        msg.setWindowTitle("Warning")
        msg.exec_()

    def showPromotionDialog(self):
        # Promotion dialog to choose a piece during the pawn promotion
        promotionDialog = QDialog(self.scene().views()[0])
        promotionDialog.setWindowTitle("Promote Pawn")
        promotionDialog.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        layout = QGridLayout()

        pieces = {'q': 'Queen', 'r': 'Rook', 'n': 'Knight', 'b': 'Bishop'}
        [self.addPieceChoice(*x, promotionDialog, layout) for x in enumerate(pieces.items())]

        promotionDialog.setLayout(layout)
        promotionDialog.exec_()

    def addPieceChoice(self, index, pieceName, promotionDialog, layout):
        piece, name = pieceName
        pieceStyle = f":/pieces/{self.pieceTheme}/{piece.lower()}"

        icon = QPixmap(pieceStyle)
        icon = icon.scaled(self.pieceSize / 2, self.pieceSize / 2, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        pieceLabel = QLabel()
        pieceLabel.setPixmap(icon)

        button = QPushButton(name)
        button.clicked.connect(lambda p=piece, s=pieceStyle: (self.promotePiece(p, s), promotionDialog.accept()))

        layout.addWidget(pieceLabel, index, 0)
        layout.addWidget(button, index, 1)

    # ---------------- Game components ----------------

    def xyToGrid(self, x, y):
        """Converts coordinates (x, y) to grid coordinates"""
        gridX = round(x / self.pieceSize)
        gridY = round(y / self.pieceSize)

        return gridX, gridY

    def gridToXY(self, gridX, gridY):
        """Converts grid coordinates to a QPointF object"""
        x = gridX * self.pieceSize
        y = gridY * self.pieceSize

        return QPointF(x, y)

    def promotePiece(self, newPieceName, newPieceStyle):
        # Changing piece name and texture
        self.pieceName = newPieceName
        self.pieceStyle = newPieceStyle
        self.loadTexture()
        self.update()

        # Performing promotion
        x, y = self.xyToGrid(self.x(), self.y())
        self.scene().logic.promotePawn(x, y, newPieceName)

    def playerMove(self, startX, startY, endX, endY, text=False):
        if [endX, endY] not in self.legalMoves:     # If a player wants to make an illegal move
            self.setPos(self.startPos)
            return

        # Performing move in logic
        self.scene().logic.movePiece(startX, startY, endX, endY)
        if not text and self.scene().logic.isPromotion(endX, endY):
            self.showPromotionDialog()

        # Checking and performing the castling
        castlingPerformed = self.scene().logic.isCastling()
        if castlingPerformed[0]:
            rookOldX, rookNewX = castlingPerformed[1]
            field = QRectF(self.gridToXY(rookOldX, endY).x(), self.gridToXY(rookOldX, endY).y(), self.pieceSize, self.pieceSize)
            rookItem = [item for item in self.scene().items(field) if (isinstance(item, Piece) and item is not self)]

            rookItem[0].setPos(self.gridToXY(rookNewX, endY))

        # Checking and performing en passant
        enPassantPerformed = self.scene().logic.isEnPassant()
        if enPassantPerformed[0]:
            x, y = enPassantPerformed[1]
            field = QRectF(self.gridToXY(x, y).x(), self.gridToXY(x, y).y(), self.pieceSize, self.pieceSize)
            targetItem = [item for item in self.scene().items(field) if (isinstance(item, Piece) and item is not self)]
        else:
            field = QRectF(self.gridToXY(endX, endY).x(), self.gridToXY(endX, endY).y(), self.pieceSize, self.pieceSize)
            targetItem = [item for item in self.scene().items(field) if (isinstance(item, Piece) and item is not self)]

        # Checking and performing capture
        if targetItem:
            self.scene().removeItem(targetItem[0])

        # Setting new position. End of the player move
        self.setPos(self.gridToXY(endX, endY))
        self.scene().logic.playerMoved = True

        # Changing tile texture under king piece if he is in check
        self.changeCheckKingTexture(startX, startY, *self.scene().logic.isCheck("light"))
        self.changeCheckKingTexture(startX, startY, *self.scene().logic.isCheck("dark"))

        # Checking the checkmate
        isCheckmate = self.scene().logic.isCheckmate(not self.scene().logic.activePlayer == "light")
        if isCheckmate:
            self.scene().gameOver()

    # ---------------- Clicking and dragging events ----------------

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        self.scene().errorLabel.clear()     # Clearing error label

        # If the game has not started or is over
        if self.scene().logic.activePlayer is None:
            self.scene().errorLabel.setText(self.scene().logic.getError(7))
            return

        # If a player tries to move an opponent's piece
        if self.scene().logic.activePlayer != self.side:
            self.scene().errorLabel.setText(self.scene().logic.getError(2))
            return

        # If the player has already made a move
        if self.scene().logic.playerMoved:
            self.scene().errorLabel.setText(self.scene().logic.getError(1))
            return

        self.setCursor(Qt.ClosedHandCursor)

        self.startPos = self.pos()
        startX, startY = self.xyToGrid(self.startPos.x(), self.startPos.y())

        # If legalMoves is empty - generate legal moves
        if not self.legalMoves:
            self.legalMoves = self.scene().logic.getLegalMoves(startX, startY)

        self.changeValidTileTexture(True)    # Change texture of the tiles on which the piece can move
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # If the new game has not started or a player tries to move an opponent's piece
        if self.scene().logic.activePlayer is None or self.scene().logic.activePlayer != self.side:
            return

        # If the player has already made a move
        if self.scene().logic.playerMoved:
            return

        # Making the piece a little transparent
        self.setOpacity(0.7)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # If the new game has not started or a player tries to move an opponent's piece
        if self.scene().logic.activePlayer is None or self.scene().logic.activePlayer != self.side:
            return

        # If the player has already made a move
        if self.scene().logic.playerMoved:
            return

        self.setCursor(Qt.OpenHandCursor)

        # Performing move
        newPos = self.pos()
        endX, endY = self.xyToGrid(newPos.x(), newPos.y())
        startX, startY = self.xyToGrid(self.startPos.x(), self.startPos.y())
        self.playerMove(startX, startY, endX, endY)

        # Changing back normal piece opacity and tile textures
        self.setOpacity(1)
        self.changeValidTileTexture(False)

        super().mouseReleaseEvent(event)

from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import QGraphicsPixmapItem, QMenu, QAction, QMessageBox, QStyle, QApplication
from PyQt5.QtGui import QPixmap, QIcon
from src import resources_rc


class Piece(QGraphicsPixmapItem):
    def __init__(self, pieceType, side, x, y, pieceSize, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.OpenHandCursor)
        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemSendsGeometryChanges, True)

        self.pieceType = pieceType
        self.pieceTypeAlg = self.getAlgNotation()
        self.side = "light" if side == "lightSide" else "dark"

        self.x = x
        self.y = y
        self.pieceSize = pieceSize
        self.setPos(x * self.pieceSize, y * self.pieceSize)
        self.startPos = None
        self.mousePressPos = None

        self.pieceStyle = f":/pieces/{self.side}/{self.pieceType}"
        self.pieceLightSideStyle = f":/pieces/light/{self.pieceType}"
        self.pieceDarkSideStyle = f":/pieces/dark/{self.pieceType}"
        self.loadTexture()

    def loadTexture(self):
        piecePixmap = QPixmap(self.pieceStyle)
        self.setPixmap(piecePixmap.scaled(self.pieceSize, self.pieceSize, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def getAlgNotation(self):
        pieceDict = {'pawn': 'P', 'rook': 'R', 'knight': 'N', 'bishop': 'B', 'queen': 'Q', 'king': 'K'}

        return pieceDict[self.pieceType]

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

    def changePieceTexture(self, pieceStyle, side):
        for item in self.scene().items():
            if isinstance(item, Piece):
                newStyle = f":/pieces/{pieceStyle}/{self.pieceType}"

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
                        item.pieceStyle = f":/pieces/{item.side}/{item.pieceType}"
                    else:
                        item.pieceStyle = f":/pieces/{pieceStyle}/{item.pieceType}"

                    item.loadTexture()
                    item.update()

                if side == "light":
                    item.pieceLightSideStyle = newStyle
                else:
                    item.pieceDarkSideStyle = newStyle

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mousePressPos = event.pos()
            self.startPos = self.pos()
            self.setCursor(Qt.ClosedHandCursor)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if event.buttons() & Qt.LeftButton:
            newPos = self.pos()
            gridPos = QPointF(round(newPos.x() / self.pieceSize) * self.pieceSize,
                              round(newPos.y() / self.pieceSize) * self.pieceSize)
            self.setPos(gridPos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.OpenHandCursor)

        super().mouseReleaseEvent(event)


class Pawn(Piece):
    def __init__(self, side, x, y, pieceSize, parent=None):
        super().__init__('pawn', side, x, y, pieceSize, parent)

    # Pawn-specific methods


class Rook(Piece):
    def __init__(self, side, x, y, pieceSize, parent=None):
        super().__init__('rook', side, x, y, pieceSize, parent)

    # Rook-specific methods


class Knight(Piece):
    def __init__(self, side, x, y, pieceSize, parent=None):
        super().__init__('knight', side, x, y, pieceSize, parent)

    # Knight-specific methods


class Bishop(Piece):
    def __init__(self, side, x, y, pieceSize, parent=None):
        super().__init__('bishop', side, x, y, pieceSize, parent)

    # Bishop-specific methods


class Queen(Piece):
    def __init__(self, side, x, y, pieceSize, parent=None):
        super().__init__('queen', side, x, y, pieceSize, parent)

    # Queen-specific methods


class King(Piece):
    def __init__(self, side, x, y, pieceSize, parent=None):
        super().__init__('king', side, x, y, pieceSize, parent)

    # King-specific methods

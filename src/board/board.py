from PySide2.QtCore import QSize, Qt, QRect
from PySide2.QtWidgets import QGraphicsScene
import itertools

from data import resources_qrc
from src.board.tile import Tile
from src.board.piece import Piece
from src.logic.chess_logic import ChessLogic


class Board(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mainWindow = parent

        self.boardSize = QSize(8, 8)
        self.tileSize = 100

        self.chessboard = ChessLogic()
        self.createTiles()
        self.createPieces()

        self.clock1 = self.mainWindow.clock1
        self.clock2 = self.mainWindow.clock2
        self.clock1.onClick = self.endPlayer1Move
        self.clock2.onClick = self.endPlayer2Move

        self.playerInput = self.mainWindow.playerInput
        self.playerInput.returnPressed.connect(self.textMove)

        self.textErrors = self.mainWindow.textErrors

    def createTiles(self):
        width, height = self.boardSize.width(), self.boardSize.height()
        [self.addItem(Tile(self.tileSize, i, j)) for i, j in itertools.product(range(width), range(height))]

    def createPieces(self):
        self.createSide("light", 7, 6)
        self.createSide("dark", 0, 1)

    def createSide(self, side, firstRow, secondRow):
        piece = "R" if side == "light" else "r"
        self.addItem(Piece(piece, side, 0, firstRow, self.tileSize))
        piece = "N" if side == "light" else "n"
        self.addItem(Piece(piece, side, 1, firstRow, self.tileSize))
        piece = "B" if side == "light" else "b"
        self.addItem(Piece(piece, side, 2, firstRow, self.tileSize))
        piece = "Q" if side == "light" else "q"
        self.addItem(Piece(piece, side, 3, firstRow, self.tileSize))
        piece = "K" if side == "light" else "k"
        self.addItem(Piece(piece, side, 4, firstRow, self.tileSize))
        piece = "B" if side == "light" else "b"
        self.addItem(Piece(piece, side, 5, firstRow, self.tileSize))
        piece = "N" if side == "light" else "n"
        self.addItem(Piece(piece, side, 6, firstRow, self.tileSize))
        piece = "R" if side == "light" else "r"
        self.addItem(Piece(piece, side, 7, firstRow, self.tileSize))

        piece = "P" if side == "light" else "p"
        [self.addItem(Piece(piece, side, x, secondRow, self.tileSize)) for x in range(self.boardSize.width())]

    def endPlayer1Move(self, event):
        if event.button() == Qt.LeftButton:
            if self.chessboard.activePlayer == "light":
                if self.chessboard.playerMoved:
                    self.changeActivePlayer()

                    self.clock1.setOpacity(0.7)
                    self.clock2.setOpacity(1.0)

                    self.clock1.timer.stop()
                    self.clock2.timer.start(1)
                else:
                    self.textErrors.setText(self.chessboard.getError(6))

        super().mousePressEvent(event)

    def endPlayer2Move(self, event):
        if event.button() == Qt.LeftButton:
            if self.chessboard.activePlayer == "dark":
                if self.chessboard.playerMoved:
                    self.changeActivePlayer()

                    self.clock1.setOpacity(1.0)
                    self.clock2.setOpacity(0.7)

                    self.clock1.timer.start(1)
                    self.clock2.timer.stop()
                else:
                    self.textErrors.setText(self.chessboard.getError(6))

        super().mousePressEvent(event)

    def changeActivePlayer(self):
        self.textErrors.clear()
        self.chessboard.playerMoved = False

        if self.chessboard.activePlayer == "light":
            self.chessboard.activePlayer = "dark"
            self.playerInput.setPlaceholderText("Input | Player №2")
        else:
            self.chessboard.activePlayer = "light"
            self.playerInput.setPlaceholderText("Input | Player №1")

        [piece.__setattr__('legalMoves', []) for piece in self.items() if isinstance(piece, Piece)]

    def textMove(self):
        self.textErrors.clear()

        moveText = self.playerInput.text()
        move = self.chessboard.parseMove(moveText)

        if move is None:
            self.textErrors.setText(self.chessboard.getError(0))
            return

        if isinstance(move, str):
            self.textErrors.setText(move)
            return

        if self.chessboard.playerMoved:
            self.textErrors.setText(self.chessboard.getError(1))
            return

        startX, startY, endX, endY, promotionPiece = move

        field = QRect(startX * self.tileSize, startY * self.tileSize, self.tileSize, self.tileSize)
        piece = [piece for piece in self.items(field) if (isinstance(piece, Piece))]

        if piece:
            piece = piece[0]    # always will be one element in piece list
            piece.legalMoves = self.chessboard.getLegalMoves(startX, startY)

            if piece.side == self.chessboard.activePlayer:
                piece.playerMove(startX, startY, endX, endY, text=True)

                if promotionPiece is not None:
                    piece.promotePiece(promotionPiece, f":/pieces/{self.chessboard.activePlayer}/{promotionPiece.lower()}")

                piece.update()
            else:
                self.textErrors.setText(self.chessboard.getError(2))
                return

        self.playerInput.clear()

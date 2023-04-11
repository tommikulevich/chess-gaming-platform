from PySide2.QtCore import QSize, Qt, QRect
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QGraphicsScene, QMessageBox, QApplication, QStyle
import itertools

from board.tile_item import Tile
from board.piece_item import Piece
from logic.chess_logic import ChessLogic


class Board(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mainWindow = parent

        # Board parameters
        self.boardSize = QSize(8, 8)
        self.tileSize = 100

        # Logic initializing
        self.logic = ChessLogic()

        # Creating tiles and pieces
        self.createTiles()
        self.createPieces()

        # Connecting signals to clocks when players click
        self.clock1 = self.mainWindow.clock1
        self.clock2 = self.mainWindow.clock2
        self.clock1.onClick = lambda event: self.endPlayerMove(event, "light")
        self.clock2.onClick = lambda event: self.endPlayerMove(event, "dark")

        # Connecting signals to error and input fields when players provide commands
        self.errorLabel = self.mainWindow.errorLabel
        self.playerInput = self.mainWindow.playerInput
        self.playerInput.returnPressed.connect(self.textMove)

    # ---------------- Creating scene items ----------------

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

    # ---------------- Configs ----------------

    def applyStyleConfig(self, boardStyleConfig, lightSideStyleConfig, darkSideStyleConfig):
        tile = [item for item in self.items() if isinstance(item, Tile)][0]
        tile.changeTileTexture(boardStyleConfig)

        lightPiece = [item for item in self.items() if isinstance(item, Piece) and item.side == "light"][0]
        lightPiece.changePieceTexture(lightSideStyleConfig, "light")

        darkPiece = [item for item in self.items() if isinstance(item, Piece) and item.side == "dark"][0]
        darkPiece.changePieceTexture(darkSideStyleConfig, "dark")

    def getStyleConfig(self):
        tile = [item for item in self.items() if isinstance(item, Tile)][0]
        boardStyleConfig = tile.boardStyleDark.split("/")[2]

        lightPiece = [item for item in self.items() if isinstance(item, Piece) and item.side == "light"][0]
        lightSideStyleConfig = lightPiece.pieceTheme

        darkPiece = [item for item in self.items() if isinstance(item, Piece) and item.side == "dark"][0]
        darkSideStyleConfig = darkPiece.pieceTheme

        return boardStyleConfig, lightSideStyleConfig, darkSideStyleConfig

    # ---------------- Game components ----------------

    def endPlayerMove(self, event, player):
        if event.button() != Qt.LeftButton:
            return

        # If the player tries to stop not his clock
        if self.logic.activePlayer != player:
            return

        # If the player has not yet made a move
        if not self.logic.playerMoved:
            self.errorLabel.setText(self.logic.getError(6))
            return

        # Changing active player and setting clocks
        self.changeActivePlayer()

        if player == "light":
            self.clock1.setOpacity(0.7)
            self.clock2.setOpacity(1.0)
            self.clock1.pauseTimer()
            self.clock2.startTimer()
        else:
            self.clock1.setOpacity(1.0)
            self.clock2.setOpacity(0.7)
            self.clock1.startTimer()
            self.clock2.pauseTimer()

    def changeActivePlayer(self):
        # Clearing error label and input field. Cleaning playerMoved variable
        self.errorLabel.clear()
        self.playerInput.clear()
        self.logic.playerMoved = False

        # Switching player
        if self.logic.activePlayer == "light":
            self.logic.activePlayer = "dark"
            self.playerInput.setPlaceholderText("Input | Player №2")
        else:
            self.logic.activePlayer = "light"
            self.playerInput.setPlaceholderText("Input | Player №1")

        # Cleaning all legalMoves variables from all pieces
        [piece.__setattr__('legalMoves', []) for piece in self.items() if isinstance(piece, Piece)]

    def textMove(self):
        # Clearing error label
        self.errorLabel.clear()

        # Read and parse text from input field
        moveText = self.playerInput.text()
        move = self.logic.parseMove(moveText)

        # If the player has already made a move
        if self.logic.playerMoved:
            self.errorLabel.setText(self.logic.getError(1))
            return

        # If parsing failed
        if move is None:
            self.errorLabel.setText(self.logic.getError(0))
            return

        # If disambiguating or incorrect move
        if isinstance(move, str):
            self.errorLabel.setText(move)
            return

        # Move processing after parsing
        startX, startY, endX, endY, promotionPiece = move

        field = QRect(startX * self.tileSize, startY * self.tileSize, self.tileSize, self.tileSize)
        piece = [piece for piece in self.items(field) if (isinstance(piece, Piece))]

        # If there are no pieces that can make that movement
        if not piece:
            self.errorLabel.setText(self.logic.getError(5))
            return

        piece = piece[0]    # always will be one element in piece list
        piece.legalMoves = self.logic.getLegalMoves(startX, startY)

        # If a player tries to move an opponent's piece
        if piece.side != self.logic.activePlayer:
            self.errorLabel.setText(self.logic.getError(2))
            return

        # Check of failed promotion
        if promotionPiece is not None and self.logic.isPromotion(endX, endY):
            self.errorLabel.setText(self.logic.getError(8))
            return

        # Perform move
        piece.playerMove(startX, startY, endX, endY, text=promotionPiece)
        piece.update()

        # Clearing input field
        self.playerInput.clear()

    def gameOver(self):
        # Stop the game and show game over message
        self.clock1.timer.stop()
        self.clock2.timer.stop()

        self.clock1.setOpacity(1.0)
        self.clock2.setOpacity(1.0)

        self.playerInput.setPlaceholderText("Game over!")

        self.showGameOverMessage()
        self.logic.activePlayer = None

    # ---------------- Additional windows ----------------

    def showGameOverMessage(self):
        msg = QMessageBox(self.views()[0])
        msg.setWindowIcon(QIcon(QApplication.instance().style().standardPixmap(QStyle.SP_FileDialogInfoView)))
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Winner: {self.logic.activePlayer} side!")
        msg.setWindowTitle("Game over")
        msg.show()

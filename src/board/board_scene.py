import itertools
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Tuple, Optional, Union

from PySide2.QtCore import (QSize, Qt, QRect, Signal)
from PySide2.QtGui import (QIcon)
from PySide2.QtWidgets import (
    QGraphicsScene, QMessageBox, QApplication, QStyle, QTableWidgetItem
)

from board.tile_item import Tile
from board.piece_item import Piece
from logic.chess_logic import ChessLogic
from bot.chess_bot import ChessBot
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from qt_windows.main_window import MainWindow
else:
    MainWindow = Any


class Board(QGraphicsScene):
    botMoveReady = Signal(tuple)

    def __init__(self, parent: MainWindow) -> None:
        super().__init__(parent)
        self.mainWindow = parent
        # Board parameters
        self.boardSize = QSize(8, 8)
        self.tileSize = 100

        # Logic initializing
        self.logic = ChessLogic()

        # Bot initializing
        self.chessBot: Optional[ChessBot] = None
        self.botSide: Optional[str] = None
        self.botMoveReady.connect(self.makeBotMove)

        # Create tiles and pieces
        self.createTiles()
        self.createPieces()

        # Connect signals to clocks when players click
        self.clock1 = self.mainWindow.clock1
        self.clock2 = self.mainWindow.clock2
        self.clock1.onClick = lambda event: self.endPlayerMove(event, "light")
        self.clock2.onClick = lambda event: self.endPlayerMove(event, "dark")

        # Connect signals to error and input fields when players provide cmds
        self.historyBlockTableWidget = self.mainWindow.historyBlockTableWidget
        self.errorLabel = self.mainWindow.errorLabel
        self.playerInputLineEdit = self.mainWindow.playerInputLineEdit

        self.playerInputLineEdit.returnPressed.connect(self.textMove)

    # ---------------------
    # Creating scene items
    # ---------------------

    def createTiles(self) -> None:
        width, height = self.boardSize.width(), self.boardSize.height()
        for i, j in itertools.product(range(width), range(height)):
            self.addItem(Tile(self.tileSize, i, j))

    def createPieces(self) -> None:
        self.createSide("light", 7, 6)
        self.createSide("dark", 0, 1)

    def createSide(self, side: str, firstRow: int, secondRow: int) -> None:
        piece = "R" if side == "light" else "r"
        self.addItem(Piece(piece, side, 0, firstRow, self.tileSize))
        self.logic.setPiece(0, firstRow, piece)

        piece = "N" if side == "light" else "n"
        self.addItem(Piece(piece, side, 1, firstRow, self.tileSize))
        self.logic.setPiece(1, firstRow, piece)

        piece = "B" if side == "light" else "b"
        self.addItem(Piece(piece, side, 2, firstRow, self.tileSize))
        self.logic.setPiece(2, firstRow, piece)

        piece = "Q" if side == "light" else "q"
        self.addItem(Piece(piece, side, 3, firstRow, self.tileSize))
        self.logic.setPiece(3, firstRow, piece)

        piece = "K" if side == "light" else "k"
        self.addItem(Piece(piece, side, 4, firstRow, self.tileSize))
        self.logic.setPiece(4, firstRow, piece)

        piece = "B" if side == "light" else "b"
        self.addItem(Piece(piece, side, 5, firstRow, self.tileSize))
        self.logic.setPiece(5, firstRow, piece)

        piece = "N" if side == "light" else "n"
        self.addItem(Piece(piece, side, 6, firstRow, self.tileSize))
        self.logic.setPiece(6, firstRow, piece)

        piece = "R" if side == "light" else "r"
        self.addItem(Piece(piece, side, 7, firstRow, self.tileSize))
        self.logic.setPiece(7, firstRow, piece)

        piece = "P" if side == "light" else "p"
        for x in range(self.boardSize.width()):
            self.addItem(Piece(piece, side, x, secondRow, self.tileSize))
        for x in range(self.boardSize.width()):
            self.logic.setPiece(x, secondRow, piece)

    # ---------------
    # Config support
    # ---------------

    def applyStyleConfig(self, boardStyleConfig: str,
                         lightSideStyleConfig: str,
                         darkSideStyleConfig: str) -> None:
        tile = [item for item in self.items() if isinstance(item, Tile)][0]
        tile.changeTileTexture(boardStyleConfig)

        lightPiece = [item for item in self.items() if isinstance(item, Piece)
                      and item.side == "light"][0]
        lightPiece.changePieceTexture(lightSideStyleConfig, "light")

        darkPiece = [item for item in self.items() if isinstance(item, Piece)
                     and item.side == "dark"][0]
        darkPiece.changePieceTexture(darkSideStyleConfig, "dark")

    def getStyleConfig(self) -> Tuple[str, str, str]:
        tile = [item for item in self.items() if isinstance(item, Tile)][0]
        boardStyleConfig = tile.boardStyleDark.split("/")[2]

        lightPiece = [item for item in self.items() if isinstance(item, Piece)
                      and item.side == "light"][0]
        lightSideStyleConfig = lightPiece.pieceTheme

        darkPiece = [item for item in self.items() if isinstance(item, Piece)
                     and item.side == "dark"][0]
        darkSideStyleConfig = darkPiece.pieceTheme

        return boardStyleConfig, lightSideStyleConfig, darkSideStyleConfig

    # ---------------
    # Game components
    # ---------------

    def endPlayerMove(self, event: Any, player: str) -> None:
        if event.button() != Qt.LeftButton:
            return

        # Check if the player tries to stop not his clock
        if self.logic.activePlayer != player:
            return

        # Check if the player tries to move his pieces if it's not his turn
        # (network mode)
        if self.mainWindow.mode == "2 players":
            if self.mainWindow.netActivePlayer \
                    != self.mainWindow.client.playerNick:
                self.errorLabel.setText(self.logic.getError(11))
                return

        # Check if the player tries to move his pieces if it's not his turn
        # (bot mode)
        if self.mainWindow.mode == "AI":
            if self.logic.activePlayer == self.botSide:
                self.errorLabel.setText(self.logic.getError(11))
                return

        # Check if the player has not yet made a move
        if not self.logic.playerMoved:
            self.errorLabel.setText(self.logic.getError(6))
            return

        # Change active player and set clocks
        self.changeActivePlayer(player)

        # TCP/IP support
        if self.mainWindow.mode == "2 players":
            # Send last performed move
            self.mainWindow.client.sendData(self.logic.lastMove)

            # Change active online player
            # Send end of turn time to "synchronize" timers
            if self.mainWindow.netActivePlayer == "light":
                time = self.mainWindow.clock1.leftTime
                leftTime = (
                    f"{time.hour()}:{time.minute()}"
                    f":{time.second()}:{time.msec()}"
                )
                self.mainWindow.client.sendData(f"time:{leftTime}")
                self.mainWindow.netActivePlayer = "dark"
            elif self.mainWindow.netActivePlayer == "dark":
                time = self.mainWindow.clock2.leftTime
                leftTime = (
                    f"{time.hour()}:{time.minute()}"
                    f":{time.second()}:{time.msec()}"
                )
                self.mainWindow.client.sendData(f"time:{leftTime}")
                self.mainWindow.netActivePlayer = "light"

    def changeClocks(self, player: str) -> None:
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

    def changeActivePlayer(self, player: str) -> None:
        # Clear error label and input field. Clean playerMoved variable
        self.errorLabel.clear()
        self.playerInputLineEdit.clear()
        self.logic.playerMoved = False

        # Switch player
        previousPlayer = self.logic.activePlayer
        if self.logic.activePlayer == "light":
            self.logic.activePlayer = "dark"
            self.playerInputLineEdit.setPlaceholderText("Input | Player №2")
        else:
            self.logic.activePlayer = "light"
            self.playerInputLineEdit.setPlaceholderText("Input | Player №1")

        # Clean all legalMoves variables from all pieces
        for piece in self.items():
            if isinstance(piece, Piece):
                piece.__setattr__('legalMoves', [])

        # Refresh history
        self.refreshHistoryBlock()

        # Check the checkmate
        isCheckmate = self.logic.isCheckmate(
            self.logic.activePlayer == "light")
        if isCheckmate:
            self.logic.activePlayer = previousPlayer
            self.gameOver()
            return

        if not self.mainWindow.isPlayback:
            self.changeClocks(player)   # Set game clocks

        # Bot support
        if self.mainWindow.mode == "AI" and self.chessBot:
            if self.logic.activePlayer == self.botSide:
                executor = ProcessPoolExecutor(
                    max_workers=multiprocessing.cpu_count())
                future = executor.submit(self.chessBot.getBotMove, self.logic)
                future.add_done_callback(self.botMove)

    def refreshHistoryBlock(self) -> None:
        newMove = self.logic.moveHistory[-1] if self.logic.moveHistory else ""
        rowCount = self.historyBlockTableWidget.rowCount()

        if len(self.logic.moveHistory) % 2 == 0:  # 'dark' side
            moveItem = QTableWidgetItem(newMove)
            moveItem.setTextAlignment(Qt.AlignCenter)
            self.historyBlockTableWidget.setItem(rowCount - 1, 1, moveItem)
        else:  # 'light' side
            self.historyBlockTableWidget.insertRow(rowCount)

            moveItem = QTableWidgetItem(newMove)
            moveItem.setTextAlignment(Qt.AlignCenter)
            self.historyBlockTableWidget.setItem(rowCount, 0, moveItem)

        self.historyBlockTableWidget.resizeColumnsToContents()
        self.historyBlockTableWidget.scrollToBottom()

    def textMove(self, text: Optional[str] = None) -> None:
        # Clear error label
        self.errorLabel.clear()
        self.errorLabel.setStyleSheet("color:rgb(227, 11, 92)")

        # Read and parse text move
        # (different actions depending on whether there is playback)
        if text:
            # Remove unnecessary symbols
            moveText = text.replace("+", "").replace("#", "").replace("ep", "")
        else:
            # Get move from line edit
            moveText = self.playerInputLineEdit.text()

            # Check if the player has already made a move
            if self.logic.playerMoved:
                self.errorLabel.setText(self.logic.getError(1))
                return

        move = self.logic.parseMove(moveText)   # Parse move

        # Check if the parsing failed
        if move is None:
            self.errorLabel.setText(self.logic.getError(0))
            return

        # Check if disambiguating or incorrect move
        if isinstance(move, str):
            self.errorLabel.setText(move)
            return

        # Move processing after parsing
        startX, startY, endX, endY, promotionPiece = move

        field = QRect(startX * self.tileSize, startY * self.tileSize,
                      self.tileSize, self.tileSize)
        piece = [piece for piece in self.items(field)
                 if (isinstance(piece, Piece))]

        # Check if there are no pieces that can make that movement
        if not piece:
            self.errorLabel.setText(self.logic.getError(5))
            return

        piece = piece[0]    # Always will be one element in piece list
        piece.legalMoves = self.logic.getLegalMoves(startX, startY)

        # Check if a player tries to move an opponent's piece
        if piece.side != self.logic.activePlayer:
            self.errorLabel.setText(self.logic.getError(2))
            return

        # Check if the player tries to move his pieces if it's not his turn
        # (network mode)
        if self.mainWindow.mode == "2 players":
            if piece.side != self.mainWindow.netActivePlayer \
                    and self.mainWindow.netActivePlayer \
                    != self.mainWindow.client.playerNick:
                self.errorLabel.setText(self.logic.getError(11))
                return

        # Check if the player tries to move his pieces if it's not his turn
        # (bot mode)
        if self.mainWindow.mode == "AI":
            if piece.side == self.botSide \
                    and self.logic.activePlayer != self.botSide:
                self.errorLabel.setText(self.logic.getError(11))
                return

        # Check for failed promotion
        if promotionPiece is not None and self.logic.isPromotion(endX, endY):
            self.errorLabel.setText(self.logic.getError(8))
            return

        # Perform move
        piece.playerMove(startX, startY, endX, endY, text=promotionPiece)
        piece.update()

        # Clear input field
        self.playerInputLineEdit.clear()

    def gameOver(self) -> None:
        # Stop the game and show game over message
        self.clock1.timer.stop()
        self.clock2.timer.stop()

        self.clock1.setOpacity(1.0)
        self.clock2.setOpacity(1.0)

        self.playerInputLineEdit.setPlaceholderText("Game over!")

        self.showGameOverMessage()
        self.logic.activePlayer = None

    # -----------
    # Bot support
    # -----------

    def startBot(self) -> None:
        self.chessBot = ChessBot()

    def botMove(self, future: Any = None) -> None:
        move = future.result()
        self.botMoveReady.emit(move)

    def makeBotMove(self, move: Tuple[Union[int, str], ...]) -> None:
        startX, startY, newX, newY = map(int, move[:4])
        promotionPiece = move[4] if len(move) > 4 else None
        sanMove = self.logic.coordsToSAN(startX, startY, newX, newY,
                                         promotionPiece)
        self.textMove(sanMove)

        # Test game bot-bot
        # self.botSide = 'light' if self.botSide == 'dark' else 'dark'

        self.changeActivePlayer(self.logic.activePlayer)
        print(f"[Bot Log] Move: {move} | {sanMove}")

    # ------------------
    # Additional windows
    # ------------------

    def showGameOverMessage(self) -> None:
        msg = QMessageBox(self.views()[0])
        msg.setWindowIcon(QIcon(QApplication.instance().style().standardPixmap(
            QStyle.SP_FileDialogInfoView)))
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Winner: {self.logic.activePlayer} side!")
        msg.setWindowTitle("Game over")
        msg.show()

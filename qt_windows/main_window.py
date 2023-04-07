from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QLineEdit, QAction, QDialog, QLabel, QStyle
from PySide2.QtGui import QBrush, QPixmap, QIcon

from qt_windows.start_dialog import StartDialog
from board.board_scene import Board
from clock.clock_item import Clock


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Loading ui from .ui file
        uiFile = QFile('data/ui/window_ui.ui')
        uiFile.open(QFile.ReadOnly)
        self.ui = QUiLoader().load(uiFile, None)
        self.setCentralWidget(self.ui)
        uiFile.close()

        # Window settings
        self.setWindowIcon(QIcon(":/pieces/yellow/k"))
        self.setWindowTitle("Chess Game")

        # Finding and configuring window elements
        self.errorLabel = self.findChild(QLabel, 'errors')
        self.playerInput = self.findChild(QLineEdit, 'input')
        self.boardView = self.findChild(QGraphicsView, 'board')
        self.clock1View = self.findChild(QGraphicsView, 'clock1')
        self.clock2View = self.findChild(QGraphicsView, 'clock2')
        self.startGameAction = self.findChild(QAction, 'startGame')
        self.startGameAction.triggered.connect(self.startNewGame)
        self.startGameAction.setIcon(self.style().standardIcon(QStyle.SP_ArrowForward))

        # Creating scenes
        self.board = None
        self.clock1 = None
        self.clock2 = None
        self.createScenes()

        self.show()

    def createScenes(self):
        # Creating clock for the first player ('light' side)
        self.clock1 = Clock(parent=self)
        self.clock1View.setScene(QGraphicsScene(self))
        self.clock1View.scene().setBackgroundBrush(QBrush(QPixmap(":/board/wood/light")))
        self.clock1View.scene().addItem(self.clock1)

        # Creating clock for the second player ('dark' side)
        self.clock2 = Clock(parent=self)
        self.clock2View.setScene(QGraphicsScene(self))
        self.clock2View.scene().setBackgroundBrush(QBrush(QPixmap(":/board/wood/light")))
        self.clock2View.scene().addItem(self.clock2)

        # Creating board
        self.board = Board(self)
        self.boardView.setScene(self.board)

    def startNewGame(self):
        startDialog = StartDialog(self)

        # Starting new game if accepted - clearing scenes and creating new elements and items
        if startDialog.exec_() == QDialog.Accepted:
            # Stop clocks to avoid errors
            self.clock1.timer.stop()
            self.clock2.timer.stop()

            # Clearing scenes and other items
            self.boardView.scene().clear()
            self.boardView.viewport().update()
            self.clock1View.scene().clear()
            self.clock1View.viewport().update()
            self.clock2View.scene().clear()
            self.clock2View.viewport().update()
            self.playerInput.returnPressed.disconnect()
            self.errorLabel.clear()

            # Creating new scenes
            self.createScenes()

            # Setting clocks
            timeH, timeMin, timeSec = startDialog.getGameTimeConfig()

            self.clock1.setTimer(timeH, timeMin, timeSec)
            self.clock1.startTimer()
            self.clock1.setOpacity(1)

            self.clock2.setTimer(timeH, timeMin, timeSec)
            self.clock2.setOpacity(0.7)

            # Setting input field
            self.playerInput.clear()
            self.playerInput.setReadOnly(False)
            self.playerInput.setPlaceholderText("Input | Player №1")

            # Setting active player
            self.board.logic.activePlayer = "light"

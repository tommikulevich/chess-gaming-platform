from PySide2.QtCore import QFile, Qt
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QLineEdit, QAction, QDialog, QLabel
from PySide2.QtGui import QBrush, QPixmap

from src.windows.start_window import StartWindow
from src.board.board import Board
from src.clock.clock import Clock


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        uiFile = QFile('data/qt_window.ui')
        uiFile.open(QFile.ReadOnly)
        self.ui = QUiLoader().load(uiFile, self)
        uiFile.close()

        self.startGameAction = None
        self.textErrors = None
        self.playerInput = None

        self.clock1 = None
        self.clock1View = None
        self.clock2 = None
        self.clock2View = None

        self.board = None
        self.boardView = None

        self.initGUI()
        self.ui.show()

    def initGUI(self):
        self.startGameAction = self.findChild(QAction, 'startGame')
        self.startGameAction.triggered.connect(self.startNewGame)

        self.textErrors = self.findChild(QLabel, 'errors')
        self.playerInput = self.findChild(QLineEdit, 'input')

        self.clock1 = Clock()
        self.clock1View = self.findChild(QGraphicsView, 'clock1')
        self.clock1View.setScene(QGraphicsScene(self))
        self.clock1View.scene().setBackgroundBrush(QBrush(QPixmap(":/board/wood/light")))
        self.clock1View.scene().addItem(self.clock1)

        self.clock2 = Clock()
        self.clock2View = self.findChild(QGraphicsView, 'clock2')
        self.clock2View.setScene(QGraphicsScene(self))
        self.clock2View.scene().setBackgroundBrush(QBrush(QPixmap(":/board/wood/light")))
        self.clock2View.scene().addItem(self.clock2)

        self.board = Board(self)
        self.boardView = self.findChild(QGraphicsView, 'board')
        self.boardView.setScene(self.board)

    def startNewGame(self):
        startDialog = StartWindow(self.ui)

        if startDialog.exec_() == QDialog.Accepted:
            self.boardView.scene().clear()
            self.boardView.viewport().update()
            self.clock1View.scene().clear()
            self.clock1View.viewport().update()
            self.clock2View.scene().clear()
            self.clock2View.viewport().update()
            self.playerInput.returnPressed.disconnect()
            self.initGUI()

            timeMin, timeSec = startDialog.getTime()

            self.clock1.setTimer(timeMin, timeSec)
            self.clock1.timer.stop()
            self.clock1.timer.start(1)
            self.clock1.setOpacity(1)

            self.clock2.setTimer(timeMin, timeSec)
            self.clock2.timer.stop()
            self.clock2.setOpacity(0.7)

            self.playerInput.clear()
            self.playerInput.setReadOnly(False)
            self.playerInput.setPlaceholderText("Input | Player №1")

            self.board.chessboard.activePlayer = "light"

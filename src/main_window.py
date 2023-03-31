from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QLineEdit, QTextEdit, QAction, QDialog
from PySide2.QtGui import QIcon, QBrush, QPixmap

from board import Board
from start_game_dialog import StartWindow


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uiFile = QFile('data/qt_main_window.ui')
        uiFile.open(QFile.ReadOnly)
        self.ui = QUiLoader().load(uiFile, self)
        uiFile.close()
        self.ui.setWindowIcon(QIcon(":/pieces/yellow/k"))

        self.clock1View = self.findChild(QGraphicsView, 'clock1')
        self.clock1View.setScene(QGraphicsScene(self))
        self.clock1View.scene().setBackgroundBrush(QBrush(QPixmap(":/board/wood/light")))

        self.clock2View = self.findChild(QGraphicsView, 'clock2')
        self.clock2View.setScene(QGraphicsScene(self))
        self.clock2View.scene().setBackgroundBrush(QBrush(QPixmap(":/board/wood/light")))

        self.playerInput = self.findChild(QLineEdit, 'input')
        self.outputBoard = self.findChild(QTextEdit, 'outputBoard')

        self.board = Board(parent=self)
        self.boardView = self.findChild(QGraphicsView, 'board')
        self.boardView.setScene(self.board)

        self.startGame = self.findChild(QAction, 'startGame')
        self.startGame.triggered.connect(self.startNewGame)

        self.ui.show()

    def startNewGame(self):
        startDialog = StartWindow(self.ui)

        if startDialog.exec_() == QDialog.Accepted:
            timeMin, timeSec = startDialog.getTime()
            self.board.clock1.setTimer(timeMin, timeSec)
            self.board.clock2.setTimer(timeMin, timeSec)
            self.board.clock1.timer.start(1)
            self.board.clock1.setOpacity(1)

            self.board.chessboard.activePlayer = "light"


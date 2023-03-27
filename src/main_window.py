from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QLineEdit, QTextEdit
from PyQt5.QtCore import Qt

from board import Board
from clock import Clock


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('data/qt_main_window.ui', self)
        self.setWindowIcon(QIcon(":/pieces/yellow/k"))

        self.clock1View = self.findChild(QGraphicsView, 'clock1')
        self.clock1View.setScene(QGraphicsScene(self))
        self.clock1View.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.clock1View.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.clock1View.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.clock2View = self.findChild(QGraphicsView, 'clock2')
        self.clock2View.setScene(QGraphicsScene(self))
        self.clock2View.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.clock2View.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.clock2View.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.playerInput = self.findChild(QLineEdit, 'input')
        self.outputBoard = self.findChild(QTextEdit, 'outputBoard')

        self.board = Board(parent=self)
        self.boardView = self.findChild(QGraphicsView, 'board')
        self.boardView.setScene(self.board)
        self.boardView.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.boardView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.boardView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.show()

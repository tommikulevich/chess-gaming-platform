from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QTextBrowser, QPlainTextEdit, QTextEdit, QLineEdit
from PyQt5.QtCore import Qt

from board import Board
from stockfish_game import StockfishGame


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('data/qt_main_window.ui', self)
        self.setWindowIcon(QIcon(":/pieces/yellow/king"))

        self.board = Board()
        self.view = self.findChild(QGraphicsView, 'graphicsView')
        self.view.setScene(self.board)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        # self.textGame = TextGame(self.findChild(QTextEdit, 'textEdit'), self.findChild(QLineEdit, 'lineEdit')

        self.show()

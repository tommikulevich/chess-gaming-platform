from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QGraphicsView
from PyQt5.QtCore import Qt
from chess_board import ChessBoard


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('src/qt_main_window.ui', self)
        self.setWindowIcon(QIcon(":/pieces/yellow/king"))

        self.board = ChessBoard()
        self.view = self.findChild(QGraphicsView, 'graphicsView')
        self.view.setScene(self.board)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.show()


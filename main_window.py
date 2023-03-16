from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from chess_board import ChessBoard
import resources_rc     # don't remove it!


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chess")
        self.setWindowIcon(QIcon(":/pieces/dark/king.png"))
        self.self.setFixedSize()

        self.board = ChessBoard()
        self.view = QGraphicsView(self.board, parent=self)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(self.view)
        self.setCentralWidget(widget)

        # To be continued (clock, text field ...)

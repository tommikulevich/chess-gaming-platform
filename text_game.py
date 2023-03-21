import chess
import chess.engine
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QApplication, QStyle


class TextGame:
    def __init__(self, outputWidget, inputWidget):
        self.inputWidget = inputWidget
        self.outputWidget = outputWidget

        self.textBoard = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci("stockfish/stockfish-windows-2022-x86-64-avx2.exe")

        self.outputWidget.setReadOnly(True)
        self.updateOutput()
        self.inputWidget.returnPressed.connect(self.movePiece)

    def movePiece(self):
        mistake = False

        try:
            move = chess.Move.from_uci(self.inputWidget.text())

            if move in self.textBoard.legal_moves:
                self.textBoard.push(move)
                self.updateOutput()
            else:
                mistake = True
                mistakeMsg = "Invalid move!"
        except ValueError:
            mistake = True
            mistakeMsg = "Invalid format!"
            # self.outputWidget.append("Invalid format!")

        if mistake:
            msg = QMessageBox()
            msg.setWindowIcon(QIcon(QApplication.instance().style().standardPixmap(QStyle.SP_MessageBoxWarning)))
            msg.setIcon(QMessageBox.Warning)
            msg.setText(mistakeMsg)
            msg.setWindowTitle("Mistake")
            msg.exec_()

        self.inputWidget.clear()

    def updateOutput(self):
        self.outputWidget.clear()

        self.outputWidget.append("     a b c d e f g h")
        self.outputWidget.append("     - - - - - - - -")

        for num, line in enumerate(str(self.textBoard).splitlines()[::-1], start=1):
            self.outputWidget.append(f'{num} | ' + line)
            self.outputWidget.setAlignment(Qt.AlignCenter)

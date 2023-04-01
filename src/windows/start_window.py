from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QDialog, QLabel, QSpinBox, QDialogButtonBox, QVBoxLayout

from data import resources_qrc


class StartWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon(":/pieces/yellow/k"))
        self.setWindowTitle("Start Game")
        self.setMinimumWidth(400)

        self.timeMinSpinBox = QSpinBox(self)
        self.timeMinSpinBox.setRange(0, 60)
        self.timeMinSpinBox.setValue(5)
        self.timeSecSpinBox = QSpinBox(self)
        self.timeSecSpinBox.setRange(0, 59)
        self.timeSecSpinBox.setValue(0)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Minutes:", self))
        layout.addWidget(self.timeMinSpinBox)
        layout.addWidget(QLabel("Seconds:", self))
        layout.addWidget(self.timeSecSpinBox)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok, self)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout.addWidget(buttonBox)

    def getTime(self):
        return self.timeMinSpinBox.value(), self.timeSecSpinBox.value()

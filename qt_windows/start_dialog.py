from PySide2.QtGui import QIcon, Qt, QFont
from PySide2.QtWidgets import QDialog, QLabel, QSpinBox, QDialogButtonBox, QGridLayout


class StartDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Window settings
        self.setWindowIcon(QIcon(":/pieces/yellow/k"))
        self.setWindowTitle("Start")
        self.setMinimumWidth(300)

        # Creating window elements
        self.enterGameTimeLabel = QLabel("Enter the game time:", self)
        self.enterGameTimeLabel.setStyleSheet("font-weight: bold")
        self.enterGameTimeLabel.setAlignment(Qt.AlignCenter)

        self.timeHourSpinBox = QSpinBox(self)
        self.timeHourSpinBox.setRange(0, 23)
        self.timeHourSpinBox.setValue(0)
        self.timeMinSpinBox = QSpinBox(self)
        self.timeMinSpinBox.setRange(0, 59)
        self.timeMinSpinBox.setValue(15)
        self.timeSecSpinBox = QSpinBox(self)
        self.timeSecSpinBox.setRange(0, 59)
        self.timeSecSpinBox.setValue(30)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok, self)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        labelFormat = QLabel("[H:Min:Sec]", self)
        labelFormat.setAlignment(Qt.AlignCenter)

        # Adding elements to a layout
        layout = QGridLayout(self)
        layout.addWidget(self.enterGameTimeLabel, 0, 0, 1, 3)
        layout.addWidget(labelFormat, 1, 0, 1, 3)
        layout.addWidget(self.timeHourSpinBox, 2, 0)
        layout.addWidget(self.timeMinSpinBox, 2, 1)
        layout.addWidget(self.timeSecSpinBox, 2, 2)
        layout.addWidget(buttonBox, 3, 0, 1, 3)

    def getGameTimeConfig(self):
        return self.timeHourSpinBox.value(), self.timeMinSpinBox.value(), self.timeSecSpinBox.value()

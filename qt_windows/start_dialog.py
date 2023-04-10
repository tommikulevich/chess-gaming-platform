from PySide2.QtCore import QFile
from PySide2.QtGui import QIcon
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QDialog, QLabel, QSpinBox, QDialogButtonBox, QButtonGroup, QRadioButton, QLineEdit, \
    QPushButton


class StartDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Loading ui from .ui file
        uiFile = QFile('data/ui/start_dialog_ui.ui')
        uiFile.open(QFile.ReadOnly)
        self.ui = QUiLoader().load(uiFile, None)
        uiFile.close()

        # Window settings
        self.ui.setWindowIcon(QIcon(":/pieces/yellow/k"))

        # --- Finding and configuring window components ---

        # OK Button
        self.buttonOK = self.ui.findChild(QDialogButtonBox, 'buttonOK')
        self.buttonOK.accepted.connect(self.ui.accept)
        self.buttonOK.rejected.connect(self.ui.reject)

        # Gaming time block
        self.timeHour = self.ui.findChild(QSpinBox, 'timeHourSpinBox')
        self.timeMin = self.ui.findChild(QSpinBox, 'timeMinSpinBox')
        self.timeSec = self.ui.findChild(QSpinBox, 'timeSecSpinBox')

        # Game mode block
        self.modeOnePlayer = self.ui.findChild(QRadioButton, 'modeOnePlayer')
        self.modeTwoPlayers = self.ui.findChild(QRadioButton, 'modeTwoPlayers')
        self.modeAI = self.ui.findChild(QRadioButton, 'modeAI')

        self.gameModes = QButtonGroup()
        self.gameModes.addButton(self.modeOnePlayer, 1)
        self.gameModes.addButton(self.modeTwoPlayers, 2)
        self.gameModes.addButton(self.modeAI, 3)

        # Network block
        self.netParam = self.ui.findChild(QLineEdit, 'netParam')\

        # Optional block
        self.jsonButton = self.ui.findChild(QPushButton, 'jsonButton')
        self.historyButton = self.ui.findChild(QPushButton, 'historyButton')
        self.statusLabel = self.ui.findChild(QLabel, 'statusLabel')
        # ... connecting buttons to functions needed ...

    def getGameTimeConfig(self):
        return self.timeHour.value(), self.timeMin.value(), self.timeSec.value()

    def getMode(self):
        return self.gameModes.checkedButton().text()

    def getNetParams(self):
        return self.netParam.text().split(':')

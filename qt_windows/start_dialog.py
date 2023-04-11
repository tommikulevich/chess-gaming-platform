import json
import os
import re
from PySide2.QtCore import QFile
from PySide2.QtGui import QIcon
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QDialog, QLabel, QSpinBox, QDialogButtonBox, QButtonGroup, QRadioButton, QLineEdit, \
    QPushButton, QFileDialog


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
        self.jsonButton.clicked.connect(self.loadConfig)
        self.historyButton.clicked.connect(self.loadHistory)

        # --- Style parameters (json) ---
        self.boardStyleConfig = None
        self.lightSideStyleConfig = None
        self.darkSideStyleConfig = None

    def getGameTime(self):
        return self.timeHour.value(), self.timeMin.value(), self.timeSec.value()

    def getMode(self):
        return self.gameModes.checkedButton().text()

    def getNetParams(self):
        return self.netParam.text().split(':')

    def getStyles(self):
        return self.boardStyleConfig, self.lightSideStyleConfig, self.darkSideStyleConfig

    def loadConfig(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        configPath, _ = QFileDialog.getOpenFileName(self, "Open Config File", "data/config", "JSON Files (*.json)", options=options)

        if os.path.isfile(configPath):
            with open(configPath, "r") as file:
                config = json.load(file)

            errors = self.validateConfig(config)    # Config parameters validation

            if not errors:
                initial = config.get("initial", {})
                style = config.get("style", {})

                # Time configuration
                timeConfig = initial.get("time", {})
                self.timeHour.setValue(timeConfig.get("hour", 0))
                self.timeMin.setValue(timeConfig.get("minute", 0))
                self.timeSec.setValue(timeConfig.get("second", 0))

                # Mode configuration
                mode = initial.get("mode", "1 player")
                if mode == "1 player":
                    self.modeOnePlayer.setChecked(True)
                elif mode == "2 players":
                    self.modeTwoPlayers.setChecked(True)
                elif mode == "AI":
                    self.modeAI.setChecked(True)

                # Network configuration
                netConfig = initial.get("network", {})
                ip = netConfig.get("ip", "")
                port = netConfig.get("port", "")
                self.netParam.setText(f"{ip}:{port}")

                # Style configuration
                board = style.get("board", {})
                self.boardStyleConfig = board.get("boardStyle", "standard")

                pieces = style.get("pieces", {})
                self.lightSideStyleConfig = pieces.get("lightSideStyle", "light")
                self.darkSideStyleConfig = pieces.get("darkSideStyle", "dark")

                # Updating status
                self.statusLabel.setText("Status: Config loaded successfully!")
                self.statusLabel.setStyleSheet("color:rgb(0, 170, 0)")
            else:
                self.statusLabel.setText("Status: Invalid config parameters (" + ", ".join(errors) + ").\nLoading failed!")
                self.statusLabel.setStyleSheet("color:rgb(227, 11, 92)")
        else:
            self.statusLabel.setText("Status: Config file not found or not selected!")
            self.statusLabel.setStyleSheet("color:rgb(227, 11, 92)")

    def validateConfig(self, config):
        errors = []
        initial = config.get("initial", {})
        style = config.get("style", {})

        # Checking time values
        timeConfig = initial.get("time", {})
        hour = timeConfig.get("hour", 0)
        minute = timeConfig.get("minute", 0)
        second = timeConfig.get("second", 0)

        if not (self.timeHour.minimum() <= hour <= self.timeHour.maximum() and
                self.timeMin.minimum() <= minute <= self.timeMin.maximum() and
                self.timeSec.minimum() <= second <= self.timeSec.maximum()):
            errors.append("time")

        # Checking mode
        mode = initial.get("mode", "1 player")
        if mode not in ["1 player", "2 players", "AI"]:
            errors.append("mode")

        # Checking network params
        netConfig = initial.get("network", {})

        ip = netConfig.get("ip", "")
        ipPattern = re.compile(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$')
        matchIP = ipPattern.match(ip)

        if matchIP:
            groups = matchIP.groups()
            valid = all(0 <= int(group) <= 255 for group in groups)

            if not valid:
                errors.append("ip")
        else:
            errors.append("ip")

        port = netConfig.get("port", "")
        portPattern = re.compile(r'^\d{1,5}$')
        matchPort = portPattern.match(port)

        if matchPort:
            valid = 0 <= int(port) <= 65535

            if not valid:
                errors.append("port")
        else:
            errors.append("port")

        # Checking style parameters
        board = style.get("board", {})
        boardStyle = board.get("boardStyle", "standard")
        if boardStyle not in ["standard", "rock", "wood"]:
            errors.append("board style")

        pieces = style.get("pieces", {})
        lightSideStyle = pieces.get("lightSideStyle", "light")
        darkSideStyle = pieces.get("darkSideStyle", "dark")
        if lightSideStyle not in ["light", "blue", "green", "red", "yellow"] \
                or darkSideStyle not in ["dark", "blue", "green", "red", "yellow"]\
                or lightSideStyle == darkSideStyle:
            errors.append("pieces style")

        return errors

    def loadHistory(self):
        pass

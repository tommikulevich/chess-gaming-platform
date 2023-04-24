import os
import re

import json
import sqlite3
from xml.etree.ElementTree import parse

from PySide2.QtCore import QFile
from PySide2.QtGui import QIcon
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QDialog, QLabel, QSpinBox, QDialogButtonBox, QButtonGroup, QRadioButton, QLineEdit, \
    QPushButton, QFileDialog, QComboBox


class StartDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # UI initializing and configuration
        self.ui = self.initUI('data/ui/start_dialog_ui.ui', ':/pieces/yellow/k')

        # UI components initializing and configuration
        self.okButton = self.initOkButton()
        self.timeSpinBoxes = self.initGameTimeBlock()
        self.netComboBox, self.netParamsLineEdit = self.initNetworkBlock()
        self.gameModesButtonGroup = self.initGameModeBlock()
        self.statusLabel = self.initOptionalBlock()

        # Styles and history parameters
        self.stylesFromConfig = {"boardStyle": None, "lightSideStyle": None, "darkSideStyle": None}
        self.historyFromFile = {"movesHistory": [], "clock1History": [], "clock2History": []}

    # -------------------
    # Window initializing
    # -------------------

    @staticmethod
    def initUI(uiPath, uiIcon):
        uiFile = QFile(uiPath)
        uiFile.open(QFile.ReadOnly)
        ui = QUiLoader().load(uiFile, None)     # Loading ui from .ui file
        ui.setWindowIcon(QIcon(uiIcon))
        uiFile.close()

        return ui

    def initOkButton(self):
        okButton = self.ui.findChild(QDialogButtonBox, 'ok')
        okButton.accepted.connect(self.ui.accept)
        okButton.rejected.connect(self.ui.reject)
        okButton = okButton.button(QDialogButtonBox.Ok)

        return okButton

    def initGameTimeBlock(self):
        timeHourSpinBox = self.ui.findChild(QSpinBox, 'timeHour')
        timeMinSpinBox = self.ui.findChild(QSpinBox, 'timeMin')
        timeSecSpinBox = self.ui.findChild(QSpinBox, 'timeSec')

        return timeHourSpinBox, timeMinSpinBox, timeSecSpinBox

    def initGameModeBlock(self):
        modeOnePlayerRadioButton = self.ui.findChild(QRadioButton, 'modeOnePlayer')
        modeTwoPlayersRadioButton = self.ui.findChild(QRadioButton, 'modeTwoPlayers')
        modeTwoPlayersRadioButton.toggled.connect(lambda toggled: self.netParamsLineEdit.setEnabled(toggled))
        modeAiRadioButton = self.ui.findChild(QRadioButton, 'modeAi')

        gameModesButtonGroup = QButtonGroup()
        gameModesButtonGroup.addButton(modeOnePlayerRadioButton, 1)
        gameModesButtonGroup.addButton(modeTwoPlayersRadioButton, 2)
        gameModesButtonGroup.addButton(modeAiRadioButton, 3)

        return gameModesButtonGroup

    def initNetworkBlock(self):
        netParamsLineEdit = self.ui.findChild(QLineEdit, 'netParams')
        netComboBox = self.ui.findChild(QComboBox, 'netComboBox')
        netComboBox.currentTextChanged.connect(self.setIpMask)

        return netComboBox, netParamsLineEdit

    def setIpMask(self, ipVersion):
        if ipVersion == "IPv4:port":
            self.netParamsLineEdit.setInputMask("000.000.000.000:00000")
            self.netParamsLineEdit.setText("127.0.0.1:5000")
            self.netParamsLineEdit.setMinimumWidth(self.netParamsLineEdit.fontMetrics().boundingRect(
                "000.000.000.000:00000").width())
        elif ipVersion == "IPv6:port":
            self.netParamsLineEdit.setInputMask("")
            self.netParamsLineEdit.setText("::1:5000")
            self.netParamsLineEdit.setMinimumWidth(self.netParamsLineEdit.fontMetrics().boundingRect(
                "0000:0000:0000:0000:0000:0000:0000:0000:000000").width())

    def initOptionalBlock(self):
        jsonButton = self.ui.findChild(QPushButton, 'jsonButton')
        historyButton = self.ui.findChild(QPushButton, 'historyButton')
        statusLabel = self.ui.findChild(QLabel, 'statusLabel')
        jsonButton.clicked.connect(self.loadConfig)
        historyButton.clicked.connect(self.loadHistory)

        return statusLabel

    # ----------------------------------------------
    # Getting options, history and config parameters
    # ----------------------------------------------

    def getGameTime(self):
        return tuple(spinBox.value() for spinBox in self.timeSpinBoxes)

    def getGameMode(self):
        return self.gameModesButtonGroup.checkedButton().text()

    def getNetParams(self):
        netParams = self.netParamsLineEdit.text().split(':')
        return ':'.join(netParams[:-1]), netParams[-1]

    def getStylesFromConfig(self):
        return tuple(self.stylesFromConfig.values())

    def getHistoryFromFiles(self):
        return tuple(self.historyFromFile.values())

    # --------------------------
    # Loading config and history
    # --------------------------

    def loadConfig(self):
        # Select config file (json)
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        configPath, _ = QFileDialog.getOpenFileName(self, "Open Config File", "data/config",
                                                    "JSON Files (*.json)", options=options)

        # Check if the config file exists
        if not os.path.isfile(configPath):
            self.statusLabel.setText("Status: Config file not found or not selected!")
            self.statusLabel.setStyleSheet("color:rgb(227, 11, 92)")
            return

        # Open config file
        with open(configPath, "r") as file:
            config = json.load(file)

        # Validate config parameters
        errors = self.validateConfig(config)
        if errors:
            self.statusLabel.setText("Status: Invalid config parameters (" + ", ".join(errors) + ").\nLoading failed!")
            self.statusLabel.setStyleSheet("color:rgb(227, 11, 92)")
            return

        # Getting parameters
        initialBlock = config.get("initial", {})
        styleBlock = config.get("style", {})

        # Time configuration
        timeConfig = initialBlock.get("time", {})
        self.timeSpinBoxes[0].setValue(timeConfig.get("hour", 0))
        self.timeSpinBoxes[1].setValue(timeConfig.get("minute", 0))
        self.timeSpinBoxes[2].setValue(timeConfig.get("second", 0))

        # Mode configuration
        modeConfig = initialBlock.get("mode", "1 player")
        modeRadioButtons = {
            "1 player": self.gameModesButtonGroup.button(1),
            "2 players": self.gameModesButtonGroup.button(2),
            "AI": self.gameModesButtonGroup.button(3)
        }
        if modeConfig in modeRadioButtons:
            modeRadioButtons[modeConfig].setChecked(True)

        # Network configuration
        netConfig = initialBlock.get("network", {})

        ip = netConfig.get("ip", "")
        ipv4Pattern = re.compile(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$')
        ipv6Pattern = re.compile(r'^(([0-9a-fA-F]{0,4}:){1,7}[0-9a-fA-F]{0,4}|::([0-9a-fA-F]{0,4}:){0,6}[0-9a-fA-F]{0,4}|([0-9a-fA-F]{0,4}:){1,6}:|([0-9a-fA-F]{0,4}:){1,5}:[0-9a-fA-F]{0,4}|([0-9a-fA-F]{0,4}:){1,4}(:[0-9a-fA-F]{0,4}){1,2}|([0-9a-fA-F]{0,4}:){1,3}(:[0-9a-fA-F]{0,4}){1,3}|([0-9a-fA-F]{0,4}:){1,2}(:[0-9a-fA-F]{0,4}){1,4}|[0-9a-fA-F]{0,4}:((:[0-9a-fA-F]{0,4}){1,5}|:)|:((:[0-9a-fA-F]{0,4}){1,6}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$')
        if ipv4Pattern.match(ip):
            self.netComboBox.setCurrentText("IPv4:port")
        elif ipv6Pattern.match(ip):
            self.netComboBox.setCurrentText("IPv6:port")

        port = netConfig.get("port", "")
        self.netParamsLineEdit.setText(f"{ip}:{port}")

        # Style configuration
        boardBlock = styleBlock.get("board", {})
        self.stylesFromConfig["boardStyle"] = boardBlock.get("boardStyle", "standard")

        piecesBlock = styleBlock.get("pieces", {})
        self.stylesFromConfig["lightSideStyle"] = piecesBlock.get("lightSideStyle", "light")
        self.stylesFromConfig["darkSideStyle"] = piecesBlock.get("darkSideStyle", "dark")

        # Update status
        self.statusLabel.setText("Status: Config loaded successfully!")
        self.statusLabel.setStyleSheet("color:rgb(0, 170, 0)")

    def validateConfig(self, config):
        errors = []

        initialBlock = config.get("initial", {})
        styleBlock = config.get("style", {})

        # Check game time values
        timeConfig = initialBlock.get("time", {})
        hour = timeConfig.get("hour", 0)
        minute = timeConfig.get("minute", 0)
        second = timeConfig.get("second", 0)
        timeValues = (hour, minute, second)

        if not all(self.timeSpinBoxes[i].minimum() <= timeValues[i] <= self.timeSpinBoxes[i].maximum() for i in range(3)):
            errors.append("time")

        # Check game mode
        modeConfig = initialBlock.get("mode", "1 player")
        if modeConfig not in ["1 player", "2 players", "AI"]:
            errors.append("mode")

        # Check network params
        netConfig = initialBlock.get("network", {})

        # 1) IP
        ip = netConfig.get("ip", "")
        ipv4Pattern = re.compile(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$')
        ipv6Pattern = re.compile(r'^(([0-9a-fA-F]{0,4}:){1,7}[0-9a-fA-F]{0,4}|::([0-9a-fA-F]{0,4}:){0,6}[0-9a-fA-F]{0,4}|([0-9a-fA-F]{0,4}:){1,6}:|([0-9a-fA-F]{0,4}:){1,5}:[0-9a-fA-F]{0,4}|([0-9a-fA-F]{0,4}:){1,4}(:[0-9a-fA-F]{0,4}){1,2}|([0-9a-fA-F]{0,4}:){1,3}(:[0-9a-fA-F]{0,4}){1,3}|([0-9a-fA-F]{0,4}:){1,2}(:[0-9a-fA-F]{0,4}){1,4}|[0-9a-fA-F]{0,4}:((:[0-9a-fA-F]{0,4}){1,5}|:)|:((:[0-9a-fA-F]{0,4}){1,6}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$')
        matchIPv4 = ipv4Pattern.match(ip)
        matchIPv6 = ipv6Pattern.match(ip)

        if matchIPv4:
            groups = matchIPv4.groups()

            if not all(0 <= int(group) <= 255 for group in groups):
                errors.append("ip")
        elif matchIPv6:
            if ip.count('::') > 1:
                errors.append("ip")
        else:
            errors.append("ip")

        # 2) Port
        port = netConfig.get("port", "")
        portPattern = re.compile(r'^\d{1,5}$')
        matchPort = portPattern.match(port)

        if matchPort:
            if not 0 <= int(port) <= 65535:
                errors.append("port")
        else:
            errors.append("port")

        # Check style parameters
        # 1) Board
        boardBlock = styleBlock.get("board", {})
        boardStyle = boardBlock.get("boardStyle", "standard")
        if boardStyle not in ["standard", "rock", "wood"]:
            errors.append("board style")

        # 2) Pieces
        piecesBlock = styleBlock.get("pieces", {})
        lightSideStyle = piecesBlock.get("lightSideStyle", "light")
        darkSideStyle = piecesBlock.get("darkSideStyle", "dark")
        if lightSideStyle not in ["light", "blue", "green", "red", "yellow"] \
                or darkSideStyle not in ["dark", "blue", "green", "red", "yellow"] \
                or lightSideStyle == darkSideStyle:
            errors.append("pieces style")

        return errors

    def loadHistory(self):
        # Select file with history (xml, db)
        historyPath, _ = QFileDialog.getOpenFileName(self, "Load History", "data/history/",
                                                     "History Files (*.xml *.db *.sqlite)")
        # Check if no file was selected
        if not historyPath:
            return

        # Get history data from files
        if historyPath.endswith('.db'):
            movesHistory, clock1History, clock2History = self.sqliteLoadHistory(historyPath)
            self.historyFromFile["movesHistory"] = movesHistory
            self.historyFromFile["clock1History"] = clock1History
            self.historyFromFile["clock2History"] = clock2History
        elif historyPath.endswith('.xml'):
            movesHistory, clock1History, clock2History = self.xmlLoadHistory(historyPath)
            self.historyFromFile["movesHistory"] = movesHistory
            self.historyFromFile["clock1History"] = clock1History
            self.historyFromFile["clock2History"] = clock2History
        else:
            self.statusLabel.setText("Status: History file has invalid type, not found or not selected!")
            self.statusLabel.setStyleSheet("color:rgb(227, 11, 92)")

            return

        # Change OK button text
        self.okButton.setText("Start playback")

        # Update status label
        self.statusLabel.setText("Status: History loaded successfully!")
        self.statusLabel.setStyleSheet("color:rgb(0, 170, 0)")

    def xmlLoadHistory(self, xmlPath):
        # Parse XML file
        tree = parse(xmlPath)
        root = tree.getroot()
        movesElem = root.find('moves')

        # Extract moves and end times
        allHistory = [(moveElem.text, moveElem.get('end_time', '')) for moveElem in movesElem.findall('move')]

        return self.splitAllHistory(allHistory)

    def sqliteLoadHistory(self, dbPath):
        # Connect to database
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()

        # Read data from history table
        cursor.execute('SELECT move, end_time FROM history')
        allHistory = cursor.fetchall()

        conn.close()

        return self.splitAllHistory(allHistory)

    @staticmethod
    def splitAllHistory(allHistory):
        # Split allHistory into separate lists
        times = [tuple(map(int, time.split(':'))) if time else None for _, time in allHistory]
        clock1History = []
        clock2History = []

        movesHistory = [move for move, _ in allHistory]
        clock1History.extend([time for i, time in enumerate(times) if i % 2 == 0 and time is not None])
        clock2History.extend([time for i, time in enumerate(times) if i % 2 == 1 and time is not None])

        return movesHistory, clock1History, clock2History

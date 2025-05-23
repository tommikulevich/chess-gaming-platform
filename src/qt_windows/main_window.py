import os
from datetime import datetime
from typing import Any, Optional, Tuple, List

import json
import sqlite3
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import (QFile, QEvent, Qt)
from PySide2.QtGui import (QBrush, QPixmap, QIcon, QTransform)
from PySide2.QtWidgets import (
    QMainWindow, QGraphicsView, QGraphicsScene, QLineEdit, QAction, QDialog,
    QLabel, QStyle, QFileDialog, QMenu, QTableWidget, QHeaderView, QGroupBox
)

from qt_windows.start_dialog import StartDialog
from qt_windows.playback_dialog import PlaybackDialog
from net.chess_client import ChessClient
from board.board_scene import Board
from clock.clock_item import Clock


class MainWindow(QMainWindow):
    isPlayback: bool
    startDialog: Optional[StartDialog]
    mode: Optional[str]
    errorLabel: QLabel
    playerInputLineEdit: QLineEdit
    historyBlockTableWidget: QTableWidget
    boardView: QGraphicsView
    clock1View: QGraphicsView
    clock2View: QGraphicsView
    saveHistoryMenu: QMenu
    settingsMenu: QMenu
    netActivePlayer: Optional[str]
    ip: Optional[str]
    port: Optional[int]
    client: Optional[ChessClient]
    board: Board
    clock1: Clock
    clock2: Clock

    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        self.isPlayback = False
        self.startDialog = None
        self.mode = None

        # UI initializing and configuration
        self.initUI('ui/main_window_ui.ui', ':/pieces/yellow/k',
                    'Chess Gaming Platform')

        # UI components initializing and configuration
        self.errorLabel, self.playerInputLineEdit, \
            self.historyBlockTableWidget = self.initTextElems()
        self.boardView, self.clock1View, self.clock2View = self.initViews()
        self.saveHistoryMenu = self.initGameMenu()
        self.settingsMenu = self.initSettingsMenu()

        # TCP/IP
        self.netActivePlayer = None
        self.ip, self.port = None, None
        self.client = None

        # Create scenes
        self.board, self.clock1, self.clock2 = None, None, None
        self.createScenes()

        self.show()

    # -------------------
    # Window initializing
    # -------------------

    def initUI(self, uiPath: str, uiIcon: str, uiName: str) -> Any:
        uiFile = QFile(uiPath)
        uiFile.open(QFile.ReadOnly)
        ui = QUiLoader().load(uiFile, None)  # Loading ui from .ui file
        uiFile.close()

        # Window configuration
        self.setCentralWidget(ui)
        self.setWindowTitle(uiName)
        self.setWindowIcon(QIcon(uiIcon))

        return ui

    def initTextElems(self) -> Tuple[QLabel, QLineEdit, QTableWidget]:
        errorLabel = self.findChild(QLabel, 'errors')
        playerInputLineEdit = self.findChild(QLineEdit, 'input')

        historyBlockTableWidget = self.findChild(QTableWidget, 'historyBlock')
        historyBlockTableWidget.setHorizontalHeaderLabels(['Light Side',
                                                           'Dark Side'])
        historyBlockTableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.Fixed)
        historyBlockTableWidget.resizeColumnsToContents()

        header = historyBlockTableWidget.horizontalHeader()
        headerFont = header.font()
        headerFont.setBold(True)
        header.setFont(headerFont)

        groupBoxHistoryLayout = \
            self.findChild(QGroupBox, 'groupBoxHistory').layout()
        groupBoxHistoryLayout.setAlignment(historyBlockTableWidget,
                                           Qt.AlignCenter)

        return errorLabel, playerInputLineEdit, historyBlockTableWidget

    def initViews(self) -> Tuple[QGraphicsView, QGraphicsView, QGraphicsView]:
        boardView = self.findChild(QGraphicsView, 'board')
        boardView.installEventFilter(self)
        clock1View = self.findChild(QGraphicsView, 'clock1')
        clock2View = self.findChild(QGraphicsView, 'clock2')

        return boardView, clock1View, clock2View

    def initGameMenu(self) -> QMenu:
        startGameAction = self.findChild(QAction, 'startGame')
        startGameAction.triggered.connect(self.startNewGame)
        startGameAction.setIcon(
            self.style().standardIcon(QStyle.SP_ArrowForward))

        saveHistoryMenu = self.findChild(QMenu, 'saveGameHistory')
        saveHistoryMenu.setIcon(
            self.style().standardIcon(QStyle.SP_DialogSaveButton))

        xmlSaveAction = self.findChild(QAction, 'xmlSave')
        xmlSaveAction.triggered.connect(self.xmlSaveHistory)
        xmlSaveAction.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        sqliteSaveAction = self.findChild(QAction, 'sqliteSave')
        sqliteSaveAction.triggered.connect(self.sqliteSave)
        sqliteSaveAction.setIcon(
            self.style().standardIcon(QStyle.SP_MediaPlay))

        return saveHistoryMenu

    def initSettingsMenu(self) -> QMenu:
        settingsMenu = self.findChild(QMenu, 'settings')

        saveConfigAction = self.findChild(QAction, 'saveConfig')
        saveConfigAction.triggered.connect(self.saveConfig)
        saveConfigAction.setIcon(
            self.style().standardIcon(QStyle.SP_DialogSaveButton))

        loadStyleAction = self.findChild(QAction, 'loadStyle')
        loadStyleAction.triggered.connect(self.loadStylesFromConfig)
        loadStyleAction.setIcon(
            self.style().standardIcon(QStyle.SP_DialogOpenButton))

        return settingsMenu

    def createScenes(self) -> None:
        # Create clock for the first player ('light' side)
        self.clock1 = Clock(parent=self)
        self.clock1View.setScene(QGraphicsScene(self))
        self.clock1View.scene().setBackgroundBrush(
            QBrush(QPixmap(":/board/wood/light")))
        self.clock1View.scene().addItem(self.clock1)

        # Create clock for the second player ('dark' side)
        self.clock2 = Clock(parent=self)
        self.clock2View.setScene(QGraphicsScene(self))
        self.clock2View.scene().setBackgroundBrush(
            QBrush(QPixmap(":/board/wood/light")))
        self.clock2View.scene().addItem(self.clock2)

        # Create board
        self.board = Board(self)
        self.boardView.setScene(self.board)

    def eventFilter(self, source: Any, event: QEvent) -> bool:
        if source == self.boardView and event.type() == QEvent.Resize:
            baseWidth, baseHeight = 800, 800
            scaleX, scaleY = float(self.boardView.width()) / baseWidth, \
                float(self.boardView.height()) / baseHeight
            transform = QTransform()
            transform.scale(scaleX, scaleY)
            self.boardView.setTransform(transform)

        return super(MainWindow, self).eventFilter(source, event)

    # -----------------------
    # Start new game/playback
    # -----------------------

    def startNewGame(self) -> None:
        # Show start window with game options
        self.startDialog = StartDialog(self)

        # Start new game if accepted: clear scenes and create new elems / items
        if self.startDialog.ui.exec_() == QDialog.Accepted:
            # Stop clocks to avoid errors
            self.clock1.timer.stop()
            self.clock2.timer.stop()

            # Clear scenes and other items
            self.boardView.scene().clear()
            self.boardView.viewport().update()
            self.clock1View.scene().clear()
            self.clock1View.viewport().update()
            self.clock2View.scene().clear()
            self.clock2View.viewport().update()
            self.playerInputLineEdit.returnPressed.disconnect()
            self.errorLabel.clear()
            self.historyBlockTableWidget.setRowCount(0)

            self.createScenes()  # Create new scenes
            self.board.logic.activePlayer = "light"  # Setting active player

            # Set styles (if config file was selected)
            styles = self.startDialog.getStylesFromConfig()
            if all(style is not None for style in styles):
                self.board.applyStyleConfig(*styles)

            # History playback (if history file was selected)
            histories = self.startDialog.getHistoryFromFiles()
            if all(history for history in histories):
                self.startHistoryPlayback(*histories)
                return

            # Unlock settings and savings (before first game)
            self.settingsMenu.setEnabled(True)
            self.saveHistoryMenu.setEnabled(True)

            # Set parameters according to the game mode
            self.mode = self.startDialog.getGameMode()
            if self.mode == "1 player":
                self.setClocks()
            if self.mode == "2 players":    # TCP/IP
                self.errorLabel.setText("Wait for a connection...")
                self.errorLabel.setStyleSheet("color:rgb(0, 170, 0)")

                self.ip, self.port = self.startDialog.getNetParams()[0], \
                    int(self.startDialog.getNetParams()[1])
                self.client = ChessClient(self.ip, self.port, self)

                # Server will wait for players before start
                self.board.logic.activePlayer = None
            elif self.mode == "AI":
                self.setClocks()
                self.board.botSide = "dark"
                self.board.startBot()

            # Set input field
            self.playerInputLineEdit.clear()
            self.playerInputLineEdit.setReadOnly(False)
            self.playerInputLineEdit.setPlaceholderText("Input | Player №1")

    def setClocks(self) -> None:
        timeHour, timeMin, timeSec = self.startDialog.getGameTime()

        self.clock1.setTimer(timeHour, timeMin, timeSec)
        self.clock1.startTimer()
        self.clock1.setOpacity(1)

        self.clock2.setTimer(timeHour, timeMin, timeSec)
        self.clock2.setOpacity(0.7)

    def startHistoryPlayback(self, movesHistory: List[str],
                             clock1History: List[Tuple[int, int, int, int]],
                             clock2History: List[Tuple[int, int, int, int]]) \
            -> None:
        self.isPlayback = True
        playbackDialog = PlaybackDialog(movesHistory, clock1History,
                                        clock2History, self)
        playbackDialog.ui.exec_()

    # --------------
    # Config support
    # --------------

    def loadStylesFromConfig(self) -> None:
        # Choose config file (json)
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        configPath, _ = QFileDialog.getOpenFileName(
            self, "Open Config File", "config", "JSON Files (*.json)",
            options=options)

        # Check if the config file exists
        if not os.path.isfile(configPath):
            self.errorLabel.setText("Config file not found or not selected!")
            self.errorLabel.setStyleSheet("color:rgb(227, 11, 92)")
            return

        # Open config file
        with open(configPath, "r") as file:
            config = json.load(file)

        # Validate config parameters
        errors = self.validateStylesFromConfig(config)
        if errors:
            self.errorLabel.setText(
                "Invalid config parameters ("
                + ", ".join(errors) + ").\nLoading failed!")
            self.errorLabel.setStyleSheet("color:rgb(227, 11, 92)")
            return

        # Style configuration
        styleBlock = config.get("style", {})

        boardBlock = styleBlock.get("board", {})
        boardStyleConfig = boardBlock.get("boardStyle", "standard")

        pieces = styleBlock.get("pieces", {})
        lightSideStyleConfig = pieces.get("lightSideStyle", "light")
        darkSideStyleConfig = pieces.get("darkSideStyle", "dark")

        styles = boardStyleConfig, lightSideStyleConfig, darkSideStyleConfig
        self.board.applyStyleConfig(*styles)

        # Update status
        self.errorLabel.setText("Config loaded successfully!")
        self.errorLabel.setStyleSheet("color:rgb(0, 170, 0)")

    @staticmethod
    def validateStylesFromConfig(config: Any) -> List[str]:
        errors = []
        style = config.get("style", {})

        # Check style parameters
        # 1) Board
        board = style.get("board", {})
        boardStyle = board.get("boardStyle", "standard")
        if boardStyle not in ["standard", "rock", "wood"]:
            errors.append("board style")

        # 2) Pieces
        pieces = style.get("pieces", {})
        lightSideStyle = pieces.get("lightSideStyle", "light")
        darkSideStyle = pieces.get("darkSideStyle", "dark")
        if lightSideStyle not in ["light", "blue", "green", "red", "yellow"] \
                or darkSideStyle not in \
                ["dark", "blue", "green", "red", "yellow"] \
                or lightSideStyle == darkSideStyle:
            errors.append("pieces style")

        return errors

    def saveConfig(self) -> None:
        # Select file to save config (json)
        currentDatetime = datetime.now()
        formattedDatetime = currentDatetime.strftime("%d-%m-%Y_%H-%M-%S")
        fileName = f"config/config_{formattedDatetime}.json"
        configPath, _ = QFileDialog.getSaveFileName(self, "Save Config File",
                                                    fileName, "JSON (*.json)")
        config = {}

        # Check if no file was selected
        if not configPath:
            return

        # Completing config with parameters
        boardStyle, lightSideStyle, darkSideStyle = self.board.getStyleConfig()
        config["style"] = {
            "board": {
                "boardStyle": boardStyle
            },
            "pieces": {
                "lightSideStyle": lightSideStyle,
                "darkSideStyle": darkSideStyle
            }
        }

        hours, mins, secs = self.startDialog.getGameTime()
        mode = self.startDialog.getGameMode()
        ip, port = self.startDialog.getNetParams()
        config["initial"] = {
            "time": {
                "hour": hours,
                "minute": mins,
                "second": secs
            },
            "mode": mode,
            "network": {
                "ip": ip,
                "port": port
            }
        }

        # Write config to file
        with open(configPath, "w") as file:
            json.dump(config, file, indent=4)

        # Update status
        self.errorLabel.setText("Config saved successfully!")
        self.errorLabel.setStyleSheet("color:rgb(0, 170, 0)")

    # ---------------
    # History support
    # ---------------

    def xmlSaveHistory(self) -> None:
        # Creating XML element representing a move with the given move and time
        def createMoveElem(move, time):
            moveElem = Element('move')
            moveElem.set('end_time', time)
            moveElem.text = move

            return moveElem

        # Select file to save history (xml)
        currentDatetime = datetime.now()
        formattedDatetime = currentDatetime.strftime("%d-%m-%Y_%H-%M-%S")
        fileName = f"history/history_{formattedDatetime}.xml"
        xmlPath, _ = QFileDialog.getSaveFileName(self, "Save History",
                                                 fileName, "XML (*.xml)")

        # Check if no file was selected
        if not xmlPath:
            return

        # Extract histories
        history = self.getAllHistory()

        game = Element('history')
        movesElem = SubElement(game, 'moves')

        moves = [createMoveElem(move, time) for move, time in history]
        movesElem.extend(moves)

        # Write XML structure to file
        xmlPretty = minidom.parseString(
            tostring(game)).toprettyxml(indent='\t')
        with open(xmlPath, 'w') as f:
            f.write(xmlPretty)

        # Update status
        self.errorLabel.setText("History in XML saved successfully!")
        self.errorLabel.setStyleSheet("color:rgb(0, 170, 0)")

    def sqliteSave(self) -> None:
        # Select file to save history (database)
        currentDatetime = datetime.now()
        formattedDatetime = currentDatetime.strftime("%d-%m-%Y_%H-%M-%S")
        fileName = f"history/history_{formattedDatetime}.db"
        dbPath, _ = QFileDialog.getSaveFileName(
            self, "Save History", fileName, "SQLite Database (*.db *.sqlite)")

        # Check if no file was selected
        if not dbPath:
            return

        # Extract histories
        history = self.getAllHistory()

        # Open a connection to the SQLite database
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()

        # Drop (if exist) and create history table
        cursor.execute('''DROP TABLE IF EXISTS history''')
        cursor.execute('''
                CREATE TABLE history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    move TEXT,
                    end_time TEXT
                )
            ''')

        # Insert game data into history table
        [cursor.execute('INSERT INTO history (move, end_time) VALUES (?, ?)',
                        (move, endTime)) for move, endTime in history]

        # Apply changes to database and close connection
        conn.commit()
        conn.close()

        # Update status label
        self.errorLabel.setText("History in SQLite3 saved successfully!")
        self.errorLabel.setStyleSheet("color:rgb(0, 170, 0)")

    def getAllHistory(self) -> List[Tuple[str, str]]:
        # Format time tuple into a string with the format 'hh:mm:ss:zz'
        def formatTime(time):
            if time is None:
                return ''

            return f'{time[0]}:{time[1]}:{time[2]}:{time[3]}'

        # Extract moves and end times from actual game
        movesHistory = self.board.logic.moveHistory
        clock1History = self.clock1.timeHistory
        clock2History = self.clock2.timeHistory

        # Combining moves and time histories
        allHistory = [
            (move, formatTime(clock1History[i // 2])
             if i % 2 == 0 and i // 2 < len(clock1History)
             else formatTime(clock2History[i // 2])
             if i % 2 == 1 and i // 2 < len(clock2History)
             else '')
            for i, move in enumerate(movesHistory)
        ]

        return allHistory

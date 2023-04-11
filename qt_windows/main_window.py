import json
import os
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QLineEdit, QAction, QDialog, QLabel, QStyle, \
    QFileDialog, QMenu
from PySide2.QtGui import QBrush, QPixmap, QIcon

from qt_windows.start_dialog import StartDialog
from board.board_scene import Board
from clock.clock_item import Clock


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.startDialog = None

        # Loading ui from .ui file
        uiFile = QFile('data/ui/main_window_ui.ui')
        uiFile.open(QFile.ReadOnly)
        self.ui = QUiLoader().load(uiFile, None)
        self.setCentralWidget(self.ui)
        uiFile.close()

        # Window settings
        self.setWindowIcon(QIcon(":/pieces/yellow/k"))
        self.setWindowTitle("Chess Game")

        # Finding and configuring window elements
        self.errorLabel = self.findChild(QLabel, 'errors')
        self.playerInput = self.findChild(QLineEdit, 'input')
        self.boardView = self.findChild(QGraphicsView, 'board')
        self.clock1View = self.findChild(QGraphicsView, 'clock1')
        self.clock2View = self.findChild(QGraphicsView, 'clock2')
        self.startGameAction = self.findChild(QAction, 'startGame')
        self.settingsMenu = self.findChild(QMenu, 'settings')
        self.startGameAction.triggered.connect(self.startNewGame)
        self.startGameAction.setIcon(self.style().standardIcon(QStyle.SP_ArrowForward))
        self.saveConfigAction = self.findChild(QAction, 'saveConfig')
        self.saveConfigAction.triggered.connect(self.saveConfig)
        self.saveConfigAction.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.loadStyleAction = self.findChild(QAction, 'loadStyle')
        self.loadStyleAction.triggered.connect(self.loadStyleFromConfig)
        self.loadStyleAction.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))

        # Creating scenes
        self.board = None
        self.clock1 = None
        self.clock2 = None
        self.createScenes()

        self.show()

    def createScenes(self):
        # Creating clock for the first player ('light' side)
        self.clock1 = Clock(parent=self)
        self.clock1View.setScene(QGraphicsScene(self))
        self.clock1View.scene().setBackgroundBrush(QBrush(QPixmap(":/board/wood/light")))
        self.clock1View.scene().addItem(self.clock1)

        # Creating clock for the second player ('dark' side)
        self.clock2 = Clock(parent=self)
        self.clock2View.setScene(QGraphicsScene(self))
        self.clock2View.scene().setBackgroundBrush(QBrush(QPixmap(":/board/wood/light")))
        self.clock2View.scene().addItem(self.clock2)

        # Creating board
        self.board = Board(self)
        self.boardView.setScene(self.board)

    def startNewGame(self):
        self.startDialog = StartDialog(self)

        # Starting new game if accepted - clearing scenes and creating new elements and items
        if self.startDialog.ui.exec_() == QDialog.Accepted:
            # Unlock settings (before first game)
            self.settingsMenu.setEnabled(True)

            # Stop clocks to avoid errors
            self.clock1.timer.stop()
            self.clock2.timer.stop()

            # Clearing scenes and other items
            self.boardView.scene().clear()
            self.boardView.viewport().update()
            self.clock1View.scene().clear()
            self.clock1View.viewport().update()
            self.clock2View.scene().clear()
            self.clock2View.viewport().update()
            self.playerInput.returnPressed.disconnect()
            self.errorLabel.clear()

            # Creating new scenes
            self.createScenes()

            # Setting styles
            styles = self.startDialog.getStyles()
            if not any(style is None for style in styles):
                self.board.applyStyleConfig(*styles)

            # Setting clocks
            timeH, timeMin, timeSec = self.startDialog.getGameTime()

            self.clock1.setTimer(timeH, timeMin, timeSec)
            self.clock1.startTimer()
            self.clock1.setOpacity(1)

            self.clock2.setTimer(timeH, timeMin, timeSec)
            self.clock2.setOpacity(0.7)

            # Setting input field
            self.playerInput.clear()
            self.playerInput.setReadOnly(False)
            self.playerInput.setPlaceholderText("Input | Player №1")

            # Setting active player
            self.board.logic.activePlayer = "light"

    def loadStyleFromConfig(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        configPath, _ = QFileDialog.getOpenFileName(self, "Open Config File", "data/config", "JSON Files (*.json)", options=options)

        if os.path.isfile(configPath):
            with open(configPath, "r") as file:
                config = json.load(file)

            errors = self.validateStyleFromConfig(config)  # Config parameters validation

            if not errors:
                style = config.get("style", {})

                board = style.get("board", {})
                boardStyleConfig = board.get("boardStyle", "standard")

                pieces = style.get("pieces", {})
                lightSideStyleConfig = pieces.get("lightSideStyle", "light")
                darkSideStyleConfig = pieces.get("darkSideStyle", "dark")

                styles = boardStyleConfig, lightSideStyleConfig, darkSideStyleConfig
                self.board.applyStyleConfig(*styles)

                # Updating status
                self.errorLabel.setText("Config loaded successfully!")
                self.errorLabel.setStyleSheet("color:rgb(0, 170, 0)")
            else:
                self.errorLabel.setText("Invalid config parameters (" + ", ".join(errors) + ").\nLoading failed!")
                self.errorLabel.setStyleSheet("color:rgb(227, 11, 92)")
        else:
            self.errorLabel.setText("Config file not found or not selected!")
            self.errorLabel.setStyleSheet("color:rgb(227, 11, 92)")

    @staticmethod
    def validateStyleFromConfig(config):
        errors = []
        style = config.get("style", {})

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

    def saveConfig(self):
        config = {}
        configPath, _ = QFileDialog.getSaveFileName(self, "Save Config File", "data/config/config.json", "JSON (*.json)")

        if not configPath:
            return

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
        mode = self.startDialog.getMode()
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

        with open(configPath, "w") as file:
            json.dump(config, file, indent=4)

        self.errorLabel.setText("Config saved successfully!")
        self.errorLabel.setStyleSheet("color:rgb(0, 170, 0)")

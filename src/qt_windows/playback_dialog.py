from typing import Any, Optional, Tuple, List, TYPE_CHECKING

from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import (QFile, QTime, QTimer, Qt)
from PySide2.QtGui import (QIcon)
from PySide2.QtWidgets import (QDialog, QPushButton, QLabel, QStyle)

if TYPE_CHECKING:
    from qt_windows.main_window import MainWindow
else:
    MainWindow = Any


class PlaybackDialog(QDialog):
    ui: Any
    nextButton: QPushButton
    autoButton: QPushButton
    exitButton: QPushButton
    moveLabel: QLabel
    movesHistory: List[str]
    clock1History: List[Tuple[int, int, int, int]]
    clock2History: List[Tuple[int, int, int, int]]
    currentMoveIndex: int
    playbackDuration: int
    playbackTimer: QTimer

    def __init__(self, movesHistory: List[str],
                 clock1History: List[Tuple[int, int, int, int]],
                 clock2History: List[Tuple[int, int, int, int]],
                 parent: Optional[MainWindow] = None) -> None:
        super().__init__(parent)
        self.mainWindow = parent

        # UI initializing and configuration
        self.ui = self.initUI('ui/playback_dialog_ui.ui', ':/pieces/yellow/k')

        # UI components initializing and configuration
        self.nextButton, self.autoButton, self.exitButton = self.initButtons()
        self.moveLabel = self.initLabels()

        # History parameters
        self.movesHistory = movesHistory
        self.clock1History = clock1History
        self.clock2History = clock2History
        self.currentMoveIndex = 0

        # Playback timer parameters
        self.playbackDuration = 500
        self.playbackTimer = QTimer(self)
        self.playbackTimer.timeout.connect(self.nextMove)

    # -------------------
    # Window initializing
    # -------------------

    @staticmethod
    def initUI(uiPath: str, uiIcon: str) -> Any:
        uiFile = QFile(uiPath)
        uiFile.open(QFile.ReadOnly)
        ui = QUiLoader().load(uiFile, None)  # Loading ui from .ui file
        ui.setWindowIcon(QIcon(uiIcon))
        ui.setWindowFlags(
            Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        uiFile.close()

        return ui

    def initButtons(self) -> Tuple[QPushButton, QPushButton, QPushButton]:
        nextButton = self.ui.findChild(QPushButton, 'nextButton')
        nextButton.setIcon(self.style().standardIcon(QStyle.SP_ArrowForward))
        nextButton.clicked.connect(self.nextMove)
        autoButton = self.ui.findChild(QPushButton, 'autoButton')
        autoButton.clicked.connect(self.autoPlayback)
        autoButton.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        exitButton = self.ui.findChild(QPushButton, 'exitButton')
        exitButton.clicked.connect(self.exitPlayback)

        return nextButton, autoButton, exitButton

    def initLabels(self) -> QLabel:
        moveLabel = self.ui.findChild(QLabel, 'moveLabel')

        return moveLabel

    # -----------------------
    # Playback implementation
    # -----------------------

    def autoPlayback(self) -> None:
        self.playbackTimer.start(self.playbackDuration)

        self.autoButton.setText("Pause")
        self.autoButton.clicked.disconnect()
        self.autoButton.clicked.connect(self.pausePlayback)

        self.nextButton.setDisabled(True)

    def pausePlayback(self) -> None:
        self.playbackTimer.stop()

        self.autoButton.setText("Auto")
        self.autoButton.clicked.disconnect()
        self.autoButton.clicked.connect(self.autoPlayback)

        self.nextButton.setDisabled(False)

    def endPlayback(self) -> None:
        self.playbackTimer.stop()

        self.mainWindow.board.logic.activePlayer = None
        self.mainWindow.isPlayback = False
        self.mainWindow.settingsMenu.setEnabled(False)
        self.mainWindow.saveHistoryMenu.setEnabled(False)
        self.mainWindow.playerInputLineEdit.setPlaceholderText(
            "Playback ended!")

        self.nextButton.setDisabled(True)
        self.autoButton.setDisabled(True)

    def exitPlayback(self) -> None:
        self.endPlayback()
        self.ui.reject()

    def nextMove(self) -> None:
        move = self.movesHistory[self.currentMoveIndex]     # Get move
        self.moveLabel.setText(f"Move: {move}")
        self.mainWindow.board.textMove(text=move)  # Perform move

        # Setting the end time of a move on the player's clock
        # 'light' side
        if self.currentMoveIndex % 2 == 0 \
                and self.currentMoveIndex // 2 < len(self.clock1History):
            time = self.clock1History[self.currentMoveIndex // 2]
            self.mainWindow.clock1.leftTime = QTime(*time)
            self.mainWindow.clock1.update()
        # 'dark' side
        elif self.currentMoveIndex % 2 == 1 \
                and self.currentMoveIndex // 2 < len(self.clock2History):
            time = self.clock2History[self.currentMoveIndex // 2]
            self.mainWindow.clock2.leftTime = QTime(*time)
            self.mainWindow.clock2.update()

        self.currentMoveIndex += 1
        # Check if all moves have been made
        if self.currentMoveIndex >= len(self.movesHistory):
            self.endPlayback()
            return

        # Change player (needed for performing move)
        self.mainWindow.board.changeActivePlayer(
            self.mainWindow.board.logic.activePlayer)

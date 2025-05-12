import sys
from PySide2.QtWidgets import QApplication

import qt_windows.resources_qrc  # noqa: F401
from qt_windows.main_window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())

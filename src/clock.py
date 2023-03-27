from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtWidgets import QGraphicsEllipseItem


class Clock(QGraphicsEllipseItem):
    def __init__(self, onClick=None, parent=None):
        super().__init__(0, 0, 200, 200, parent)
        self.setBrush(QBrush(QColor("green")))
        self.onClick = onClick

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.onClick is not None:
                self.onClick(event)

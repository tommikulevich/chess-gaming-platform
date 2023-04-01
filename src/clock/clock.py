from PySide2.QtCore import Qt, QTimer, QTime, QRectF
from PySide2.QtGui import QColor, QBrush, QPainter, QPen
from PySide2.QtWidgets import QGraphicsRectItem


class Clock(QGraphicsRectItem):
    def __init__(self, size=300, parent=None):
        super().__init__(0, 0, size, size, parent)
        self.setBrush(QBrush(QColor("white")))
        self.setPen(QPen(Qt.black, 5))
        self.setOpacity(0.7)
        self.onClick = None

        self.size = size
        self.tran = int(self.size / 2)

        self.timer = QTimer()
        self.time = QTime(0, 0, 0)
        self.timer.timeout.connect(self.updateTime)

    def setTimer(self, timeMin, timeSec):
        self.time = QTime(0, timeMin, timeSec)

    def updateTime(self):
        self.time = self.time.addMSecs(-1)
        if self.time == QTime(0, 0, 0):
            self.timer.stop()
        self.update()

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.black)
        painter.translate(self.tran, self.tran)

        numMSec = 1000
        numSec = 60
        numMin = 6

        list(map(lambda i: self.drawDivisions(painter, i, numMin), range(numSec)))

        font = painter.font()
        fontSize = int(4)
        font.setPointSize(fontSize)
        painter.setFont(font)
        painter.setPen(Qt.black)

        list(map(lambda i: self.drawNumSec(painter, i, numMin), range(1, numSec+1)))

        self.drawMinArrow(painter, numMin, numSec)
        self.drawSecArrow(painter, numMin)
        self.drawMSecArrow(painter, numMin, numSec, numMSec)

    def drawDivisions(self, painter, i, numMin):
        painter.save()
        painter.rotate(numMin * i)

        if i % 5 == 0:
            painter.setPen(Qt.red)
            painter.drawLine(0, -(self.tran - 20), 0, -(self.tran - 5))
        else:
            painter.setPen(Qt.gray)
            painter.drawLine(0, -(self.tran - 15), 0, -(self.tran - 5))

        painter.restore()

    def drawNumSec(self, painter, i, numMin):
        painter.save()
        painter.rotate(numMin * i)
        painter.translate(0, -(self.tran - 30))
        painter.rotate(-numMin * i)

        if i % 5 == 0:
            painter.setPen(Qt.red)
            painter.drawText(QRectF(-10, -10, 20, 20), Qt.AlignCenter, str(i))

        painter.restore()

    def drawMinArrow(self, painter, numMin, numSec):
        painter.setPen(Qt.black)
        painter.save()
        painter.rotate(-numMin * (self.time.minute() + (self.time.second() / float(numSec))))
        painter.drawLine(0, 0, 0, -(self.tran - 45))
        painter.restore()

    def drawSecArrow(self, painter, numMin):
        painter.setPen(Qt.red)
        painter.save()
        painter.rotate(-numMin * self.time.second())
        painter.drawLine(0, 0, 0, -(self.tran - 25))
        painter.restore()

    def drawMSecArrow(self, painter, numMin, numSec, numMSec):
        painter.setPen(Qt.blue)
        painter.save()
        painter.rotate(-numMin * numSec * (self.time.msec() / float(numMSec)))
        painter.drawLine(0, 0, 0, -(self.tran - 15))
        painter.restore()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.onClick is not None:
                self.onClick(event)

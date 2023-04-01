from PySide2.QtCore import Qt, QTimer, QTime, QRectF
from PySide2.QtGui import QColor, QBrush, QPainter, QPen
from PySide2.QtWidgets import QGraphicsEllipseItem


class Clock(QGraphicsEllipseItem):
    def __init__(self, size=320, parent=None):
        super().__init__(0, 0, size, size)
        self.mainWindow = parent
        self.onClick = None

        # Setting design of the clock
        self.setBrush(QBrush(QColor("white")))
        self.setPen(QPen(Qt.black, 4))
        self.setOpacity(0.7)
        self.size = size
        self.tran = int(self.size / 2)
        self.font = int(self.size / 50)

        # Initializing timer
        self.timer = QTimer()
        self.time = QTime(0, 0, 0)
        self.timer.timeout.connect(self.updateTime)

    # ---------------- Setting timer ----------------

    def setTimer(self, timeH, timeMin, timeSec):
        self.time = QTime(timeH, timeMin, timeSec)

    def updateTime(self):
        self.time = self.time.addMSecs(-1)

        # If timer ends - game is over
        if self.time == QTime(0, 0, 0):
            self.timer.stop()
            self.mainWindow.board.changeActivePlayer()
            self.mainWindow.board.gameOver()

        self.update()

    # ---------------- Main paint element  ----------------

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw main divs
        painter.setPen(Qt.black)
        painter.translate(self.tran, self.tran)
        list(map(lambda i: self.drawMainDivs(painter, i), range(60)))

        # Draw hour numbers
        font = painter.font()
        font.setPointSize(self.font)
        painter.setFont(font)
        painter.setPen(Qt.black)
        list(map(lambda i: self.drawHourNums(painter, i), range(1, 13)))

        # Draw inner divs
        list(map(lambda i: self.drawInnerDivs(painter, i), range(10 * 5)))

        # Draw millisecond numbers
        font = painter.font()
        font.setPointSize(self.font-1)
        painter.setFont(font)
        painter.setPen(Qt.black)
        list(map(lambda inum: self.drawMSecNum(painter, *inum), enumerate([0, 200, 400, 600, 800])))

        # Draw arrows
        self.drawHourArrow(painter)
        self.drawMinArrow(painter)
        self.drawSecArrow(painter)
        self.drawMSecArrow(painter)

    # ---------------- Drawing elements: numbers and divs  ----------------

    def drawMainDivs(self, painter, i):
        painter.save()

        painter.rotate(6 * i)
        if i % 5 == 0:
            painter.setPen(Qt.black)
            painter.drawLine(0, -(self.tran - 20), 0, -(self.tran - 5))
        else:
            painter.setPen(Qt.gray)
            painter.drawLine(0, -(self.tran - 15), 0, -(self.tran - 5))

        painter.restore()

    def drawHourNums(self, painter, i):
        painter.save()

        painter.rotate(6 * i * 5)
        painter.translate(0, -(self.tran - 30))
        painter.rotate(-6 * i * 5)

        painter.setPen(Qt.darkBlue)
        painter.drawText(QRectF(-10, -10, 20, 20), Qt.AlignCenter, str(i))

        painter.restore()

    def drawInnerDivs(self, painter, i):
        painter.save()

        painter.rotate(360 / (10 * 5) * i)
        if i % 10 == 0:
            painter.setPen(Qt.red)
            painter.drawLine(0, -(0.4 * self.tran) + 5, 0, -(0.4 * self.tran) - 5)
        else:
            painter.setPen(Qt.black)
            painter.drawLine(0, -(0.4 * self.tran) + 4, 0, -(0.4 * self.tran) - 4)

        painter.restore()

    def drawMSecNum(self, painter, i, num):
        painter.save()

        painter.rotate(360 / 5 * i)
        painter.translate(0, -(0.33 * self.tran) + 10)
        painter.rotate(-360 / 5 * i)
        painter.drawText(QRectF(-10, -10, 20, 20), Qt.AlignCenter, str(num))

        painter.restore()

    # ---------------- Drawing elements: arrows ----------------

    def drawHourArrow(self, painter):
        painter.save()

        painter.setPen(QPen(Qt.black, 3))
        hours = self.time.hour() if self.time.hour() <= 12 else self.time.hour() - 12
        painter.rotate(-30 * (hours + (self.time.minute() / float(60)) + (self.time.second() / float(60 * 60))))
        painter.drawLine(0, 0, 0, -(self.tran - 90))

        painter.restore()

    def drawMinArrow(self, painter):
        painter.save()

        painter.setPen(QPen(Qt.black, 2))
        painter.rotate(-6 * (self.time.minute() + (self.time.second() / float(60))))
        painter.drawLine(0, 0, 0, -(self.tran - 60))

        painter.restore()

    def drawSecArrow(self, painter):
        painter.save()

        painter.setPen(Qt.red)
        painter.rotate(-6 * self.time.second())
        painter.drawLine(0, 0, 0, -(self.tran - 20))

        painter.restore()

    def drawMSecArrow(self, painter):
        painter.save()

        painter.setPen(Qt.blue)
        painter.rotate(-6 * 60 * (self.time.msec() / float(1000)))
        painter.drawLine(0, 0, 0, -(0.4 * self.tran + 4))

        painter.restore()

    # ---------------- Clicking events ----------------

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        if self.onClick is None:
            return

        self.onClick(event)

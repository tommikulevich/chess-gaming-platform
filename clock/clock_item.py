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
        self.gameTime = QTime(0, 0, 0, 0)
        self.endTime = QTime(0, 0, 0, 0)
        self.leftTime = QTime(0, 0, 0, 0)
        self.beforePause = QTime(0, 0, 0, 0)
        self.afterPause = QTime(0, 0, 0, 0)
        self.timer.timeout.connect(self.updateTime)

    # ---------------- Setting timer ----------------

    def setTimer(self, timeH, timeMin, timeSec):
        self.gameTime = QTime(timeH, timeMin, timeSec, 0)

    def setEndTime(self):
        self.endTime = QTime.currentTime()
        self.endTime = self.endTime.addMSecs(self.gameTime.msec() + 1000 * (self.gameTime.second() + 60 * self.gameTime.minute() + 60 * 60 * self.gameTime.hour()))

    def updateTime(self):
        currentTime = QTime.currentTime()
        self.leftTime = self.endTime.addMSecs(-currentTime.msec() - 1000 * (currentTime.second() + 60 * currentTime.minute() + 60 * 60 * currentTime.hour()))

        # If timer ends - game is over
        if self.leftTime <= QTime(0, 0, 0, 0):
            self.timer.stop()
            self.mainWindow.board.changeActivePlayer()
            self.mainWindow.board.gameOver()

        self.update()

    def pauseTimer(self):
        self.timer.stop()
        self.beforePause = QTime.currentTime()

    def startTimer(self):
        # When timer starts at the beginning of the game
        if self.leftTime == QTime(0, 0, 0, 0):
            self.setEndTime()
            self.timer.start(1)
            return

        self.afterPause = QTime.currentTime()
        timeDiff = self.afterPause.addMSecs(-self.beforePause.msec() - 1000 * (self.beforePause.second() + 60 * self.beforePause.minute() + 60 * 60 * self.beforePause.hour()))

        self.endTime = self.endTime.addMSecs(timeDiff.msec() + 1000 * (timeDiff.second() + 60 * timeDiff.minute() + 60 * 60 * timeDiff.hour()))
        self.timer.start(1)

    # ---------------- Main paint element  ----------------

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw main divs
        painter.setPen(Qt.black)
        painter.translate(self.tran, self.tran)
        [self.drawMainDivs(painter, i) for i in range(60)]

        # Draw hour numbers
        font = painter.font()
        font.setPointSize(self.font)
        painter.setFont(font)
        painter.setPen(Qt.black)
        [self.drawHourNums(painter, i) for i in range(1, 13)]

        # Draw inner divs
        [self.drawInnerDivs(painter, i) for i in range(10 * 5)]

        # Draw millisecond numbers
        font = painter.font()
        font.setPointSize(self.font-1)
        painter.setFont(font)
        painter.setPen(Qt.black)
        [self.drawMSecNum(painter, *inum) for inum in enumerate([0, 200, 400, 600, 800])]

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
        hours = self.leftTime.hour() if self.leftTime.hour() <= 12 else self.leftTime.hour() - 12
        painter.rotate(-30 * (hours + (self.leftTime.minute() / float(60)) + (self.leftTime.second() / float(60 * 60))))
        painter.drawLine(0, 0, 0, -(self.tran - 80))

        painter.restore()

    def drawMinArrow(self, painter):
        painter.save()

        painter.setPen(QPen(Qt.black, 2))
        painter.rotate(-6 * (self.leftTime.minute() + (self.leftTime.second() / float(60))))
        painter.drawLine(0, 0, 0, -(self.tran - 65))

        painter.restore()

    def drawSecArrow(self, painter):
        painter.save()

        painter.setPen(Qt.red)
        painter.rotate(-6 * self.leftTime.second())
        painter.drawLine(0, 0, 0, -(self.tran - 20))

        painter.restore()

    def drawMSecArrow(self, painter):
        painter.save()

        painter.setPen(Qt.blue)
        painter.rotate(-6 * 60 * (self.leftTime.msec() / float(1000)))
        painter.drawLine(0, 0, 0, -(0.4 * self.tran + 4))

        painter.restore()

    # ---------------- Clicking events ----------------

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        if self.onClick is None:
            return

        self.onClick(event)
        super().mousePressEvent(event)

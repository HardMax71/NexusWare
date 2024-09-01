from PySide6.QtCore import Qt, QPropertyAnimation, Property
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import (
    QWidget
)


class LoadingSpinner(QWidget):
    def __init__(self, parent=None, size=40, num_dots=8, dot_size=10):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.num_dots = num_dots
        self.dot_size = dot_size
        self.counter = 0

        self.animation = QPropertyAnimation(self, b"rotation")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(360)
        self.animation.setLoopCount(-1)
        self.animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for i in range(self.num_dots):
            x = self.width() / 2 + (self.width() / 2 - self.dot_size) * \
                (1 - i / self.num_dots) * 0.7 * \
                (1 - (self.counter + i) % self.num_dots / self.num_dots)
            y = self.height() / 2
            painter.setBrush(QColor(100, 100, 100, 255 * (1 - (self.counter + i) % self.num_dots / self.num_dots)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(x - self.dot_size / 2), int(y - self.dot_size / 2), self.dot_size, self.dot_size)

    def showEvent(self, event):
        self.animation.start()

    def hideEvent(self, event):
        self.animation.stop()

    def get_rotation(self):
        return self.counter

    def set_rotation(self, value):
        self.counter = value
        self.update()

    rotation = Property(int, get_rotation, set_rotation)

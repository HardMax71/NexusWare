from PySide6.QtCore import Qt, QPropertyAnimation, Signal
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import (
    QWidget, QGraphicsOpacityEffect, QGraphicsDropShadowEffect
)


class ToggleSwitch(QWidget):
    toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 30)
        self._checked = False

        # Opacity effect for smooth transitions
        self._opacity = QGraphicsOpacityEffect()
        self._opacity.setOpacity(0.8)
        self.setGraphicsEffect(self._opacity)
        self._animation = QPropertyAnimation(self._opacity, b"opacity", self)
        self._animation.setDuration(100)

        # Shadow effect to make the thumb more visible
        self._shadow_effect = QGraphicsDropShadowEffect(self)
        self._shadow_effect.setBlurRadius(10)
        self._shadow_effect.setOffset(0, 2)
        self._shadow_effect.setColor(QColor(0, 0, 0, 150))
        self.setGraphicsEffect(self._shadow_effect)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the track
        track_color = QColor(180, 180, 180) if not self._checked else QColor(0, 150, 0)
        painter.setPen(Qt.NoPen)
        painter.setBrush(track_color)
        painter.drawRoundedRect(0, 5, 60, 20, 10, 10)

        # Draw the thumb
        thumb_position = 2 if not self._checked else 29
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(thumb_position, 2, 26, 26)

    def mousePressEvent(self, event):
        self._checked = not self._checked
        self._animation.setStartValue(0.8)
        self._animation.setEndValue(1.0)
        self._animation.start()
        self.update()
        self.toggled.emit(self._checked)

    def mouseReleaseEvent(self, event):
        self._animation.setStartValue(1.0)
        self._animation.setEndValue(0.8)
        self._animation.start()

    def isChecked(self):
        return self._checked

    def setChecked(self, checked):
        self._checked = checked
        self.update()

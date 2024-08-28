from PySide6.QtCore import Qt, QPropertyAnimation, Property, QEasingCurve, Signal
from PySide6.QtGui import QPainter, QColor, QIcon
from PySide6.QtWidgets import (
    QPushButton, QLineEdit, QComboBox, QLabel, QWidget, QVBoxLayout, QGraphicsOpacityEffect, QFrame, QStyle,
    QGraphicsDropShadowEffect
)

from desktop_app.src.ui.icon_path_enum import IconPath


class StyledButton(QPushButton):
    def __init__(self, text, parent=None, icon_path: IconPath = None):
        super().__init__(text, parent)

        if icon_path:  # hiding text, setting icon and tooltip
            icon_path_value: str = icon_path.value
            self.setIcon(QIcon(icon_path_value))
            self.setText("")
            self.setToolTip(text)  # Set tooltip to original text
        else:  # setting text if no icon
            self.setText(text)


class StyledLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)


class StyledComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)


class StyledLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignVCenter)


class CollapsibleBox(QWidget):
    def __init__(self, title="", parent=None):
        super().__init__(parent)

        self.toggle_button = StyledButton(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.toggled.connect(self.on_toggle)

        self.toggle_animation = QPropertyAnimation(self, b"maximumHeight")
        self.toggle_animation.setDuration(300)
        self.toggle_animation.setEasingCurve(QEasingCurve.InOutQuad)

        self.content_area = QWidget()
        self.content_area.setMaximumHeight(0)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.toggle_button)
        self.main_layout.addWidget(self.content_area)
        self.main_layout.addStretch()

    def on_toggle(self, checked):
        if checked:
            self.toggle_animation.setEndValue(self.content_area.sizeHint().height())
        else:
            self.toggle_animation.setEndValue(0)
        self.toggle_animation.start()

    def setContentLayout(self, layout):
        self.content_area.setLayout(layout)
        collapsed_height = self.sizeHint().height() - self.content_area.maximumHeight()
        self.toggle_animation.setStartValue(collapsed_height)
        self.toggle_animation.setEndValue(collapsed_height)


class ClickableLabel(QLabel):
    clicked = Signal()

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


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


class CardWidget(QFrame):
    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setLineWidth(1)

        layout = QVBoxLayout(self)
        title_label = StyledLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        layout.addWidget(content)


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

from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout
)

from src.ui.components.widgets.styled_elements import StyledButton


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

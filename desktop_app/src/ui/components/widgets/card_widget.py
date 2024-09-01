from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout, QFrame
)

from src.ui.components.widgets.styled_elements import StyledLabel


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

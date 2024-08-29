from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QPushButton, QLineEdit, QComboBox, QLabel
)

from desktop_app.src.ui.components.icon_path import IconPath


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

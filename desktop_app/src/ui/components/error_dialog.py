from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton


class ErrorDialog(QDialog):
    def __init__(self, error_message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Error")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout(self)

        self.error_label = QLabel(error_message)
        self.error_label.setWordWrap(True)  # Wrap long error messages
        layout.addWidget(self.error_label)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button, alignment=Qt.AlignCenter)

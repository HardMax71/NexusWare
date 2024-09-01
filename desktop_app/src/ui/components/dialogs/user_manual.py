import markdown
from PySide6.QtGui import QFont, Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextBrowser, QPushButton, QSizePolicy,
    QHBoxLayout
)


class UserManualDialog(QDialog):
    def __init__(self, content, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Manual")
        self.setMinimumSize(800, 600)
        self.init_ui(content)

    def init_ui(self, content):
        layout = QVBoxLayout(self)

        self.text_browser = QTextBrowser(self)
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setFont(QFont("Arial", 11))
        html_content = markdown.markdown(content)
        self.text_browser.setHtml(html_content)

        layout.addWidget(self.text_browser)

        bottom_layout = QHBoxLayout()

        hint_label = QLabel("Tip: You can disable automatic manual display after login in the General Settings.")
        hint_label.setWordWrap(False)
        hint_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        bottom_layout.addWidget(hint_label, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        bottom_layout.addStretch()

        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.accept)
        bottom_layout.addWidget(close_button, alignment=Qt.AlignRight | Qt.AlignVCenter)

        layout.addLayout(bottom_layout)

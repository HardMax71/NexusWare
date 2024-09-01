from PySide6.QtGui import QFont, Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy,
    QFrame
)


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About NexusWare WMS")
        self.setFixedSize(400, 350)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # Title
        title_label = QLabel("NexusWare WMS")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)

        # Version
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_font = QFont()
        version_font.setPointSize(10)
        version_label.setFont(version_font)
        main_layout.addWidget(version_label)

        main_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #d0d0d0;")
        main_layout.addWidget(separator)

        main_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Description
        description_label = QLabel(
            "A comprehensive Warehouse Management System\ndesigned for efficiency and reliability.")
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setWordWrap(True)
        description_font = QFont()
        description_font.setPointSize(11)
        description_label.setFont(description_font)
        main_layout.addWidget(description_label)

        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Copyright
        copyright_label = QLabel("© 2024 Max Azatian")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_font = QFont()
        copyright_font.setPointSize(9)
        copyright_label.setFont(copyright_font)
        main_layout.addWidget(copyright_label)

        # GitHub link
        github_button = QPushButton("GitHub")
        github_button.clicked.connect(lambda: self.open_url("https://github.com/HardMax71/NexusWare"))
        github_button.setFixedSize(110, 32)
        github_button_font = QFont()
        github_button_font.setPointSize(10)
        github_button.setFont(github_button_font)
        main_layout.addWidget(github_button, alignment=Qt.AlignCenter)

    def open_url(self, url):
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl
        QDesktopServices.openUrl(QUrl(url))

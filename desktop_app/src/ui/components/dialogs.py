import markdown
from PySide6.QtGui import QFont, Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QProgressBar, QDialogButtonBox, QFileDialog, QMessageBox, QTextBrowser, QPushButton, QSpacerItem, QSizePolicy,
    QFrame, QHBoxLayout
)


class ConfirmDialog(QDialog):
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(message))

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)


class InputDialog(QDialog):
    def __init__(self, title, label, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(label))

        self.input = QLineEdit()
        layout.addWidget(self.input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_input(self):
        return self.input.text()


class ProgressDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel()
        layout.addWidget(self.status_label)

    def set_progress(self, value):
        self.progress_bar.setValue(value)

    def set_status(self, status):
        self.status_label.setText(status)


class MessageBox(QMessageBox):
    def __init__(self, title, message, icon=QMessageBox.Information, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setText(message)
        self.setIcon(icon)


class FileDialog(QFileDialog):
    def __init__(self, title, file_type, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setNameFilter(file_type)
        self.setViewMode(QFileDialog.List)
        self.setFileMode(QFileDialog.ExistingFile)


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

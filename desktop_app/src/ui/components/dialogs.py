from PySide6.QtGui import QFont, Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QProgressBar, QDialogButtonBox, QFileDialog, QMessageBox, QTextBrowser, QPushButton, QHBoxLayout, QTextEdit
)
from .custom_widgets import StyledButton, StyledLabel
import markdown

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

        # Create text browser
        self.text_browser = QTextBrowser(self)
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setFont(QFont("Arial", 11))

        # Convert markdown to HTML
        html_content = markdown.markdown(content)
        self.text_browser.setHtml(html_content)

        layout.addWidget(self.text_browser)

        # Add close button
        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignRight)

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About NexusWare WMS")
        self.setFixedSize(400, 300)  # Adjust size as needed

        layout = QVBoxLayout(self)

        # Create a QTextEdit for displaying the about text
        about_text_edit = QTextEdit(self)
        about_text_edit.setReadOnly(True)  # Make it read-only
        about_text_edit.setText(
            "NexusWare WMS\n"
            "Version 1.0.0\n\n"
            "A comprehensive Warehouse Management System.\n"
            "© 2024 Max Azatian @ https://github.com/HardMax71/NexusWare. All rights reserved.\n\n"
            "For support, please contact me at Github"
        )

        # Add the QTextEdit to the layout
        layout.addWidget(about_text_edit)

        # Add a close button
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
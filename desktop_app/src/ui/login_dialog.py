from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit
from requests import HTTPError

from .components import StyledLineEdit, StyledButton, ErrorDialog


class LoginDialog(QDialog):
    def __init__(self, auth_service, parent=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Login to NexusWare WMS")
        self.setFixedSize(350, 200)

        layout = QVBoxLayout(self)

        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        self.username_input = StyledLineEdit()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)

        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        self.password_input = StyledLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        self.login_button = StyledButton("Login")
        self.login_button.clicked.connect(self.attempt_login)
        layout.addWidget(self.login_button, alignment=Qt.AlignCenter)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red;")
        layout.addWidget(self.error_label, alignment=Qt.AlignCenter)

    def attempt_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            response = self.auth_service.login(username, password)
            if response.get("access_token"):
                self.accept()
            else:
                self.show_error_dialog("Invalid username or password")
        except HTTPError as e:
            try:
                error_data = e.response.json()
                error_message = error_data.get('detail', 'Unknown error occurred.')
            except ValueError:
                error_message = e.response.text

            self.show_error_dialog(f"Login failed: {error_message}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.attempt_login()
        else:
            super().keyPressEvent(event)

    def show_error_dialog(self, message):
        error_dialog = ErrorDialog(message, self)
        error_dialog.exec_()

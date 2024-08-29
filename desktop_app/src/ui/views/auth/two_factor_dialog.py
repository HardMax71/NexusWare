from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QLabel)
from requests import HTTPError

from public_api.api import UsersAPI


class TwoFactorDialog(QDialog):
    def __init__(self, users_api: UsersAPI, username: str, password: str, parent=None):
        super().__init__(parent)
        self.users_api = users_api
        self.username = username
        self.password = password
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Two-Factor Authentication")
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        instructions = QLabel("Please enter the 6-digit code from your Google Authenticator app.")
        layout.addWidget(instructions)

        self.two_factor_input = QLineEdit()
        self.two_factor_input.setPlaceholderText("Enter 6-digit code")
        layout.addWidget(self.two_factor_input)

        verify_button = QPushButton("Verify")
        verify_button.clicked.connect(self.verify_2fa)
        layout.addWidget(verify_button)

    def verify_2fa(self):
        two_factor_code = self.two_factor_input.text()
        try:
            token = self.users_api.login_2fa(self.username, self.password, two_factor_code)
            if token:
                self.accept()
            else:
                self.show_error_dialog("Invalid 2FA code")
        except HTTPError as e:
            self.handle_error(e)

    def handle_error(self, e):
        try:
            error_data = e.response.json()
            error_message = error_data.get('detail', 'Unknown error occurred.')
        except ValueError:
            error_message = e.response.text
        self.show_error_dialog(f"Login failed: {error_message}")

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.verify_2fa()
        else:
            super().keyPressEvent(event)

    def show_error_dialog(self, message: str):
        QMessageBox.critical(self, "Login Error", message)

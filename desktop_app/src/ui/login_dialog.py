from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QPushButton, QFormLayout, QMessageBox, QLabel)
from requests import HTTPError

from desktop_app.src.services.authentication import AuthenticationService

class LoginDialog(QDialog):
    def __init__(self, auth_service: AuthenticationService, parent=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Login to NexusWare WMS")
        self.setMinimumWidth(300)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(30, 30, 30, 30)

        self.setup_login_form()

    def setup_login_form(self):
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        form_layout.addRow("Username:", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter password")
        form_layout.addRow("Password:", self.password_input)

        self.main_layout.addLayout(form_layout)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.attempt_login)
        self.login_button.setDefault(True)
        self.main_layout.addWidget(self.login_button)

    def attempt_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        try:
            token = self.auth_service.login(username, password)
            if token.access_token == "2FA_REQUIRED":
                self.show_2fa_dialog(username, password)
            else:
                self.accept()
        except HTTPError as e:
            self.handle_error(e)

    def show_2fa_dialog(self, username, password):
        two_factor_dialog = TwoFactorDialog(self.auth_service, username, password, self)
        if two_factor_dialog.exec() == QDialog.Accepted:
            self.accept()

    def handle_error(self, e):
        try:
            error_data = e.response.json()
            error_message = error_data.get('detail', 'Unknown error occurred.')
        except ValueError:
            error_message = e.response.text
        self.show_error_dialog(f"Login failed: {error_message}")

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.attempt_login()
        else:
            super().keyPressEvent(event)

    def show_error_dialog(self, message: str):
        QMessageBox.critical(self, "Login Error", message)


class TwoFactorDialog(QDialog):
    def __init__(self, auth_service: AuthenticationService, username: str, password: str, parent=None):
        super().__init__(parent)
        self.auth_service = auth_service
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
            token = self.auth_service.login_2fa(self.username, self.password, two_factor_code)
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
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QPushButton, QFormLayout, QMessageBox, QLabel,
                               QHBoxLayout, QInputDialog)
from requests import HTTPError

from desktop_app.src.services.authentication import AuthenticationService


class LoginDialog(QDialog):
    def __init__(self, auth_service: AuthenticationService, parent=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Login to NexusWare WMS")
        self.setMinimumWidth(450)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(30, 30, 30, 30)

        self.setup_login_form()

    def setup_login_form(self):
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter email")
        form_layout.addRow("Email:", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter password")

        # Create and add the show password action
        show_password_icon = QIcon("icons:eye_view.png")
        self.show_password_action = QAction(show_password_icon, "Show password", self)
        self.show_password_action.setCheckable(True)
        self.password_input.addAction(self.show_password_action, QLineEdit.TrailingPosition)
        self.show_password_action.toggled.connect(self.toggle_password_visibility)

        form_layout.addRow("Password:", self.password_input)

        self.main_layout.addLayout(form_layout)

        button_layout = QHBoxLayout()

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.attempt_login)
        self.login_button.setDefault(True)
        button_layout.addWidget(self.login_button)

        self.reset_password_button = QPushButton("Reset Password")
        self.reset_password_button.clicked.connect(self.reset_password)
        button_layout.addWidget(self.reset_password_button)

        self.main_layout.addLayout(button_layout)

    def toggle_password_visibility(self, show):
        self.password_input.setEchoMode(QLineEdit.Normal if show else QLineEdit.Password)
        icon = QIcon("icons:eye_hide.png" if show else "icons:eye_view.png")
        self.show_password_action.setIcon(icon)

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

    def reset_password(self):
        email, ok = QInputDialog.getText(self, "Reset Password", "Enter your email:")
        if ok and email:
            try:
                message = self.auth_service.reset_password(email)
                QMessageBox.information(self, "Password Reset", message.message)
            except HTTPError as e:
                self.handle_error(e)

    def handle_error(self, e):
        try:
            error_data = e.response.json()
            error_message = error_data.get('detail', 'Unknown error occurred.')
        except ValueError:
            error_message = e.response.text
        self.show_error_dialog(f"Error: {error_message}")

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.attempt_login()
        else:
            super().keyPressEvent(event)

    def show_error_dialog(self, message: str):
        QMessageBox.critical(self, "Error", message)


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

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QFormLayout, QMessageBox)
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

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

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

        main_layout.addLayout(form_layout)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.attempt_login)
        self.login_button.setDefault(True)
        main_layout.addWidget(self.login_button)

    def attempt_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        try:
            token = self.auth_service.login(username, password)
            if token:
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
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.attempt_login()
        else:
            super().keyPressEvent(event)

    def show_error_dialog(self, message: str):
        QMessageBox.critical(self, "Login Error", message)
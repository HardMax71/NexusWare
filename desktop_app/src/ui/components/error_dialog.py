import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QPushButton, QVBoxLayout, QTextEdit,
                               QLabel, QDialogButtonBox, QApplication)
from requests.exceptions import HTTPError


class DetailedErrorDialog(QDialog):
    def __init__(self, exctype, value, traceback, app_context):
        super().__init__()
        self.app_context = app_context
        self.setWindowTitle("Error")
        self.setMinimumSize(400, 300)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)

        layout = QVBoxLayout(self)

        error_label = QLabel("An error has occurred.")
        error_label.setStyleSheet("font-weight: bold; color: red;")
        layout.addWidget(error_label)

        detailed_text = f"Error Type: {exctype.__name__}\n"
        detailed_text += f"Error Message: {str(value)}\n\n"

        if isinstance(value, HTTPError):
            response = value.response
            detailed_text += f"Status Code: {response.status_code}\n"
            detailed_text += f"URL: {response.url}\n"
            detailed_text += "Response Headers:\n"
            for key, value in response.headers.items():
                detailed_text += f"  {key}: {value}\n"
            detailed_text += "\nResponse Content:\n"
            try:
                content = json.loads(response.content)
                detailed_text += json.dumps(content, indent=2)
            except json.JSONDecodeError:
                detailed_text += response.text

        text_edit = QTextEdit()
        text_edit.setPlainText(detailed_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        relogin_button = QPushButton("Re-login")
        relogin_button.clicked.connect(self.relogin)
        button_box.addButton(relogin_button, QDialogButtonBox.ActionRole)

    def relogin(self):
        self.accept()
        main_window = QApplication.activeWindow()
        if main_window:
            main_window.close()

        from desktop_app.src.ui import LoginDialog
        login_dialog = LoginDialog(self.app_context.auth_service)
        if login_dialog.exec() == LoginDialog.Accepted:
            self.app_context.create_and_show_main_window()
        else:
            QApplication.quit()


def global_exception_handler(app_context):
    def handler(exctype, value, traceback):
        error_dialog = DetailedErrorDialog(exctype, value, traceback, app_context)
        error_dialog.exec()

    return handler

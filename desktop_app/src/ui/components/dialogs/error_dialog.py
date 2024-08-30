import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QPushButton, QVBoxLayout, QTextEdit,
                               QLabel, QApplication, QFrame,
                               QHBoxLayout)
from requests.exceptions import HTTPError


class DetailedErrorDialog(QDialog):
    def __init__(self, exctype, value, traceback, app_context):
        super().__init__()
        self.app_context = app_context
        self.setWindowTitle("Error")
        self.setMinimumSize(450, 200)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Error icon and title
        header_layout = QHBoxLayout()
        error_icon = QLabel("⚠️")
        error_icon.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(error_icon)
        error_title = QLabel("An error has occurred")
        error_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(error_title)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)

        # Error description
        self.description_label = QLabel(f"{str(value)}")
        self.description_label.setWordWrap(True)
        main_layout.addWidget(self.description_label)

        # More details button
        self.more_details_button = QPushButton("Show Details")
        self.more_details_button.clicked.connect(self.toggle_details)
        main_layout.addWidget(self.more_details_button)

        # Detailed error information
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.hide()
        main_layout.addWidget(self.text_edit)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        relogin_button = QPushButton("Re-login")
        relogin_button.clicked.connect(self.relogin)
        button_layout.addWidget(relogin_button)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        button_layout.addWidget(ok_button)

        main_layout.addLayout(button_layout)

        self.prepare_detailed_text(exctype, value)

    def prepare_detailed_text(self, exctype, value):
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

        self.text_edit.setPlainText(detailed_text)

    def toggle_details(self):
        if self.text_edit.isVisible():
            self.text_edit.hide()
            self.more_details_button.setText("Show Details")
            self.setFixedSize(450, 200)
        else:
            self.text_edit.show()
            self.more_details_button.setText("Hide Details")
            self.setFixedSize(600, 400)

    def relogin(self):
        self.accept()
        main_window = QApplication.activeWindow()
        if main_window:
            main_window.close()

        from desktop_app.src.ui import LoginDialog
        login_dialog = LoginDialog(self.app_context.users_api)
        if login_dialog.exec() == LoginDialog.Accepted:
            self.app_context.create_and_show_main_window()
        else:
            QApplication.quit()


def global_exception_handler(app_context):
    def handler(exctype, value, traceback):
        error_dialog = DetailedErrorDialog(exctype, value, traceback, app_context)
        error_dialog.exec()

    return handler

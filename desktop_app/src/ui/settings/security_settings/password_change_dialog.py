from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLineEdit,
                               QDialog, QFormLayout, QPushButton)


class PasswordChangeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Change Password")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.current_password = QLineEdit(self)
        self.current_password.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Current Password:", self.current_password)

        self.new_password = QLineEdit(self)
        self.new_password.setEchoMode(QLineEdit.Password)
        form_layout.addRow("New Password:", self.new_password)

        self.confirm_password = QLineEdit(self)
        self.confirm_password.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Confirm New Password:", self.confirm_password)

        layout.addLayout(form_layout)

        button_box = QHBoxLayout()
        ok_button = QPushButton("OK", self)
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel", self)
        cancel_button.clicked.connect(self.reject)
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)

        layout.addLayout(button_box)

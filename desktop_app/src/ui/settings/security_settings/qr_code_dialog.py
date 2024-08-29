import json
from io import BytesIO

import pyotp
import qrcode
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSpinBox, QMessageBox, QLineEdit,
                               QDialog, QFormLayout, QPushButton, QLabel)
from requests import HTTPError

from desktop_app.src.ui.components import StyledLabel, StyledButton, ToggleSwitch
from public_api.api import UsersAPI
from public_api.shared_schemas import UserUpdate


class QRCodeDialog(QDialog):
    def __init__(self, qr_pixmap, secret_key, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Up Google Authenticator")
        self.setup_ui(qr_pixmap, secret_key)

    def setup_ui(self, qr_pixmap, secret_key):
        layout = QVBoxLayout(self)

        # QR Code
        qr_label = QLabel(self)
        qr_label.setPixmap(qr_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        qr_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(qr_label)

        # Instructions
        instructions = QLabel("1. Open Google Authenticator on your phone\n"
                              "2. Tap '+' and select 'Scan QR code'\n"
                              "3. Scan the QR code above\n"
                              "4. Enter the 6-digit code from Google Authenticator below")
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)

        # Secret key (in case QR code doesn't work)
        secret_label = QLabel(f"Secret key: {secret_key}")
        secret_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(secret_label)

        # Code input
        self.code_input = QLineEdit(self)
        self.code_input.setPlaceholderText("Enter 6-digit code")
        layout.addWidget(self.code_input)

        # Buttons
        button_box = QHBoxLayout()
        verify_button = QPushButton("Verify", self)
        verify_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel", self)
        cancel_button.clicked.connect(self.reject)
        button_box.addWidget(verify_button)
        button_box.addWidget(cancel_button)
        layout.addLayout(button_box)

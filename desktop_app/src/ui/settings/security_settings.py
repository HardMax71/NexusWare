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


class SecuritySettingsWidget(QWidget):
    def __init__(self, config_manager, api_client, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.api_client = api_client
        self.users_api = UsersAPI(api_client)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Two-factor authentication
        tfa_layout = QHBoxLayout()
        tfa_label = StyledLabel("Two-factor authentication:")
        self.tfa_toggle = ToggleSwitch()
        self.tfa_toggle.toggled.connect(self.on_tfa_toggled)
        tfa_layout.addWidget(tfa_label)
        tfa_layout.addWidget(self.tfa_toggle)
        layout.addLayout(tfa_layout)

        # Password change
        self.change_password_button = StyledButton("Change Password")
        self.change_password_button.clicked.connect(self.change_password)
        layout.addWidget(self.change_password_button)

        # Session timeout
        timeout_layout = QHBoxLayout()
        timeout_label = StyledLabel("Session timeout (minutes):")
        self.timeout_input = QSpinBox()
        self.timeout_input.setRange(5, 120)
        self.timeout_input.setValue(self.config_manager.get("session_timeout", 30))
        self.timeout_input.valueChanged.connect(self.on_timeout_changed)
        timeout_layout.addWidget(timeout_label)
        timeout_layout.addWidget(self.timeout_input)
        layout.addLayout(timeout_layout)

        # Data encryption
        encryption_layout = QHBoxLayout()
        encryption_label = StyledLabel("Data encryption:")
        self.encryption_toggle = ToggleSwitch()
        self.encryption_toggle.setChecked(self.config_manager.get("data_encryption", True))
        self.encryption_toggle.toggled.connect(self.on_encryption_toggled)
        encryption_layout.addWidget(encryption_label)
        encryption_layout.addWidget(self.encryption_toggle)
        layout.addLayout(encryption_layout)

        # Password strength requirements
        strength_layout = QHBoxLayout()
        strength_label = StyledLabel("Minimum password strength:")
        self.strength_input = QSpinBox()
        self.strength_input.setRange(1, 5)
        self.strength_input.setValue(self.config_manager.get("min_password_strength", 3))
        self.strength_input.valueChanged.connect(self.on_strength_changed)
        strength_layout.addWidget(strength_label)
        strength_layout.addWidget(self.strength_input)
        layout.addLayout(strength_layout)

        layout.addStretch()

        self.load_current_user()

    def load_current_user(self):
        try:
            self.current_user = self.users_api.get_current_user()
            self.tfa_toggle.setChecked(self.current_user.two_factor_auth_enabled)
        except HTTPError as e:
            QMessageBox.critical(self, "Error", f"Failed to load user data: {str(e)}")

    def on_tfa_toggled(self, state):
        if state:
            try:
                current_user = self.users_api.get_current_user()

                # Generate a secret key for Google Authenticator
                secret_key = pyotp.random_base32()

                # Create a TOTP instance
                totp = pyotp.TOTP(secret_key)

                # Generate the provisioning URI for Google Authenticator
                uri = totp.provisioning_uri(name=current_user.email, issuer_name="NexusWareWMS")

                # Create QR code
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(uri)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")

                # Convert PIL Image to QPixmap
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                qr_pixmap = QPixmap()
                qr_pixmap.loadFromData(buffer.getvalue())

                # Show QR code dialog
                dialog = QRCodeDialog(qr_pixmap, secret_key, self)
                if dialog.exec() == QDialog.Accepted:
                    # Verify the entered code
                    entered_code = dialog.code_input.text()
                    if totp.verify(entered_code):
                        # Update user in the database
                        user_update = UserUpdate(
                            two_factor_auth_enabled=True,
                            two_factor_auth_secret=secret_key
                        )
                        updated_user = self.users_api.update_current_user(user_update)
                        self.current_user = updated_user
                        QMessageBox.information(self, "Two-Factor Authentication",
                                                "Two-factor authentication has been successfully enabled.")
                    else:
                        QMessageBox.warning(self, "Verification Failed",
                                            "The entered code is incorrect. "
                                            "Two-factor authentication has not been enabled.")
                        self.tfa_toggle.setChecked(False)
                else:
                    self.tfa_toggle.setChecked(False)
            except Exception as e:
                QMessageBox.critical(self, "Error",
                                     f"An error occurred while setting up two-factor authentication: {str(e)}")
                self.tfa_toggle.setChecked(False)
        else:
            confirm = QMessageBox.question(self, "Disable Two-Factor Authentication",
                                           "Are you sure you want to disable two-factor authentication? "
                                           "This will reduce the security of your account.",
                                           QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                try:
                    user_update = UserUpdate(
                        two_factor_auth_enabled=False,
                        two_factor_auth_secret=None
                    )
                    updated_user = self.users_api.update_current_user(user_update)
                    self.current_user = updated_user
                    QMessageBox.information(self, "Two-Factor Authentication",
                                            "Two-factor authentication has been disabled.")
                except HTTPError as e:
                    QMessageBox.critical(self, "Error",
                                         f"Failed to disable two-factor authentication: {str(e)}")
                    self.tfa_toggle.setChecked(True)
            else:
                self.tfa_toggle.setChecked(True)

    def change_password(self):
        dialog = PasswordChangeDialog(self)
        if dialog.exec() == QDialog.Accepted:
            current_password = dialog.current_password.text()
            new_password = dialog.new_password.text()
            confirm_password = dialog.confirm_password.text()

            if new_password == confirm_password:
                try:
                    response = self.users_api.change_password(current_password, new_password)
                    QMessageBox.information(self, "Password Changed", response.message)
                except HTTPError as e:
                    try:
                        details = json.loads(e.response.text)
                        error_detail = details.get('detail', 'Unknown error occurred')
                    except json.JSONDecodeError:
                        error_detail = 'Unable to parse error details'

                    QMessageBox.warning(self, "Error", f"Failed to change password: {error_detail}")
            else:
                QMessageBox.warning(self, "Error", "New passwords do not match.")

    def on_timeout_changed(self, timeout):
        self.config_manager.set("session_timeout", timeout)

    def on_encryption_toggled(self, state):
        self.config_manager.set("data_encryption", state)
        if state:
            QMessageBox.information(self, "Data Encryption",
                                    "Data encryption has been enabled. All sensitive data will now be encrypted.")
        else:
            QMessageBox.warning(self, "Data Encryption",
                                "Data encryption has been disabled. This may pose security risks.")

    def on_strength_changed(self, strength):
        self.config_manager.set("min_password_strength", strength)
        strength_descriptions = [
            "Very Weak", "Weak", "Moderate", "Strong", "Very Strong"
        ]
        QMessageBox.information(self, "Password Strength",
                                f"Minimum password strength set to: {strength_descriptions[strength - 1]}")


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

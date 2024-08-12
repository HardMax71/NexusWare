from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpinBox

from ..components import StyledLabel, StyledButton, ToggleSwitch


class SecuritySettingsWidget(QWidget):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Two-factor authentication
        # TODO - Implement two-factor authentication and other commented out stuff
        tfa_layout = QHBoxLayout()
        tfa_label = StyledLabel("Two-factor authentication:")
        self.tfa_toggle = ToggleSwitch()
        # self.tfa_toggle.setChecked(self.config_manager.get("two_factor_auth", False))
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
        # self.timeout_input.setValue(self.config_manager.get("session_timeout", 30))
        self.timeout_input.valueChanged.connect(self.on_timeout_changed)
        timeout_layout.addWidget(timeout_label)
        timeout_layout.addWidget(self.timeout_input)
        layout.addLayout(timeout_layout)

        # Data encryption
        encryption_layout = QHBoxLayout()
        encryption_label = StyledLabel("Data encryption:")
        self.encryption_toggle = ToggleSwitch()
        # self.encryption_toggle.setChecked(self.config_manager.get("data_encryption", True))
        self.encryption_toggle.toggled.connect(self.on_encryption_toggled)
        encryption_layout.addWidget(encryption_label)
        encryption_layout.addWidget(self.encryption_toggle)
        layout.addLayout(encryption_layout)

        layout.addStretch()

    def on_tfa_toggled(self, state):
        self.config_manager.set("two_factor_auth", state)

    def change_password(self):
        # TODO - Implement password change logic here
        pass

    def on_timeout_changed(self, timeout):
        self.config_manager.set("session_timeout", timeout)

    def on_encryption_toggled(self, state):
        self.config_manager.set("data_encryption", state)

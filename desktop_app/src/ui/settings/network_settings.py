import requests
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpinBox, QMessageBox, QFrame, QToolButton, QStyle

from desktop_app.src.ui.components import StyledLabel, StyledLineEdit, StyledButton


class NetworkSettingsWidget(QWidget):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # API Base URL (read-only)
        base_url_layout = QHBoxLayout()
        base_url_label = StyledLabel("API Base URL:")
        self.base_url_input = StyledLineEdit()
        self.base_url_input.setText(self.config_manager.get("api_base_url", "http://127.0.0.1:8000/api/v1"))
        self.base_url_input.setReadOnly(True)
        base_url_layout.addWidget(base_url_label)
        base_url_layout.addWidget(self.base_url_input)
        layout.addLayout(base_url_layout)

        # Test URL
        test_url_layout = QHBoxLayout()
        test_url_label = StyledLabel("Test URL:")
        self.test_url_input = StyledLineEdit()
        self.test_url_input.setText(self.config_manager.get("api_test_url", "http://127.0.0.1:8000/"))
        self.test_url_input.textChanged.connect(self.on_test_url_changed)
        test_url_layout.addWidget(test_url_label)
        test_url_layout.addWidget(self.test_url_input)
        layout.addLayout(test_url_layout)

        # Timeout
        timeout_layout = QHBoxLayout()
        timeout_label = StyledLabel("Request Timeout (seconds):")
        self.timeout_input = QSpinBox()
        self.timeout_input.setRange(1, 60)
        self.timeout_input.setValue(self.config_manager.get("request_timeout", 10))
        self.timeout_input.valueChanged.connect(self.on_timeout_changed)
        timeout_layout.addWidget(timeout_label)
        timeout_layout.addWidget(self.timeout_input)
        layout.addLayout(timeout_layout)

        # Test Connection
        self.test_button = StyledButton("Test Connection")
        self.test_button.clicked.connect(self.test_connection)
        layout.addWidget(self.test_button)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # ShipEngine API Key
        api_layout = QVBoxLayout()
        api_label = StyledLabel("ShipEngine API Key:")
        api_label.setFont(QFont(api_label.font().family(), api_label.font().pointSize(), QFont.Bold))

        api_input_layout = QHBoxLayout()
        self.api_input = StyledLineEdit()
        self.api_input.setText(self.config_manager.get("shipengine_api_key", "TEST_API"))
        self.api_input.setEchoMode(StyledLineEdit.Password)
        self.api_input.textChanged.connect(self.on_api_key_changed)

        self.toggle_visibility_button = QToolButton()
        self.toggle_visibility_button.setIcon(self.style().standardIcon(getattr(QStyle, "SP_DialogApplyButton")))
        self.toggle_visibility_button.clicked.connect(self.toggle_api_key_visibility)

        api_input_layout.addWidget(self.api_input)
        api_input_layout.addWidget(self.toggle_visibility_button)

        api_layout.addWidget(api_label)
        api_layout.addLayout(api_input_layout)
        layout.addLayout(api_layout)

        layout.addStretch()

    def on_test_url_changed(self, url):
        self.config_manager.set("api_test_url", url)

    def on_api_key_changed(self, api_key):
        self.config_manager.set("shipengine_api_key", api_key)

    def on_timeout_changed(self, timeout):
        self.config_manager.set("request_timeout", timeout)

    def toggle_api_key_visibility(self):
        if self.api_input.echoMode() == StyledLineEdit.Password:
            self.api_input.setEchoMode(StyledLineEdit.Normal)
            icon = self.style().standardIcon(getattr(QStyle, "SP_DialogCancelButton"))
        else:
            self.api_input.setEchoMode(StyledLineEdit.Password)
            icon = self.style().standardIcon(getattr(QStyle, "SP_DialogApplyButton"))

        self.toggle_visibility_button.setIcon(icon)

    def test_connection(self):
        url = self.test_url_input.text()
        timeout = self.timeout_input.value()

        try:
            response = requests.get(url, timeout=timeout)

            if response.status_code == 200:
                data = response.json()
                if data.get('message') == "Welcome to NexusWare WMS API":
                    QMessageBox.information(self, "Connection Test", "Connection successful!", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "Connection Test", "Connected, but unexpected response.", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Connection Test", f"Connection failed. Status code: {response.status_code}",
                                    QMessageBox.Ok)

        except requests.exceptions.Timeout:
            QMessageBox.critical(self, "Connection Test",
                                 "Connection timed out. Please check your network or increase the timeout.",
                                 QMessageBox.Ok)
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Connection Test",
                                 "Connection error. Please check the server URL and your network connection.",
                                 QMessageBox.Ok)
        except Exception as e:
            QMessageBox.critical(self, "Connection Test", f"An error occurred: {str(e)}", QMessageBox.Ok)

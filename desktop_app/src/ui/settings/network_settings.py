import requests
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpinBox, QMessageBox

from ..components import StyledLabel, StyledLineEdit, StyledButton


class NetworkSettingsWidget(QWidget):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Server URL
        url_layout = QHBoxLayout()
        url_label = StyledLabel("Server URL:")
        self.url_input = StyledLineEdit()
        # self.url_input.setText(self.config_manager.get("server_url", ""))
        self.url_input.textChanged.connect(self.on_url_changed)
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # API Key
        api_layout = QHBoxLayout()
        api_label = StyledLabel("API Key:")
        self.api_input = StyledLineEdit()
        # self.api_input.setText(self.config_manager.get("api_key", ""))
        self.api_input.textChanged.connect(self.on_api_key_changed)
        api_layout.addWidget(api_label)
        api_layout.addWidget(self.api_input)
        layout.addLayout(api_layout)

        # Timeout
        timeout_layout = QHBoxLayout()
        timeout_label = StyledLabel("Request Timeout (seconds):")
        self.timeout_input = QSpinBox()
        self.timeout_input.setRange(1, 60)
        # self.timeout_input.setValue(self.config_manager.get("request_timeout", 30))
        self.timeout_input.valueChanged.connect(self.on_timeout_changed)
        timeout_layout.addWidget(timeout_label)
        timeout_layout.addWidget(self.timeout_input)
        layout.addLayout(timeout_layout)

        # Test Connection
        self.test_button = StyledButton("Test Connection")
        self.test_button.clicked.connect(self.test_connection)
        layout.addWidget(self.test_button)

        layout.addStretch()

    def on_url_changed(self, url):
        self.config_manager.set("server_url", url)

    def on_api_key_changed(self, api_key):
        self.config_manager.set("api_key", api_key)

    def on_timeout_changed(self, timeout):
        self.config_manager.set("request_timeout", timeout)

    def test_connection(self):
        url = self.url_input.text().rstrip('/') + '/'  # Ensure the URL ends with a single '/'
        api_key = self.api_input.text()
        timeout = self.timeout_input.value()

        try:
            headers = {'Authorization': f'Bearer {api_key}'} if api_key else {}
            response = requests.get(url, headers=headers, timeout=timeout)

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

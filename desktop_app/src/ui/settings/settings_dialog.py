from PySide6.QtWidgets import QDialog, QTabWidget, QVBoxLayout, QDialogButtonBox

from .advanced_settings import AdvancedSettingsWidget
from .appearance_settings import AppearanceSettingsWidget
from .general_settings import GeneralSettingsWidget
from .network_settings import NetworkSettingsWidget
from .security_settings import SecuritySettingsWidget
from .system_diagnostics import SystemDiagnosticsWidget


class SettingsDialog(QDialog):
    def __init__(self, config_manager, parent=None, api_client=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.api_client = api_client
        self.setWindowTitle("Settings")
        self.setMinimumSize(500, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.tab_widget = QTabWidget()

        self.general_settings = GeneralSettingsWidget(self.config_manager)
        self.appearance_settings = AppearanceSettingsWidget(self.config_manager)
        self.network_settings = NetworkSettingsWidget(self.config_manager)
        self.security_settings = SecuritySettingsWidget(self.config_manager, self.api_client)
        self.advanced_settings = AdvancedSettingsWidget(self.config_manager)
        self.system_diagnostics = SystemDiagnosticsWidget(self.config_manager, self.api_client)

        self.tab_widget.addTab(self.general_settings, "General")
        self.tab_widget.addTab(self.appearance_settings, "Appearance")
        self.tab_widget.addTab(self.network_settings, "Network")
        self.tab_widget.addTab(self.security_settings, "Security")
        self.tab_widget.addTab(self.advanced_settings, "Advanced")
        self.tab_widget.addTab(self.system_diagnostics, "System Diagnostics")

        layout.addWidget(self.tab_widget)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ok_button = button_box.button(QDialogButtonBox.Ok)
        cancel_button = button_box.button(QDialogButtonBox.Cancel)

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        layout.addWidget(button_box)

    def accept(self):
        self.config_manager.apply_changes()
        super().accept()

    def reject(self):
        self.config_manager.discard_changes()
        super().reject()
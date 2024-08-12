from PySide6.QtWidgets import QDialog, QTabWidget, QVBoxLayout, QDialogButtonBox
from PySide6.QtCore import Qt

from .general_settings import GeneralSettingsWidget
from .appearance_settings import AppearanceSettingsWidget
from .network_settings import NetworkSettingsWidget
from .security_settings import SecuritySettingsWidget
from .advanced_settings import AdvancedSettingsWidget
from ..components import StyledButton


class SettingsDialog(QDialog):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("Settings")
        self.setMinimumSize(500, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Create tab widget
        self.tab_widget = QTabWidget()

        # Create settings widgets
        self.general_settings = GeneralSettingsWidget(self.config_manager)
        self.appearance_settings = AppearanceSettingsWidget(self.config_manager)
        self.network_settings = NetworkSettingsWidget(self.config_manager)
        self.security_settings = SecuritySettingsWidget(self.config_manager)
        self.advanced_settings = AdvancedSettingsWidget(self.config_manager)

        # Add tabs
        self.tab_widget.addTab(self.general_settings, "General")
        self.tab_widget.addTab(self.appearance_settings, "Appearance")
        self.tab_widget.addTab(self.network_settings, "Network")
        self.tab_widget.addTab(self.security_settings, "Security")
        self.tab_widget.addTab(self.advanced_settings, "Advanced")

        layout.addWidget(self.tab_widget)

        # Add OK and Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ok_button = button_box.button(QDialogButtonBox.Ok)
        cancel_button = button_box.button(QDialogButtonBox.Cancel)

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        # Style the buttons
        ok_button.setProperty("class", "primary")
        cancel_button.setProperty("class", "secondary")

        layout.addWidget(button_box)

    def accept(self):
        # Save all settings before closing
        self.save_settings()
        super().accept()

    def save_settings(self):
        # Each settings widget is responsible for saving its own settings
        # via the config_manager, so we don't need to do anything here.
        # However, you could add any additional saving logic if needed.
        pass

    def reject(self):
        # Optionally, you could add logic here to warn the user if they have unsaved changes
        super().reject()


from PySide6.QtCore import QCoreApplication, QSettings
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QMessageBox

from desktop_app.src.ui.components import StyledLabel, StyledComboBox, ToggleSwitch


class GeneralSettingsWidget(QWidget):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Language selection
        lang_layout = QHBoxLayout()
        lang_label = StyledLabel("Language:")
        self.lang_combo = StyledComboBox()
        self.lang_combo.addItems(["English", "Spanish", "French", "German"])
        self.lang_combo.setCurrentText(self.config_manager.get("language", "English"))
        self.lang_combo.currentTextChanged.connect(self.on_language_changed)
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        layout.addLayout(lang_layout)

        # Automatic updates
        update_layout = QHBoxLayout()
        update_label = StyledLabel("Automatic updates:")
        self.update_toggle = ToggleSwitch()
        self.update_toggle.setChecked(self.config_manager.get("auto_update", True))
        self.update_toggle.toggled.connect(self.on_auto_update_toggled)
        update_layout.addWidget(update_label)
        update_layout.addWidget(self.update_toggle)
        layout.addLayout(update_layout)

        # Startup behavior
        startup_layout = QHBoxLayout()
        startup_label = StyledLabel("Start on system startup:")
        self.startup_toggle = ToggleSwitch()
        self.startup_toggle.setChecked(self.config_manager.get("start_on_startup", False))
        self.startup_toggle.toggled.connect(self.on_startup_toggled)
        startup_layout.addWidget(startup_label)
        startup_layout.addWidget(self.startup_toggle)
        layout.addLayout(startup_layout)

        layout.addStretch()

    def on_language_changed(self, language):
        self.config_manager.set("language", language)
        QMessageBox.information(self, "Language Changed",
                                "Please restart the application for the language change to take effect.")

    def on_auto_update_toggled(self, state):
        self.config_manager.set("auto_update", state)

    def on_startup_toggled(self, state):
        self.config_manager.set("start_on_startup", state)
        self.set_startup_behavior(state)

    def set_startup_behavior(self, enable):
        # TODO: Add same behavior for Linux and macOS
        settings = QSettings("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                             QSettings.NativeFormat)
        if enable:
            settings.setValue("NexusWareWMS", QCoreApplication.applicationFilePath().replace('/', '\\'))
        else:
            settings.remove("NexusWareWMS")

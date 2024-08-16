from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpinBox

from desktop_app.src.ui.components import StyledLabel, StyledButton, StyledComboBox


class AdvancedSettingsWidget(QWidget):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Logging level
        log_layout = QHBoxLayout()
        log_label = StyledLabel("Logging level:")
        self.log_combo = StyledComboBox()
        self.log_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_combo.setCurrentText(self.config_manager.get("log_level", "INFO"))
        self.log_combo.currentTextChanged.connect(self.on_log_level_changed)
        log_layout.addWidget(log_label)
        log_layout.addWidget(self.log_combo)
        layout.addLayout(log_layout)

        # Cache size
        cache_layout = QHBoxLayout()
        cache_label = StyledLabel("Cache size (MB):")
        self.cache_input = QSpinBox()
        self.cache_input.setRange(50, 1000)
        self.cache_input.setValue(self.config_manager.get("cache_size", 200))
        self.cache_input.valueChanged.connect(self.on_cache_size_changed)
        cache_layout.addWidget(cache_label)
        cache_layout.addWidget(self.cache_input)
        layout.addLayout(cache_layout)

        # Reset settings
        self.reset_button = StyledButton("Reset All Settings")
        self.reset_button.clicked.connect(self.reset_settings)
        layout.addWidget(self.reset_button)

        layout.addStretch()

    def on_log_level_changed(self, level):
        self.config_manager.set("log_level", level)

    def on_cache_size_changed(self, size):
        self.config_manager.set("cache_size", size)

    def reset_settings(self):
        self.config_manager.set("log_level", "INFO")
        self.config_manager.set("cache_size", 200)
        self.refresh_settings()

    def refresh_settings(self):
        self.log_combo.setCurrentText(self.config_manager.get("log_level", "INFO"))
        self.cache_input.setValue(self.config_manager.get("cache_size", 200))

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_settings()

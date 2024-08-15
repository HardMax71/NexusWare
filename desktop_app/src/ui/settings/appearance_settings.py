from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFontComboBox

from ..components import StyledLabel, StyledComboBox


class AppearanceSettingsWidget(QWidget):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # TODO: Implement theme selection, font selection, and font size selection
        # Theme selection
        theme_layout = QHBoxLayout()
        theme_label = StyledLabel("Theme:")
        self.theme_combo = StyledComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        # self.theme_combo.setCurrentText(self.config_manager.get("theme", "System"))
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)

        # Font selection
        font_layout = QHBoxLayout()
        font_label = StyledLabel("Font:")
        self.font_combo = QFontComboBox()
        # self.font_combo.setCurrentFont(QFont(self.config_manager.get("font", "Arial")))
        self.font_combo.currentFontChanged.connect(self.on_font_changed)
        font_layout.addWidget(font_label)
        font_layout.addWidget(self.font_combo)
        layout.addLayout(font_layout)

        # Font size
        size_layout = QHBoxLayout()
        size_label = StyledLabel("Font size:")
        self.size_combo = StyledComboBox()
        self.size_combo.addItems(["Small", "Medium", "Large"])
        # self.size_combo.setCurrentText(self.config_manager.get("font_size", "Medium"))
        self.size_combo.currentTextChanged.connect(self.on_font_size_changed)
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_combo)
        layout.addLayout(size_layout)

        layout.addStretch()

    def on_theme_changed(self, theme):
        self.config_manager.set("theme", theme)

    def on_font_changed(self, font):
        self.config_manager.set("font", font.family())

    def on_font_size_changed(self, size):
        self.config_manager.set("font_size", size)

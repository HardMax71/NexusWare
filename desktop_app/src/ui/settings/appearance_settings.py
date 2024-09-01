import os

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFontComboBox, QMessageBox, QApplication

from src.ui.components import StyledLabel, StyledComboBox


class AppearanceSettingsWidget(QWidget):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Theme selection
        theme_layout = QHBoxLayout()
        theme_label = StyledLabel("Theme:")
        self.theme_combo = StyledComboBox()
        self.load_available_themes()
        current_theme = self.config_manager.get("theme", "light")
        self.theme_combo.setCurrentText(current_theme.capitalize())
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)

        # Font selection
        font_layout = QHBoxLayout()
        font_label = StyledLabel("Font:")
        self.font_combo = QFontComboBox()
        current_font = self.config_manager.get("font", "Arial")
        self.font_combo.setCurrentFont(QFont(current_font))
        self.font_combo.currentFontChanged.connect(self.on_font_changed)
        font_layout.addWidget(font_label)
        font_layout.addWidget(self.font_combo)
        layout.addLayout(font_layout)

        # Font size
        size_layout = QHBoxLayout()
        size_label = StyledLabel("Font size:")
        self.size_combo = StyledComboBox()
        self.size_combo.addItems(["Small", "Medium", "Large"])
        current_size = self.config_manager.get("font_size", "Medium")
        self.size_combo.setCurrentText(current_size)
        self.size_combo.currentTextChanged.connect(self.on_font_size_changed)
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_combo)
        layout.addLayout(size_layout)

        layout.addStretch()

    def load_available_themes(self):
        styles_dir = "./resources/styles"
        theme_files = [f for f in os.listdir(styles_dir) if f.endswith("_theme.qss")]
        themes = [f.split("_")[0].capitalize() for f in theme_files]
        self.theme_combo.addItems(themes)

    def on_theme_changed(self, theme):
        theme_lower = theme.lower()
        self.config_manager.set("theme", theme_lower)
        self.apply_theme(theme_lower)

    def on_font_changed(self, font):
        self.config_manager.set("font", font.family())
        self.apply_font(font.family())

    def on_font_size_changed(self, size):
        self.config_manager.set("font_size", size)
        self.apply_font_size(size)

    def apply_theme(self, theme):
        stylesheet_path = f"./resources/styles/{theme}_theme.qss"
        try:
            with open(stylesheet_path, "r") as f:
                stylesheet = f.read()
                QApplication.instance().setStyleSheet(stylesheet)
        except FileNotFoundError:
            QMessageBox.warning(self, "Theme Error", f"Theme file not found: {stylesheet_path}")

    def apply_font(self, font_family):
        app = QApplication.instance()
        font = app.font()
        font.setFamily(font_family)
        app.setFont(font)

    def apply_font_size(self, size):
        app = QApplication.instance()
        font = app.font()
        if size == "Small":
            font.setPointSize(8)
        elif size == "Medium":
            font.setPointSize(10)
        elif size == "Large":
            font.setPointSize(12)
        app.setFont(font)

    def showEvent(self, event):
        super().showEvent(event)
        # Apply current settings when the widget is shown
        theme = self.config_manager.get("theme", "light")
        font = self.config_manager.get("font", "Arial")
        font_size = self.config_manager.get("font_size", "Medium")
        self.apply_theme(theme)
        self.apply_font(font)
        self.apply_font_size(font_size)

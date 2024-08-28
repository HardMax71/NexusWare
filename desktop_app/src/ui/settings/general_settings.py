import os
import sys

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

        # Show manual toggle
        manual_layout = QHBoxLayout()
        manual_label = StyledLabel("Show manual after login:")
        self.manual_toggle = ToggleSwitch()
        self.manual_toggle.setChecked(self.config_manager.get("show_manual_after_login", True))
        self.manual_toggle.toggled.connect(self.on_show_manual_toggled)
        manual_layout.addWidget(manual_label)
        manual_layout.addWidget(self.manual_toggle)
        layout.addLayout(manual_layout)

        # Show tutorial mode toggle
        tutorial_layout = QHBoxLayout()
        tutorial_label = StyledLabel("Show tutorial mode:")
        self.tutorial_toggle = ToggleSwitch()
        self.tutorial_toggle.setChecked(self.config_manager.get("start_tutorial", True))
        self.tutorial_toggle.toggled.connect(self.on_show_tutorial_toggled)
        tutorial_layout.addWidget(tutorial_label)
        tutorial_layout.addWidget(self.tutorial_toggle)
        layout.addLayout(tutorial_layout)

        layout.addStretch()

    def on_show_tutorial_toggled(self, state):
        self.config_manager.set("start_tutorial", state)

    def on_show_manual_toggled(self, state):
        self.config_manager.set("show_manual_after_login", state)

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
        if sys.platform == "win32":
            self.set_windows_startup(enable)
        elif sys.platform == "darwin":
            self.set_macos_startup(enable)
        elif sys.platform.startswith("linux"):
            self.set_linux_startup(enable)
        else:
            QMessageBox.warning(self, "Unsupported Platform",
                                "Setting startup behavior is not supported on this platform.")

    def set_windows_startup(self, enable):
        settings = QSettings("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                             QSettings.NativeFormat)
        app_path = QCoreApplication.applicationFilePath().replace('/', '\\')
        if enable:
            settings.setValue("NexusWareWMS", app_path)
        else:
            settings.remove("NexusWareWMS")

    def set_macos_startup(self, enable):
        app_name = QCoreApplication.applicationName()
        plist_path = os.path.expanduser(f"~/Library/LaunchAgents/com.{app_name}.plist")
        app_path = QCoreApplication.applicationFilePath()

        if enable:
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
            <plist version="1.0">
            <dict>
                <key>Label</key>
                <string>com.{app_name}</string>
                <key>ProgramArguments</key>
                <array>
                    <string>{app_path}</string>
                </array>
                <key>RunAtLoad</key>
                <true/>
            </dict>
            </plist>"""
            with open(plist_path, "w") as f:
                f.write(plist_content)
        else:
            if os.path.exists(plist_path):
                os.remove(plist_path)

    def set_linux_startup(self, enable):
        app_name = QCoreApplication.applicationName()
        desktop_file_path = os.path.expanduser(f"~/.config/autostart/{app_name}.desktop")
        app_path = QCoreApplication.applicationFilePath()

        if enable:
            desktop_file_content = f"""[Desktop Entry]
            Type=Application
            Exec={app_path}
            Hidden=false
            NoDisplay=false
            X-GNOME-Autostart-enabled=true
            Name[en_US]={app_name}
            Name={app_name}
            Comment[en_US]=Start {app_name} on system startup
            Comment=Start {app_name} on system startup
            """
            os.makedirs(os.path.dirname(desktop_file_path), exist_ok=True)
            with open(desktop_file_path, "w") as f:
                f.write(desktop_file_content)
        else:
            if os.path.exists(desktop_file_path):
                os.remove(desktop_file_path)

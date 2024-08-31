import subprocess
import sys
import tempfile

import requests
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox, QProgressDialog
from packaging import version

from src.utils import ConfigManager


class UpdateManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.current_version = self.config_manager.get("app_version")
        self.update_url = self.config_manager.get("update_check_url")
        self.update_download_url = self.config_manager.get("update_download_url")

    def check_for_updates(self):
        try:
            response = requests.get(self.update_url)
            response.raise_for_status()
            latest_version = response.json()["latest_version"]

            if version.parse(latest_version) > version.parse(self.current_version):
                return latest_version
            return None
        except requests.RequestException:
            return None

    def download_update(self, version):
        try:
            url = f"{self.update_download_url}/{version}/NexusWareWMS-{version}.exe"
            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 KB

            progress_dialog = QProgressDialog("Downloading update...", "Cancel", 0, total_size)
            progress_dialog.setWindowModality(Qt.WindowModal)

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.exe')

            try:
                for data in response.iter_content(block_size):
                    size = temp_file.write(data)
                    progress_dialog.setValue(progress_dialog.value() + size)

                    if progress_dialog.wasCanceled():
                        raise Exception("Download canceled by user")

            finally:
                temp_file.close()

            progress_dialog.close()
            return temp_file.name

        except requests.RequestException as e:
            QMessageBox.critical(None, "Update Error", f"Failed to download update: {str(e)}")
            return None
        except Exception as e:
            QMessageBox.critical(None, "Update Error", str(e))
            return None

    def install_update(self, update_file):
        try:
            if sys.platform == 'win32':
                subprocess.Popen([update_file, '/SILENT'])
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', update_file])
            else:
                subprocess.Popen(['xdg-open', update_file])

            sys.exit(0)
        except Exception as e:
            QMessageBox.critical(None, "Update Error", f"Failed to install update: {str(e)}")

    def perform_update(self):
        latest_version = self.check_for_updates()
        if latest_version:
            reply = QMessageBox.question(None, "Update Available",
                                         f"A new version ({latest_version}) is available. Do you want to update?",
                                         QMessageBox.Yes | QMessageBox.No)

            if reply == QMessageBox.Yes:
                update_file = self.download_update(latest_version)
                if update_file:
                    self.install_update(update_file)
        else:
            QMessageBox.information(None, "No Updates", "You are using the latest version.")

    def set_auto_update(self, enabled):
        self.config_manager.set("auto_update", enabled)

    def is_auto_update_enabled(self):
        return self.config_manager.get("auto_update", True)

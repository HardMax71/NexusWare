import requests
from packaging import version

from desktop_app.src.utils import ConfigManager


class UpdateManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.current_version = self.config_manager.get("app_version")
        self.update_url = self.config_manager.get("update_check_url")

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
        # TODO: Implement update download logic here
        pass

    def install_update(self, version):
        # TODO: Implement update installation logic here
        pass
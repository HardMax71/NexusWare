import json
import os

class ConfigManager:
    def __init__(self, config_file='./resources/config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        self.temp_config = {}

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get(self, key, default=None):
        return self.temp_config.get(key, self.config.get(key, default))

    def set(self, key, value):
        self.temp_config[key] = value

    def apply_changes(self):
        self.config.update(self.temp_config)
        self.save_config()
        self.temp_config.clear()

    def discard_changes(self):
        self.temp_config.clear()

    def delete(self, key):
        if key in self.config:
            del self.config[key]
            self.save_config()

    def clear(self):
        self.config = {}
        self.save_config()
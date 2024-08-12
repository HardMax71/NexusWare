import json
import os
from datetime import datetime, timedelta


class Cache:
    def __init__(self, cache_dir='cache'):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def _get_cache_path(self, key):
        return os.path.join(self.cache_dir, f"{key}.json")

    def set(self, key, value, expire_in_seconds=3600):
        cache_data = {
            'value': value,
            'expires_at': (datetime.now() + timedelta(seconds=expire_in_seconds)).isoformat()
        }
        with open(self._get_cache_path(key), 'w') as f:
            json.dump(cache_data, f)

    def get(self, key):
        try:
            with open(self._get_cache_path(key), 'r') as f:
                cache_data = json.load(f)

            if datetime.now() < datetime.fromisoformat(cache_data['expires_at']):
                return cache_data['value']
            else:
                self.delete(key)
                return None
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return None

    def delete(self, key):
        try:
            os.remove(self._get_cache_path(key))
        except FileNotFoundError:
            pass

    def clear(self):
        for filename in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")

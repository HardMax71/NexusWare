# src/nexusware/utils/cache_manager.py
import json
import os
from datetime import datetime, timedelta
from typing import Any


class CacheManager:
    def __init__(self, cache_dir: str = '.cache'):
        self.cache_dir = cache_dir
        self.memory_cache: dict[str, dict] = {}
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _get_cache_path(self, key: str) -> str:
        """Get file path for cache key"""
        return os.path.join(self.cache_dir, f"{key}.json")

    def set(self, key: str, value: Any, expires_in: int | None = None):
        """Set value in cache"""
        cache_data = {
            'value': value,
            'timestamp': datetime.now().timestamp(),
            'expires_in': expires_in
        }

        # Memory cache
        self.memory_cache[key] = cache_data

        # Disk cache
        try:
            cache_path = self._get_cache_path(key)
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            print(f"Failed to write to cache: {str(e)}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        # Try memory cache first
        if key in self.memory_cache:
            cache_data = self.memory_cache[key]
            if self._is_valid(cache_data):
                return cache_data['value']
            else:
                del self.memory_cache[key]

        # Try disk cache
        try:
            cache_path = self._get_cache_path(key)
            if os.path.exists(cache_path):
                with open(cache_path, 'r') as f:
                    cache_data = json.load(f)

                if self._is_valid(cache_data):
                    # Update memory cache
                    self.memory_cache[key] = cache_data
                    return cache_data['value']
                else:
                    # Remove expired cache
                    os.remove(cache_path)
        except Exception as e:
            print(f"Failed to read from cache: {str(e)}")

        return default

    def _is_valid(self, cache_data: dict) -> bool:
        """Check if cache entry is still valid"""
        if not cache_data.get('expires_in'):
            return True

        timestamp = cache_data['timestamp']
        expires_in = cache_data['expires_in']

        expiry_time = datetime.fromtimestamp(timestamp) + timedelta(seconds=expires_in)
        return datetime.now() < expiry_time

    def delete(self, key: str):
        """Delete value from cache"""
        # Remove from memory cache
        if key in self.memory_cache:
            del self.memory_cache[key]

        # Remove from disk cache
        try:
            cache_path = self._get_cache_path(key)
            if os.path.exists(cache_path):
                os.remove(cache_path)
        except Exception as e:
            print(f"Failed to delete from cache: {str(e)}")

    def clear(self):
        """Clear all cache"""
        # Clear memory cache
        self.memory_cache.clear()

        # Clear disk cache
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, filename))
        except Exception as e:
            print(f"Failed to clear cache: {str(e)}")

    def get_size(self) -> int:
        """Get total size of cache in bytes"""
        total_size = 0
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.cache_dir, filename)
                total_size += os.path.getsize(file_path)
        return total_size

    def cleanup_expired(self):
        """Remove all expired cache entries"""
        # Clean memory cache
        expired_keys = [
            key for key, data in self.memory_cache.items()
            if not self._is_valid(data)
        ]
        for key in expired_keys:
            del self.memory_cache[key]

        # Clean disk cache
        try:
            for filename in os.listdir(self.cache_dir):
                if not filename.endswith('.json'):
                    continue

                file_path = os.path.join(self.cache_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        cache_data = json.load(f)

                    if not self._is_valid(cache_data):
                        os.remove(file_path)
                except:
                    # Remove corrupted cache files
                    os.remove(file_path)
        except Exception as e:
            print(f"Failed to cleanup cache: {str(e)}")

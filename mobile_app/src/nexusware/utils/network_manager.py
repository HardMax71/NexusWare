# src/nexusware/utils/network_manager.py
from typing import Dict, Any
from urllib.parse import urljoin

import aiohttp


class NetworkManager:
    def __init__(self):
        self.base_url = "http://localhost:8000"  # Default base URL
        self.session = None
        self.token = None
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    async def initialize(self):
        """Initialize aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

    async def close(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None

    def set_base_url(self, url: str):
        """Set API base URL"""
        self.base_url = url

    def set_token(self, token: str):
        """Set authentication token"""
        self.token = token
        if token:
            self.headers['Authorization'] = f'Bearer {token}'
        elif 'Authorization' in self.headers:
            del self.headers['Authorization']

    async def request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make HTTP request"""
        if not self.session:
            await self.initialize()

        url = urljoin(self.base_url, endpoint)

        # Add headers
        kwargs['headers'] = {**self.headers, **(kwargs.get('headers', {}))}

        try:
            async with self.session.request(method, url, **kwargs) as response:
                if response.status == 401:
                    # Handle token refresh here if needed
                    raise Exception("Unauthorized")

                if response.status not in (200, 201, 204):
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")

                if response.status == 204:
                    return None

                return await response.json()

        except aiohttp.ClientError as e:
            raise Exception(f"Network error: {str(e)}")

    async def get(self, endpoint: str, params: Dict | None = None) -> Any:
        """Make GET request"""
        return await self.request('GET', endpoint, params=params)

    async def post(self, endpoint: str, data: Dict | None = None) -> Any:
        """Make POST request"""
        return await self.request('POST', endpoint, json=data)

    async def put(self, endpoint: str, data: Dict | None = None) -> Any:
        """Make PUT request"""
        return await self.request('PUT', endpoint, json=data)

    async def delete(self, endpoint: str) -> Any:
        """Make DELETE request"""
        return await self.request('DELETE', endpoint)

    async def upload_file(self, endpoint: str, file_path: str, **kwargs) -> Any:
        """Upload file to server"""
        if not self.session:
            await self.initialize()

        url = urljoin(self.base_url, endpoint)

        with open(file_path, 'rb') as f:
            data = aiohttp.FormData()
            data.add_field('file',
                           f,
                           filename=file_path.split('/')[-1],
                           content_type='application/octet-stream')

            async with self.session.post(url, data=data, headers=self.headers) as response:
                if response.status not in (200, 201):
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")

                return await response.json()

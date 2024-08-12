import requests

from desktop_app.src.config import API_BASE_URL


class APIClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.token = None

    def set_token(self, token):
        self.token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def get(self, endpoint, params=None, headers=None):
        response = self.session.get(f"{self.base_url}{endpoint}", params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint, data=None, json=None, headers=None, params=None):
        response = self.session.post(f"{self.base_url}{endpoint}",
                                     data=data, json=json, headers=headers,
                                     params=params)
        response.raise_for_status()
        return response.json()

    def put(self, endpoint, data=None, json=None, headers=None):
        response = self.session.put(f"{self.base_url}{endpoint}", data=data, json=json, headers=headers)
        response.raise_for_status()
        return response.json()

    def delete(self, endpoint, headers=None):
        response = self.session.delete(f"{self.base_url}{endpoint}", headers=headers)
        response.raise_for_status()
        return response.json()

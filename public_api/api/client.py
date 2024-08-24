# public_api/api/client.py
from datetime import datetime, timedelta

import requests
from requests import HTTPError

from public_api.shared_schemas import Token


class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token: str | None = None
        self.refresh_token: str | None = None
        self.token_expiry: datetime | None = None

    def set_tokens(self, access_token: str, refresh_token: str, expires_in: int):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
        self.session.headers.update({"Authorization": f"Bearer {access_token}"})

    def refresh_access_token(self) -> bool:
        if not self.refresh_token:
            return False

        try:
            response = self.request_call("POST", "/users/refresh-token",
                                         json={
                                             "refresh_token": self.refresh_token
                                         })
            token = Token.model_validate(response)
            self.set_tokens(token.access_token, token.refresh_token, token.expires_in)
            return True
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return False

    def is_token_expired(self) -> bool:
        if self.token_expiry is None:
            return self.access_token is None
        return datetime.utcnow() >= self.token_expiry

    def request(self, method: str, endpoint: str, **kwargs):
        if self.is_token_expired():
            if self.refresh_token and not self.refresh_access_token():
                raise HTTPError("Unable to refresh token")

        try:
            return self.request_call(method, endpoint, **kwargs)
        except HTTPError as e:
            if e.response.status_code == 401:  # Unauthorized
                if self.refresh_access_token():
                    return self.request_call(method, endpoint, **kwargs)
            raise

    def request_call(self, method: str, endpoint: str, **kwargs):
        response = self.session.request(method, f"{self.base_url}{endpoint}", **kwargs)
        response.raise_for_status()
        if response.status_code == 204:
            return None
        return response.json()

    def get(self, endpoint: str, params: dict | None = None, headers: dict | None = None):
        return self.request("GET", endpoint, params=params, headers=headers)

    def post(self, endpoint: str, data: dict | None = None, json: dict | None = None, headers: dict | None = None,
             params: dict | None = None):
        return self.request("POST", endpoint, data=data, json=json, headers=headers, params=params)

    def put(self, endpoint: str, data: dict | None = None, json: dict | None = None, headers: dict | None = None):
        return self.request("PUT", endpoint, data=data, json=json, headers=headers)

    def delete(self, endpoint: str, headers: dict | None = None):
        return self.request("DELETE", endpoint, headers=headers)

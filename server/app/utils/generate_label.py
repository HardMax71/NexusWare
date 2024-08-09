# /server/app/utils/generate_label.py
# Utility function for ShipEngine API calls
import requests
from fastapi import HTTPException

from server.app.core.config import settings


def shipengine_api_call(endpoint, method="GET", data=None):
    headers = {
        "API-Key": settings.SHIPENGINE_API_KEY,
        "Content-Type": "application/json"
    }
    url = f"{settings.SHIPENGINE_API_URL}/{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"ShipEngine API error: {str(e)}")

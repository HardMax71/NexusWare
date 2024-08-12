from typing import Optional

from .client import APIClient


class LocationsAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_location(self, location_data: dict):
        return self.client.post("/locations/", json=location_data)

    def get_locations(self, skip: int = 0, limit: int = 100, location_filter: Optional[dict] = None):
        return self.client.get("/locations/", params={"skip": skip, "limit": limit, **(location_filter or {})})

    def get_location(self, location_id: int):
        return self.client.get(f"/locations/{location_id}")

    def update_location(self, location_id: int, location_data: dict):
        return self.client.put(f"/locations/{location_id}", json=location_data)

    def delete_location(self, location_id: int):
        return self.client.delete(f"/locations/{location_id}")

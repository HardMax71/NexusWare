from public_api.shared_schemas.inventory import (
    LocationCreate, LocationUpdate, Location, LocationWithInventory, LocationFilter
)
from .client import APIClient


class LocationsAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_location(self, location_data: LocationCreate) -> Location:
        response = self.client.post("/locations/", json=location_data.model_dump(mode="json"))
        return Location.model_validate(response)

    def get_locations(self, skip: int = 0, limit: int = 100,
                      location_filter: LocationFilter | None = None) -> list[LocationWithInventory]:
        params = {"skip": skip, "limit": limit}
        if location_filter:
            params.update(location_filter.model_dump(mode="json", exclude_unset=True))
        response = self.client.get("/locations/", params=params)
        return [LocationWithInventory.model_validate(item) for item in response]

    def get_location(self, location_id: int) -> LocationWithInventory:
        response = self.client.get(f"/locations/{location_id}")
        return LocationWithInventory.model_validate(response)

    def update_location(self, location_id: int, location_data: LocationUpdate) -> Location:
        response = self.client.put(f"/locations/{location_id}",
                                   json=location_data.model_dump(mode="json", exclude_unset=True))
        return Location.model_validate(response)

    def delete_location(self, location_id: int) -> Location:
        response = self.client.delete(f"/locations/{location_id}")
        return Location.model_validate(response)

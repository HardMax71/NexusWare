from typing import List

from public_api.api.client import APIClient
from public_api.shared_schemas import CarrierCreate, CarrierUpdate, Carrier


class CarriersAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_carrier(self, carrier_data: CarrierCreate) -> Carrier:
        response = self.client.post("/carriers/", json=carrier_data.model_dump(mode="json"))
        return Carrier.model_validate(response)

    def get_carriers(self, skip: int = 0, limit: int = 100) -> List[Carrier]:
        response = self.client.get("/carriers/", params={"skip": skip, "limit": limit})
        return [Carrier.model_validate(item) for item in response]

    def get_carrier(self, carrier_id: int) -> Carrier:
        response = self.client.get(f"/carriers/{carrier_id}")
        return Carrier.model_validate(response)

    def update_carrier(self, carrier_id: int, carrier_data: CarrierUpdate) -> Carrier:
        response = self.client.put(f"/carriers/{carrier_id}",
                                   json=carrier_data.model_dump(mode="json", exclude_unset=True))
        return Carrier.model_validate(response)

    def delete_carrier(self, carrier_id: int) -> None:
        self.client.delete(f"/carriers/{carrier_id}")

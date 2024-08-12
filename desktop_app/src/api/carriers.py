from .client import APIClient


class CarriersAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_carrier(self, carrier_data: dict):
        return self.client.post("/carriers/", json=carrier_data)

    def get_carriers(self, skip: int = 0, limit: int = 100):
        return self.client.get("/carriers/", params={"skip": skip, "limit": limit})

    def get_carrier(self, carrier_id: int):
        return self.client.get(f"/carriers/{carrier_id}")

    def update_carrier(self, carrier_id: int, carrier_data: dict):
        return self.client.put(f"/carriers/{carrier_id}", json=carrier_data)

    def delete_carrier(self, carrier_id: int):
        return self.client.delete(f"/carriers/{carrier_id}")

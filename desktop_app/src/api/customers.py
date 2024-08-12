from typing import Optional

from .client import APIClient


class CustomersAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_customer(self, customer_data: dict):
        return self.client.post("/customers/", json=customer_data)

    def get_customers(self, skip: int = 0, limit: int = 100, customer_filter: Optional[dict] = None):
        return self.client.get("/customers/", params={"skip": skip, "limit": limit, **(customer_filter or {})})

    def get_customer(self, customer_id: int):
        return self.client.get(f"/customers/{customer_id}")

    def update_customer(self, customer_id: int, customer_data: dict):
        return self.client.put(f"/customers/{customer_id}", json=customer_data)

    def delete_customer(self, customer_id: int):
        return self.client.delete(f"/customers/{customer_id}")

    def get_customer_orders(self, customer_id: int, skip: int = 0, limit: int = 100):
        return self.client.get(f"/customers/{customer_id}/orders", params={"skip": skip, "limit": limit})

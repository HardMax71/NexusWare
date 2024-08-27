from public_api.shared_schemas import (
    CustomerCreate, CustomerUpdate, Customer, CustomerFilter, Order
)
from .client import APIClient


class CustomersAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_customer(self, customer_data: CustomerCreate) -> Customer:
        response = self.client.post("/customers/", json=customer_data.model_dump(mode="json"))
        return Customer.model_validate(response)

    def get_customers(self, skip: int = 0, limit: int = 100,
                      customer_filter: CustomerFilter | None = None) -> list[Customer]:
        params = {"skip": skip, "limit": limit}
        if customer_filter:
            params.update(customer_filter.model_dump(mode="json", exclude_unset=True))
        response = self.client.get("/customers/", params=params)
        return [Customer.model_validate(item) for item in response]

    def get_customer(self, customer_id: int) -> Customer:
        response = self.client.get(f"/customers/{customer_id}")
        return Customer.model_validate(response)

    def update_customer(self, customer_id: int, customer_data: CustomerUpdate) -> Customer:
        response = self.client.put(f"/customers/{customer_id}",
                                   json=customer_data.model_dump(mode="json", exclude_unset=True))
        return Customer.model_validate(response)

    def delete_customer(self, customer_id: int) -> None:
        self.client.delete(f"/customers/{customer_id}")

    def get_customer_orders(self, customer_id: int, skip: int = 0, limit: int = 100) -> list[Order]:
        response = self.client.get(f"/customers/{customer_id}/orders", params={"skip": skip, "limit": limit})
        return [Order.model_validate(item) for item in response]

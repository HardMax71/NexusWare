from public_api.shared_schemas import (
    Supplier, SupplierCreate, SupplierUpdate, SupplierFilter, PurchaseOrder
)
from .client import APIClient


class SuppliersAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def get_suppliers(self, skip: int = 0, limit: int = 100,
                      filter_params: SupplierFilter | None = None) -> list[Supplier]:
        params = {"skip": skip, "limit": limit}
        if filter_params:
            params.update(filter_params.model_dump(mode="json", exclude_unset=True))
        response = self.client.get("/suppliers/", params=params)
        return [Supplier.model_validate(item) for item in response]

    def get_supplier(self, supplier_id: int) -> Supplier:
        response = self.client.get(f"/suppliers/{supplier_id}")
        return Supplier.model_validate(response)

    def create_supplier(self, supplier_data: SupplierCreate) -> Supplier:
        response = self.client.post("/suppliers/", json=supplier_data.model_dump(mode="json"))
        return Supplier.model_validate(response)

    def update_supplier(self, supplier_id: int, supplier_data: SupplierUpdate) -> Supplier:
        response = self.client.put(f"/suppliers/{supplier_id}",
                                   json=supplier_data.model_dump(mode="json", exclude_unset=True))
        return Supplier.model_validate(response)

    def delete_supplier(self, supplier_id: int) -> None:
        self.client.delete(f"/suppliers/{supplier_id}")

    def get_supplier_purchase_orders(self, supplier_id: int,
                                     skip: int = 0, limit: int = 100) -> list[PurchaseOrder]:
        response = self.client.get(f"/suppliers/{supplier_id}/purchase_orders",
                                   params={"skip": skip, "limit": limit})
        return [PurchaseOrder.model_validate(item) for item in response]

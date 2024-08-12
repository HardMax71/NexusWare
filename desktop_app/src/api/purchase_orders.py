from typing import Optional, List

from .client import APIClient


class PurchaseOrdersAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_purchase_order(self, purchase_order_data: dict):
        return self.client.post("/purchase_orders/", json=purchase_order_data)

    def get_purchase_orders(self, skip: int = 0, limit: int = 100, po_filter: Optional[dict] = None):
        return self.client.get("/purchase_orders/", params={"skip": skip, "limit": limit, **(po_filter or {})})

    def get_purchase_order(self, po_id: int):
        return self.client.get(f"/purchase_orders/{po_id}")

    def update_purchase_order(self, po_id: int, po_data: dict):
        return self.client.put(f"/purchase_orders/{po_id}", json=po_data)

    def delete_purchase_order(self, po_id: int):
        return self.client.delete(f"/purchase_orders/{po_id}")

    def receive_purchase_order(self, po_id: int, received_items: List[dict]):
        return self.client.post(f"/purchase_orders/{po_id}/receive", json={"received_items": received_items})

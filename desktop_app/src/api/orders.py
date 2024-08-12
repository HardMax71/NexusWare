from datetime import datetime
from typing import Optional

from .client import APIClient


class OrdersAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_order(self, order_data: dict):
        return self.client.post("/orders/", json=order_data)

    def get_orders(self, skip: int = 0, limit: int = 100, filter_params: Optional[dict] = None):
        return self.client.get("/orders/", params={"skip": skip, "limit": limit, **(filter_params or {})})

    def get_order(self, order_id: int):
        return self.client.get(f"/orders/{order_id}")

    def update_order(self, order_id: int, order_data: dict):
        return self.client.put(f"/orders/{order_id}", json=order_data)

    def delete_order(self, order_id: int):
        return self.client.delete(f"/orders/{order_id}")

    def get_order_summary(self, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None):
        params = {}
        if date_from:
            params["date_from"] = date_from.isoformat()
        if date_to:
            params["date_to"] = date_to.isoformat()
        return self.client.get("/orders/summary", params=params)

    def cancel_order(self, order_id: int):
        return self.client.post(f"/orders/{order_id}/cancel")

    def ship_order(self, order_id: int, shipping_info: dict):
        return self.client.post(f"/orders/{order_id}/ship", json=shipping_info)

    def cancel_order_item(self, order_id: int, item_id: int):
        return self.client.post(f"/orders/{order_id}/cancel_item", json={"item_id": item_id})

    def add_order_item(self, order_id: int, item_data: dict):
        return self.client.post(f"/orders/{order_id}/add_item", json=item_data)

    def get_backorders(self):
        return self.client.get("/orders/backorders")

    def bulk_import_orders(self, import_data: dict):
        return self.client.post("/orders/bulk_import", json=import_data)

    def get_order_processing_times(self, start_date: datetime, end_date: datetime):
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        return self.client.get("/orders/processing_times", params=params)

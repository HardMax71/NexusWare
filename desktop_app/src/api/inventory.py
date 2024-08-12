from datetime import datetime
from typing import Optional, List

from .client import APIClient


class InventoryAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_inventory(self, inventory_data: dict):
        return self.client.post("/inventory/", json=inventory_data)

    def get_inventory(self, skip: int = 0, limit: int = 100, inventory_filter: Optional[dict] = None):
        params = {"skip": skip, "limit": limit}
        if inventory_filter:
            params.update(inventory_filter)
        return self.client.get("/inventory", params=params)

    def get_inventory_item(self, inventory_id: int):
        return self.client.get(f"/inventory/{inventory_id}")

    def update_inventory(self, inventory_id: int, inventory_data: dict):
        return self.client.put(f"/inventory/{inventory_id}", json=inventory_data)

    def adjust_inventory(self, inventory_id: int, adjustment_data: dict):
        return self.client.post(f"/inventory/{inventory_id}/adjust", json=adjustment_data)

    def transfer_inventory(self, transfer_data: dict):
        return self.client.post("/inventory/transfer", json=transfer_data)

    def get_inventory_report(self):
        return self.client.get("/inventory/report")

    def perform_cycle_count(self, location_id: int, counted_items: List[dict]):
        return self.client.post("/inventory/cycle_count", json={"location_id": location_id, "counted_items": counted_items})

    def get_low_stock_items(self, threshold: int = 10):
        return self.client.get("/inventory/low_stock", params={"threshold": threshold})

    def get_out_of_stock_items(self):
        return self.client.get("/inventory/out_of_stock")

    def create_reorder_list(self, threshold: int = 10):
        return self.client.post("/inventory/reorder", params={"threshold": threshold})

    def get_product_locations(self, product_id: int):
        return self.client.get(f"/inventory/product_locations/{product_id}")

    def batch_update_inventory(self, updates: List[dict]):
        return self.client.post("/inventory/batch_update", json=updates)

    def get_inventory_movement_history(self, product_id: int, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        params = {}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
        return self.client.get(f"/inventory/movement_history/{product_id}", params=params)

    def get_inventory_summary(self):
        return self.client.get("/inventory/summary")

    def perform_stocktake(self, stocktake_data: dict):
        return self.client.post("/inventory/stocktake", json=stocktake_data)

    def perform_abc_analysis(self):
        return self.client.get("/inventory/abc_analysis")

    def optimize_inventory_locations(self):
        return self.client.post("/inventory/optimize_locations")

    def get_expiring_soon_inventory(self, days: int = 30):
        return self.client.get("/inventory/expiring_soon", params={"days": days})

    def bulk_import_inventory(self, import_data: dict):
        return self.client.post("/inventory/bulk_import", json=import_data)

    def get_storage_utilization(self):
        return self.client.get("/inventory/storage_utilization")

from datetime import datetime

from .client import APIClient


class WarehouseAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def get_warehouse_layout(self):
        return self.client.get("/warehouse/layout")

    def get_warehouse_stats(self):
        return self.client.get("/warehouse/stats")

    def get_location_inventory(self, location_id):
        return self.client.get(f"/warehouse/inventory/{location_id}")

    def update_location_inventory(self, location_id, product_id, inventory_update):
        return self.client.put(f"/warehouse/inventory/{location_id}/{product_id}", json=inventory_update)

    def move_inventory(self, movement_data):
        return self.client.post("/warehouse/inventory/move", json=movement_data)

    def adjust_inventory(self, adjustment_data):
        return self.client.post("/warehouse/inventory/adjust", json=adjustment_data)

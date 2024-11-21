from typing import List

from public_api.api.client import APIClient
from public_api.shared_schemas import WarehouseLayout, WarehouseStats, LocationInventory, LocationInventoryUpdate, \
    InventoryMovement, InventoryAdjustment


class WarehouseAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def get_warehouse_layout(self) -> WarehouseLayout:
        response = self.client.get("/warehouse/layout")
        return WarehouseLayout.model_validate(response)

    def get_warehouse_stats(self) -> WarehouseStats:
        response = self.client.get("/warehouse/stats")
        return WarehouseStats.model_validate(response)

    def get_location_inventory(self, location_id: int) -> List[LocationInventory]:
        response = self.client.get(f"/warehouse/inventory/{location_id}")
        return [LocationInventory.model_validate(item) for item in response]

    def update_location_inventory(self, location_id: int, product_id: int,
                                  inventory_update: LocationInventoryUpdate) -> LocationInventory:
        response = self.client.put(f"/warehouse/inventory/{location_id}/{product_id}",
                                   json=inventory_update.model_dump(mode="json"))
        return LocationInventory.model_validate(response)

    def move_inventory(self, movement_data: InventoryMovement) -> InventoryMovement:
        response = self.client.post("/warehouse/inventory/move",
                                    json=movement_data.model_dump(mode="json"))
        return InventoryMovement.model_validate(response)

    def adjust_inventory(self, adjustment_data: InventoryAdjustment) -> InventoryAdjustment:
        response = self.client.post("/warehouse/inventory/adjust",
                                    json=adjustment_data.model_dump(mode="json"))
        return InventoryAdjustment.model_validate(response)

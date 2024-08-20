from typing import Optional, List, Dict

from public_api.shared_schemas import (
    InventoryCreate, InventoryUpdate, Inventory, InventoryList, InventoryFilter,
    InventoryTransfer, InventoryReport, ProductWithInventory, Product,
    LocationWithInventory, InventoryMovement, InventorySummary, StocktakeCreate,
    StocktakeResult, ABCAnalysisResult, InventoryLocationSuggestion,
    BulkImportData, BulkImportResult, StorageUtilization, InventoryAdjustment
)
from .client import APIClient


class InventoryAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_inventory(self, inventory_data: InventoryCreate) -> Inventory:
        response = self.client.post("/inventory/", json=inventory_data.model_dump(mode="json"))
        return Inventory.model_validate(response)

    def get_inventory(self, skip: int = 0, limit: int = 100,
                      inventory_filter: Optional[InventoryFilter] = None) -> InventoryList:
        params = {"skip": skip, "limit": limit}
        if inventory_filter:
            params.update(inventory_filter.model_dump(mode="json", exclude_unset=True))
        response = self.client.get("/inventory", params=params)
        return InventoryList.model_validate(response)

    def get_inventory_item(self, id: int) -> Inventory:
        response = self.client.get(f"/inventory/{id}")
        return Inventory.model_validate(response)

    def update_inventory(self, id: int, inventory_data: InventoryUpdate) -> Inventory:
        response = self.client.put(f"/inventory/{id}",
                                   json=inventory_data.model_dump(mode="json", exclude_unset=True))
        return Inventory.model_validate(response)

    def adjust_inventory(self, id: int, adjustment_data: InventoryAdjustment) -> Inventory:
        response = self.client.post(f"/inventory/{id}/adjust", json=adjustment_data.model_dump(mode="json"))
        return Inventory.model_validate(response)

    def transfer_inventory(self, transfer_data: InventoryTransfer) -> Inventory:
        response = self.client.post("/inventory/transfer", json=transfer_data.model_dump(mode="json"))
        return Inventory.model_validate(response)

    def get_inventory_report(self) -> InventoryReport:
        response = self.client.get("/inventory/report")
        return InventoryReport.model_validate(response)

    def perform_cycle_count(self, location_id: int, counted_items: List[InventoryUpdate]) -> List[Inventory]:
        response = self.client.post("/inventory/cycle_count", json={
            "location_id": location_id,
            "counted_items": [item.model_dump(mode="json") for item in counted_items]
        })
        return [Inventory.model_validate(item) for item in response]

    def get_low_stock_items(self, threshold: int = 10) -> List[ProductWithInventory]:
        response = self.client.get("/inventory/low_stock", params={"threshold": threshold})
        return [ProductWithInventory.model_validate(item) for item in response]

    def get_out_of_stock_items(self) -> List[Product]:
        response = self.client.get("/inventory/out_of_stock")
        return [Product.model_validate(item) for item in response]

    def create_reorder_list(self, threshold: int = 10) -> List[Product]:
        response = self.client.post("/inventory/reorder", params={"threshold": threshold})
        return [Product.model_validate(item) for item in response]

    def get_product_locations(self, product_id: int) -> List[LocationWithInventory]:
        response = self.client.get(f"/inventory/product_locations/{product_id}")
        return [LocationWithInventory.model_validate(item) for item in response]

    def batch_update_inventory(self, updates: List[InventoryUpdate]) -> List[Inventory]:
        response = self.client.post("/inventory/batch_update",
                                    json=[update.model_dump(mode="json") for update in updates])
        return [Inventory.model_validate(item) for item in response]

    def get_inventory_movement_history(self, product_id: int, start_date: Optional[int] = None,
                                       end_date: Optional[int] = None) -> List[InventoryMovement]:
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        response = self.client.get(f"/inventory/movement_history/{product_id}", params=params)
        return [InventoryMovement.model_validate(item) for item in response]

    def get_inventory_summary(self) -> InventorySummary:
        response = self.client.get("/inventory/summary")
        return InventorySummary.model_validate(response)

    def perform_stocktake(self, stocktake_data: StocktakeCreate) -> StocktakeResult:
        response = self.client.post("/inventory/stocktake", json=stocktake_data.model_dump(mode="json"))
        return StocktakeResult.model_validate(response)

    def perform_abc_analysis(self) -> ABCAnalysisResult:
        response = self.client.get("/inventory/abc_analysis")
        return ABCAnalysisResult.model_validate(response)

    def optimize_inventory_locations(self) -> List[InventoryLocationSuggestion]:
        response = self.client.post("/inventory/optimize_locations")
        return [InventoryLocationSuggestion.model_validate(item) for item in response]

    def get_expiring_soon_inventory(self, days: int = 30) -> List[ProductWithInventory]:
        response = self.client.get("/inventory/expiring_soon", params={"days": days})
        return [ProductWithInventory.model_validate(item) for item in response]

    def bulk_import_inventory(self, import_data: BulkImportData) -> BulkImportResult:
        response = self.client.post("/inventory/bulk_import", json=import_data.model_dump(mode="json"))
        return BulkImportResult.model_validate(response)

    def get_storage_utilization(self) -> StorageUtilization:
        response = self.client.get("/inventory/storage_utilization")
        return StorageUtilization.model_validate(response)

    def get_inventory_forecast(self, product_id: int) -> Dict:
        response = self.client.get(f"/inventory/forecast/{product_id}")
        return response

    def get_reorder_suggestions(self) -> List[Dict]:
        response = self.client.get("/inventory/reorder_suggestions")
        return response

    def delete_inventory_item(self, id: int) -> Inventory:
        response = self.client.delete(f"/inventory/{id}")
        return Inventory.model_validate(response)

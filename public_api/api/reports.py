from typing import List

from public_api.api import APIClient
from public_api.shared_schemas import (
    InventorySummaryReport, OrderSummaryReport, WarehousePerformanceReport, KPIDashboard, InventoryTrendItem
)


class ReportsAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def get_inventory_summary(self) -> InventorySummaryReport:
        response = self.client.get("/reports/inventory_summary")
        return InventorySummaryReport.model_validate(response)

    def get_order_summary(self, start_date: int, end_date: int) -> OrderSummaryReport:
        params = {"start_date": start_date, "end_date": end_date}
        response = self.client.get("/reports/order_summary", params=params)
        return OrderSummaryReport.model_validate(response)

    def get_warehouse_performance(self, start_date: int, end_date: int) -> WarehousePerformanceReport:
        params = {"start_date": start_date, "end_date": end_date}
        response = self.client.get("/reports/warehouse_performance", params=params)
        return WarehousePerformanceReport.model_validate(response)

    def get_kpi_dashboard(self) -> KPIDashboard:
        response = self.client.get("/reports/kpi_dashboard")
        return KPIDashboard.model_validate(response)

    def get_inventory_trend(self, days_past: int = 5, days_future: int = 5) -> dict[str, List[InventoryTrendItem]]:
        response = self.client.get(
            "/inventory/trend",
            params={"days_past": days_past, "days_future": days_future}
        )
        past_items = [InventoryTrendItem.model_validate(item) for item in response["past"]]
        prediction_items = [InventoryTrendItem.model_validate(item) for item in response["predictions"]]
        return {"past": past_items, "predictions": prediction_items}

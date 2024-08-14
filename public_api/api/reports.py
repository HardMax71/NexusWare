from public_api.shared_schemas.reports import (
    InventorySummaryReport, OrderSummaryReport, WarehousePerformanceReport, KPIDashboard
)
from .client import APIClient


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

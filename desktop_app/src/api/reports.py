from .client import APIClient


class ReportsAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def get_inventory_summary(self):
        return self.client.get("/reports/inventory_summary")

    def get_order_summary(self, start_date, end_date):
        params = {"start_date": start_date, "end_date": end_date}
        return self.client.get("/reports/order_summary", params=params)

    def get_warehouse_performance(self, start_date, end_date):
        params = {"start_date": start_date, "end_date": end_date}
        return self.client.get("/reports/warehouse_performance", params=params)

    def get_kpi_dashboard(self):
        return self.client.get("/reports/kpi_dashboard")

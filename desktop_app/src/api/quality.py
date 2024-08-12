from datetime import datetime
from typing import Optional, List

from .client import APIClient


class QualityAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_quality_check(self, check_data: dict):
        return self.client.post("/quality/checks", json=check_data)

    def get_quality_checks(self, skip: int = 0, limit: int = 100, filter_params: Optional[dict] = None):
        return self.client.get("/quality/checks", params={"skip": skip, "limit": limit, **(filter_params or {})})

    def get_quality_check(self, check_id: int):
        return self.client.get(f"/quality/checks/{check_id}")

    def update_quality_check(self, check_id: int, check_data: dict):
        return self.client.put(f"/quality/checks/{check_id}", json=check_data)

    def delete_quality_check(self, check_id: int):
        return self.client.delete(f"/quality/checks/{check_id}")

    def get_quality_metrics(self, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None):
        params = {}
        if date_from:
            params["date_from"] = date_from.isoformat()
        if date_to:
            params["date_to"] = date_to.isoformat()
        return self.client.get("/quality/metrics", params=params)

    def create_quality_standard(self, standard_data: dict):
        return self.client.post("/quality/standards", json=standard_data)

    def get_quality_standards(self, skip: int = 0, limit: int = 100):
        return self.client.get("/quality/standards", params={"skip": skip, "limit": limit})

    def get_quality_standard(self, standard_id: int):
        return self.client.get(f"/quality/standards/{standard_id}")

    def update_quality_standard(self, standard_id: int, standard_data: dict):
        return self.client.put(f"/quality/standards/{standard_id}", json=standard_data)

    def delete_quality_standard(self, standard_id: int):
        return self.client.delete(f"/quality/standards/{standard_id}")

    def create_quality_alert(self, alert_data: dict):
        return self.client.post("/quality/alerts", json=alert_data)

    def get_quality_alerts(self, skip: int = 0, limit: int = 100):
        return self.client.get("/quality/alerts", params={"skip": skip, "limit": limit})

    def resolve_quality_alert(self, alert_id: int, resolution_data: dict):
        return self.client.put(f"/quality/alerts/{alert_id}/resolve", json=resolution_data)

    def get_product_quality_history(self, product_id: int, skip: int = 0, limit: int = 100):
        return self.client.get(f"/quality/product/{product_id}/history", params={"skip": skip, "limit": limit})

    def get_quality_check_summary(self, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None):
        params = {}
        if date_from:
            params["date_from"] = date_from.isoformat()
        if date_to:
            params["date_to"] = date_to.isoformat()
        return self.client.get("/quality/checks/summary", params=params)

    def get_product_quality_standards(self, product_id: int):
        return self.client.get(f"/quality/product/{product_id}/standards")

    def create_batch_quality_check(self, checks: List[dict]):
        return self.client.post("/quality/batch_check", json=checks)

    def get_active_quality_alerts(self, skip: int = 0, limit: int = 100):
        return self.client.get("/quality/alerts/active", params={"skip": skip, "limit": limit})

    def add_comment_to_quality_check(self, check_id: int, comment_data: dict):
        return self.client.post(f"/quality/checks/{check_id}/comment", json=comment_data)

    def get_product_defect_rates(self, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None):
        params = {}
        if date_from:
            params["date_from"] = date_from.isoformat()
        if date_to:
            params["date_to"] = date_to.isoformat()
        return self.client.get("/quality/reports/defect_rate", params=params)

from datetime import datetime
from typing import Optional
from .client import APIClient

class AuditAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_audit_log(self, log_data: dict):
        return self.client.post("/audit/logs", json=log_data)

    def get_audit_logs(self, skip: int = 0, limit: int = 100, filter_params: Optional[dict] = None):
        return self.client.get("/audit/logs", params={"skip": skip, "limit": limit, **(filter_params or {})})

    def get_audit_log(self, log_id: int):
        return self.client.get(f"/audit/logs/{log_id}")

    def get_audit_summary(self, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None):
        params = {}
        if date_from:
            params["date_from"] = date_from.isoformat()
        if date_to:
            params["date_to"] = date_to.isoformat()
        return self.client.get("/audit/logs/summary", params=params)

    def get_user_audit_logs(self, user_id: int, skip: int = 0, limit: int = 100):
        return self.client.get(f"/audit/logs/user/{user_id}", params={"skip": skip, "limit": limit})

    def get_table_audit_logs(self, table_name: str, skip: int = 0, limit: int = 100):
        return self.client.get(f"/audit/logs/table/{table_name}", params={"skip": skip, "limit": limit})

    def get_record_audit_logs(self, table_name: str, record_id: int, skip: int = 0, limit: int = 100):
        return self.client.get(f"/audit/logs/record/{table_name}/{record_id}", params={"skip": skip, "limit": limit})

    def export_audit_logs(self, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None):
        params = {}
        if date_from:
            params["date_from"] = date_from.isoformat()
        if date_to:
            params["date_to"] = date_to.isoformat()
        return self.client.get("/audit/logs/export", params=params)

    def get_audit_log_actions(self):
        return self.client.get("/audit/logs/actions")

    def get_audited_tables(self):
        return self.client.get("/audit/logs/tables")
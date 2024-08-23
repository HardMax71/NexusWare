from public_api.shared_schemas import (
    AuditLogCreate, AuditLog, AuditLogWithUser, AuditLogFilter,
    AuditSummary, AuditLogExport
)
from .client import APIClient


class AuditAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_audit_log(self, log: AuditLogCreate) -> AuditLog:
        response = self.client.post("/audit/logs", json=log.model_dump(mode="json"))
        return AuditLog.model_validate(response)

    def get_audit_logs(self, skip: int = 0, limit: int = 100,
                       filter_params: AuditLogFilter | None = None) -> list[AuditLogWithUser]:
        params = {"skip": skip, "limit": limit}
        if filter_params:
            params.update(filter_params.model_dump(mode="json", exclude_unset=True))
        response = self.client.get("/audit/logs", params=params)
        return [AuditLogWithUser.model_validate(item) for item in response]

    def get_audit_log(self, log_id: int) -> AuditLogWithUser:
        response = self.client.get(f"/audit/logs/{log_id}")
        return AuditLogWithUser.model_validate(response)

    def get_audit_summary(self, date_from: int | None = None,
                          date_to: int | None = None) -> AuditSummary:
        params = {}
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        response = self.client.get("/audit/logs/summary", params=params)
        return AuditSummary.model_validate(response)

    def get_user_audit_logs(self, user_id: int, skip: int = 0, limit: int = 100) -> list[AuditLog]:
        response = self.client.get(f"/audit/logs/user/{user_id}", params={"skip": skip, "limit": limit})
        return [AuditLog.model_validate(item) for item in response]

    def get_table_audit_logs(self, table_name: str, skip: int = 0, limit: int = 100) -> list[AuditLog]:
        response = self.client.get(f"/audit/logs/table/{table_name}", params={"skip": skip, "limit": limit})
        return [AuditLog.model_validate(item) for item in response]

    def get_record_audit_logs(self, table_name: str, record_id: int,
                              skip: int = 0, limit: int = 100) -> list[AuditLog]:
        response = self.client.get(f"/audit/logs/record/{table_name}/{record_id}",
                                   params={"skip": skip, "limit": limit})
        return [AuditLog.model_validate(item) for item in response]

    def export_audit_logs(self, date_from: int | None = None,
                          date_to: int | None = None) -> AuditLogExport:
        params = {}
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        response = self.client.get("/audit/logs/export", params=params)
        return AuditLogExport.model_validate(response)

    def get_audit_log_actions(self) -> list[str]:
        response = self.client.get("/audit/logs/actions")
        return [str(item) for item in response]

    def get_audited_tables(self) -> list[str]:
        response = self.client.get("/audit/logs/tables")
        return [str(item) for item in response]

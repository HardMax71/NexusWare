from pydantic import BaseModel, ConfigDict

from .user import UserSanitized


class AuditLogBase(BaseModel):
    user_id: int
    action_type: str
    table_name: str
    record_id: int
    old_value: str | None = None
    new_value: str | None = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLog(AuditLogBase):
    id: int
    timestamp: int

    model_config = ConfigDict(from_attributes=True)


class AuditLogWithUser(AuditLog):
    user: UserSanitized

    model_config = ConfigDict(from_attributes=True)


class AuditLogFilter(BaseModel):
    user_id: int | None = None
    action_type: str | None = None
    table_name: str | None = None
    record_id: int | None = None
    date_from: int | None = None
    date_to: int | None = None


class UserActivitySummary(BaseModel):
    user_id: int
    username: str
    total_actions: int


class AuditSummary(BaseModel):
    total_logs: int
    logs_by_action: dict[str, int]
    logs_by_table: dict[str, int]
    most_active_users: list[UserActivitySummary]


class AuditLogExport(BaseModel):
    logs: list[AuditLog]
    export_timestamp: int


class AuditLogList(BaseModel):
    logs: list[AuditLog]
    total: int

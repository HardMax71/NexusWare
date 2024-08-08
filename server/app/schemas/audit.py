# /server/app/schemas/audit.py
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from .user import User


class AuditLogBase(BaseModel):
    user_id: int
    action_type: str
    table_name: str
    record_id: int
    old_value: str
    new_value: str


class AuditLogCreate(AuditLogBase):
    pass


class AuditLog(AuditLogBase):
    log_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class AuditLogWithUser(AuditLog):
    user: "User"


class AuditLogFilter(BaseModel):
    user_id: Optional[int] = None
    action_type: Optional[str] = None
    table_name: Optional[str] = None
    record_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class AuditSummary(BaseModel):
    total_logs: int
    logs_by_action: dict
    logs_by_table: dict
    most_active_users: List["UserActivitySummary"]


class UserActivitySummary(BaseModel):
    user_id: int
    username: str
    total_actions: int


class AuditLogExport(BaseModel):
    logs: List[AuditLog]
    export_timestamp: datetime

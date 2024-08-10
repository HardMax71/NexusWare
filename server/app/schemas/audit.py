# /server/app/schemas/audit_log.py
from datetime import datetime
from typing import Optional, List, Dict

from pydantic import BaseModel

from .user import User


class AuditLogBase(BaseModel):
    user_id: int
    action_type: str
    table_name: str
    record_id: int
    old_value: Optional[str] = None
    new_value: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLog(AuditLogBase):
    log_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class AuditLogWithUser(AuditLog):
    user: User

    class Config:
        from_attributes = True


class AuditLogFilter(BaseModel):
    user_id: Optional[int] = None
    action_type: Optional[str] = None
    table_name: Optional[str] = None
    record_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class UserActivitySummary(BaseModel):
    user_id: int
    username: str
    total_actions: int


class AuditSummary(BaseModel):
    total_logs: int
    logs_by_action: Dict[str, int]
    logs_by_table: Dict[str, int]
    most_active_users: List[UserActivitySummary]


class AuditLogExport(BaseModel):
    logs: List[AuditLog]
    export_timestamp: datetime


class AuditLogList(BaseModel):
    logs: List[AuditLog]
    total: int
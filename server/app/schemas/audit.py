# /server/app/schemas/audit.py
from datetime import datetime

from pydantic import BaseModel


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

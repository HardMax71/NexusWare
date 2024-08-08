# /server/app/schemas/task.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TaskBase(BaseModel):
    task_type: str
    description: str
    assigned_to: int
    due_date: datetime
    priority: str
    status: str


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    task_type: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class Task(TaskBase):
    task_id: int
    created_at: datetime

    class Config:
        from_attributes = True

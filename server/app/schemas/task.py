# /server/app/schemas/task.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .user import User


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


class TaskWithAssignee(Task):
    assigned_user: "User"


class TaskFilter(BaseModel):
    task_type: Optional[str] = None
    assigned_to: Optional[int] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date_from: Optional[datetime] = None
    due_date_to: Optional[datetime] = None


class TaskComment(BaseModel):
    comment_id: int
    task_id: int
    user_id: int
    comment: str
    created_at: datetime


class TaskCommentCreate(BaseModel):
    comment: str


class TaskStatistics(BaseModel):
    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    high_priority_tasks: int


class UserTaskSummary(BaseModel):
    user_id: int
    username: str
    assigned_tasks: int
    completed_tasks: int
    overdue_tasks: int

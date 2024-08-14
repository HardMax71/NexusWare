# /server/app/shared_schemas/task.py
from typing import Optional, List

from pydantic import BaseModel

from .user import User


class TaskBase(BaseModel):
    task_type: str
    description: str
    assigned_to: int
    due_date: int
    priority: str
    status: str


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    task_type: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[int] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class Task(TaskBase):
    task_id: int
    created_at: int

    class Config:
        from_attributes = True


class TaskWithAssignee(Task):
    assigned_user: User


class TaskFilter(BaseModel):
    task_type: Optional[str] = None
    assigned_to: Optional[int] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date_from: Optional[int] = None
    due_date_to: Optional[int] = None


class TaskCommentBase(BaseModel):
    task_id: int
    user_id: int
    comment: str


class TaskCommentCreate(TaskCommentBase):
    pass


class TaskComment(TaskCommentBase):
    comment_id: int
    created_at: int

    class Config:
        from_attributes = True


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


class TaskWithComments(Task):
    comments: List[TaskComment] = []


class TaskPriorityUpdate(BaseModel):
    priority: str


class TaskAssignmentUpdate(BaseModel):
    assigned_to: int


class TaskStatusUpdate(BaseModel):
    status: str


class TaskDueDateUpdate(BaseModel):
    due_date: int


class TaskProgressUpdate(BaseModel):
    progress: int  # Percentage of completion


class TaskDependency(BaseModel):
    task_id: int
    dependent_task_id: int


class TaskDependencyCreate(BaseModel):
    dependent_task_id: int


class TaskTimeline(BaseModel):
    task_id: int
    task_type: str
    description: str
    start_date: int
    end_date: int


class TaskTypeDistribution(BaseModel):
    task_type: str
    count: int
    percentage: float


class TaskAnalytics(BaseModel):
    total_tasks: int
    completion_rate: float
    average_completion_time: float
    type_distribution: List[TaskTypeDistribution]


class BulkTaskCreate(BaseModel):
    tasks: List[TaskCreate]


class BulkTaskCreateResult(BaseModel):
    success_count: int
    failure_count: int
    errors: List[str]

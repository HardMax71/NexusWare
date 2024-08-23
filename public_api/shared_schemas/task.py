# /server/app/shared_schemas/task.py
from enum import Enum

from pydantic import BaseModel

from .user import UserSanitized


class TaskStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TaskType(str, Enum):
    FEATURE = "Feature"
    BUGFIX = "Bugfix"
    IMPROVEMENT = "Improvement"
    RESEARCH = "Research"
    OTHER = "Other"


class TaskBase(BaseModel):
    task_type: TaskType
    description: str
    assigned_to: int
    due_date: int
    priority: TaskPriority
    status: TaskStatus


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    task_type: TaskType | None = None
    description: str | None = None
    assigned_to: int | None = None
    due_date: int | None = None
    priority: TaskPriority | None = None
    status: TaskStatus | None = None


class Task(TaskBase):
    id: int
    created_at: int

    class Config:
        from_attributes = True


class TaskWithAssignee(Task):
    assigned_user: UserSanitized | None = None


class TaskFilter(BaseModel):
    task_type: TaskType | None = None
    assigned_to: int | None = None
    priority: TaskPriority | None = None
    status: TaskStatus | None = None
    due_date_from: int | None = None
    due_date_to: int | None = None


class TaskCommentBase(BaseModel):
    task_id: int
    user_id: int
    comment: str


class TaskCommentCreate(TaskCommentBase):
    pass


class TaskComment(TaskCommentBase):
    id: int
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
    comments: list[TaskComment] = []


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
    type_distribution: list[TaskTypeDistribution]


class BulkTaskCreate(BaseModel):
    tasks: list[TaskCreate]


class BulkTaskCreateResult(BaseModel):
    success_count: int
    failure_count: int
    errors: list[str]

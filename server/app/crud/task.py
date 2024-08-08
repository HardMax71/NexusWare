# /server/app/crud/task.py
from server.app.models import Task
from server.app.schemas import TaskCreate, TaskUpdate

from .base import CRUDBase


class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    pass


task = CRUDTask(Task)

# /server/app/crud/task.py
from datetime import datetime
from typing import List, Optional

from sqlalchemy import func, case
from sqlalchemy.orm import Session

from server.app.models import Task, User, TaskComment
from server.app.schemas import TaskCreate, TaskUpdate, TaskFilter, TaskCommentCreate, TaskStatistics, UserTaskSummary
from .base import CRUDBase


class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    def get_multi_with_filter(self, db: Session, *, skip: int = 0, limit: int = 100, filter_params: TaskFilter) -> List[
        Task]:
        query = db.query(self.model).join(User)
        if filter_params.task_type:
            query = query.filter(Task.task_type == filter_params.task_type)
        if filter_params.assigned_to:
            query = query.filter(Task.assigned_to == filter_params.assigned_to)
        if filter_params.priority:
            query = query.filter(Task.priority == filter_params.priority)
        if filter_params.status:
            query = query.filter(Task.status == filter_params.status)
        if filter_params.due_date_from:
            query = query.filter(Task.due_date >= filter_params.due_date_from)
        if filter_params.due_date_to:
            query = query.filter(Task.due_date <= filter_params.due_date_to)
        return query.offset(skip).limit(limit).all()

    def get_with_assignee(self, db: Session, id: int) -> Optional[Task]:
        return db.query(self.model).filter(self.model.task_id == id).join(User).first()

    def complete(self, db: Session, *, db_obj: Task) -> Task:
        db_obj.status = "completed"
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def add_comment(self, db: Session, *, task_id: int, comment: TaskCommentCreate, user_id: int) -> TaskComment:
        db_comment = TaskComment(
            task_id=task_id,
            user_id=user_id,
            comment=comment.comment
        )
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment

    def get_comments(self, db: Session, *, task_id: int, skip: int = 0, limit: int = 100) -> List[TaskComment]:
        return db.query(TaskComment).filter(TaskComment.task_id == task_id).offset(skip).limit(limit).all()

    def get_statistics(self, db: Session) -> TaskStatistics:
        total_tasks = db.query(func.count(Task.task_id)).scalar()
        completed_tasks = db.query(func.count(Task.task_id)).filter(Task.status == "completed").scalar()
        overdue_tasks = db.query(func.count(Task.task_id)).filter(Task.due_date < datetime.utcnow(),
                                                                  Task.status != "completed").scalar()
        high_priority_tasks = db.query(func.count(Task.task_id)).filter(Task.priority == "high").scalar()

        return TaskStatistics(
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            overdue_tasks=overdue_tasks,
            high_priority_tasks=high_priority_tasks
        )

    def get_user_summary(self, db: Session) -> List[UserTaskSummary]:
        query = db.query(
            User.user_id,
            User.username,
            func.count(Task.task_id).label("assigned_tasks"),
            func.sum(case((Task.status == "completed", 1), else_=0)).label("completed_tasks"),
            func.sum(case((Task.due_date < func.now(), Task.status != "completed", 1), else_=0)).label("overdue_tasks")
        ).outerjoin(Task, User.user_id == Task.assigned_to).group_by(User.user_id)

        return [
            UserTaskSummary(
                user_id=row.id,
                username=row.username,
                assigned_tasks=row.assigned_tasks,
                completed_tasks=row.completed_tasks,
                overdue_tasks=row.overdue_tasks
            )
            for row in query.all()
        ]

    def get_overdue(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Task]:
        return db.query(self.model).filter(Task.due_date < datetime.utcnow(),
                                           Task.status != "completed").offset(
            skip).limit(limit).all()

    def create_batch(self, db: Session, *, obj_in_list: List[TaskCreate]) -> List[Task]:
        db_objs = [Task(**obj_in.dict()) for obj_in in obj_in_list]
        db.add_all(db_objs)
        db.commit()
        for obj in db_objs:
            db.refresh(obj)
        return db_objs

    def get_user_tasks(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        return db.query(self.model).filter(Task.assigned_to == user_id).offset(skip).limit(limit).all()


task = CRUDTask(Task)

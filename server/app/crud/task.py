from sqlalchemy import func, case
from sqlalchemy.orm import Session

from public_api.shared_schemas import TaskCreate, TaskUpdate, TaskFilter, TaskCommentCreate, TaskStatistics, \
    UserTaskSummary, \
    Task as TaskSchema, TaskComment as TaskCommentSchema
from server.app.models import Task, User, TaskComment
from .base import CRUDBase


class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    def get_multi_with_filter(self, db: Session, *,
                              skip: int = 0, limit: int = 100, filter_params: TaskFilter) -> list[TaskSchema]:
        query = db.query(self.model).join(User)
        if filter_params.id:
            query = query.filter(Task.id == filter_params.id)
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

        tasks = query.offset(skip).limit(limit).all()
        return [TaskSchema.model_validate(x) for x in tasks]

    def complete(self, db: Session, *, db_obj: Task) -> TaskSchema:
        db_obj.status = "completed"
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return TaskSchema.model_validate(db_obj)

    def add_comment(self, db: Session, *, task_id: int, comment: TaskCommentCreate, user_id: int) -> TaskCommentSchema:
        db_comment = TaskComment(
            task_id=task_id,
            user_id=user_id,
            comment=comment.comment
        )
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return TaskCommentSchema.model_validate(db_comment)

    def get_comments(self, db: Session, *, task_id: int, skip: int = 0, limit: int = 100) -> list[TaskCommentSchema]:
        comments = db.query(TaskComment).filter(TaskComment.task_id == task_id).offset(skip).limit(limit).all()
        return [TaskCommentSchema.model_validate(comment) for comment in comments]

    def get_statistics(self, db: Session) -> TaskStatistics:
        total_tasks = db.query(func.count(Task.id)).scalar()
        completed_tasks = db.query(func.count(Task.id)).filter(Task.status == "completed").scalar()
        overdue_tasks = db.query(func.count(Task.id)).filter(Task.due_date < func.now(),
                                                             Task.status != "completed").scalar()
        high_priority_tasks = db.query(func.count(Task.id)).filter(Task.priority == "high").scalar()

        return TaskStatistics(
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            overdue_tasks=overdue_tasks,
            high_priority_tasks=high_priority_tasks
        )

    def get_user_summary(self, db: Session) -> list[UserTaskSummary]:
        query = db.query(
            User.id,
            User.username,
            func.count(Task.id).label("assigned_tasks"),
            func.sum(case((Task.status == "completed", 1), else_=0)).label("completed_tasks"),
            func.sum(case((Task.due_date < func.now(), Task.status != "completed", 1),
                          else_=0)).label("overdue_tasks")
        ).outerjoin(Task, User.id == Task.assigned_to).group_by(User.id)

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

    def get_overdue(self, db: Session, *, skip: int = 0, limit: int = 100) -> list[TaskSchema]:
        overdue_tasks = (db.query(self.model)
                         .filter(Task.due_date < func.now(),
                                 Task.status != "completed")
                         .offset(skip).limit(limit)
                         .all())
        return [TaskSchema.model_validate(task) for task in overdue_tasks]

    def create_batch(self, db: Session, *, obj_in_list: list[TaskCreate]) -> list[TaskSchema]:
        db_objs = [Task(**obj_in.model_dump()) for obj_in in obj_in_list]
        db.add_all(db_objs)
        db.commit()
        for obj in db_objs:
            db.refresh(obj)
        return [TaskSchema.model_validate(obj) for obj in db_objs]

    def get_user_tasks(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> list[TaskSchema]:
        tasks = (db.query(self.model)
                 .filter(Task.assigned_to == user_id)
                 .offset(skip).limit(limit)
                 .all())
        return [TaskSchema.model_validate(task) for task in tasks]


task = CRUDTask(Task)

# /server/app/api/v1/endpoints/tasks.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Body
from sqlalchemy.orm import Session

from .... import crud, models, schemas
from ....api import deps

router = APIRouter()


@router.post("/", response_model=schemas.Task)
def create_task(
        task: schemas.TaskCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.task.create(db=db, obj_in=task)


@router.get("/", response_model=List[schemas.TaskWithAssignee])
def read_tasks(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        filter_params: schemas.TaskFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.task.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=filter_params)


@router.get("/{task_id}", response_model=schemas.TaskWithAssignee)
def read_task(
        task_id: int = Path(..., title="The ID of the task to get"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    task = crud.task.get_with_assignee(db, id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=schemas.Task)
def update_task(
        task_id: int = Path(..., title="The ID of the task to update"),
        task_in: schemas.TaskUpdate = Body(..., title="Task update data"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    task = crud.task.get(db, id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.task.update(db, db_obj=task, obj_in=task_in)


@router.delete("/{task_id}", response_model=schemas.Task)
def delete_task(
        task_id: int = Path(..., title="The ID of the task to delete"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    task = crud.task.get(db, id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.task.remove(db, id=task_id)


@router.post("/{task_id}/complete", response_model=schemas.Task)
def complete_task(
        task_id: int = Path(..., title="The ID of the task to complete"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    task = crud.task.get(db, id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.task.complete(db, db_obj=task)


@router.post("/{task_id}/comment", response_model=schemas.TaskComment)
def add_task_comment(
        task_id: int = Path(..., title="The ID of the task to comment on"),
        comment: schemas.TaskCommentCreate = Body(..., title="Task comment data"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.task.add_comment(db, task_id=task_id, comment=comment, user_id=current_user.user_id)


@router.get("/{task_id}/comments", response_model=List[schemas.TaskComment])
def get_task_comments(
        task_id: int = Path(..., title="The ID of the task to get comments for"),
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.task.get_comments(db, task_id=task_id, skip=skip, limit=limit)


@router.get("/statistics", response_model=schemas.TaskStatistics)
def get_task_statistics(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.task.get_statistics(db)


@router.get("/user-summary", response_model=List[schemas.UserTaskSummary])
def get_user_task_summary(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.task.get_user_summary(db)


@router.get("/overdue", response_model=List[schemas.TaskWithAssignee])
def get_overdue_tasks(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.task.get_overdue(db, skip=skip, limit=limit)


@router.post("/batch-create", response_model=List[schemas.Task])
def create_batch_tasks(
        tasks: List[schemas.TaskCreate],
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.task.create_batch(db=db, obj_in_list=tasks)


@router.get("/my-tasks", response_model=List[schemas.Task])
def get_my_tasks(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.task.get_user_tasks(db, user_id=current_user.user_id, skip=skip, limit=limit)

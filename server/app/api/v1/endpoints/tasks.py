# /server/app/api/v1/endpoints/tasks.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Body
from sqlalchemy.orm import Session

from public_api import shared_schemas
from .... import crud, models
from ....api import deps

router = APIRouter()


@router.post("/", response_model=shared_schemas.Task)
def create_task(
        task: shared_schemas.TaskCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.task.create(db=db, obj_in=task)


@router.get("/", response_model=List[shared_schemas.TaskWithAssignee])
def read_tasks(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        filter_params: shared_schemas.TaskFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.task.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=filter_params)


@router.get("/statistics", response_model=shared_schemas.TaskStatistics)
def get_task_statistics(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.task.get_statistics(db)


@router.get("/user_summary", response_model=List[shared_schemas.UserTaskSummary])
def get_user_task_summary(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.task.get_user_summary(db)


@router.get("/overdue", response_model=List[shared_schemas.TaskWithAssignee])
def get_overdue_tasks(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.task.get_overdue(db, skip=skip, limit=limit)


@router.post("/batch_create", response_model=List[shared_schemas.Task])
def create_batch_tasks(
        tasks: List[shared_schemas.TaskCreate],
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.task.create_batch(db=db, obj_in_list=tasks)


@router.get("/my_tasks", response_model=List[shared_schemas.Task])
def get_my_tasks(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    filter_params = shared_schemas.TaskFilter(assigned_to=current_user.id)
    return crud.task.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=filter_params)


@router.get("/{task_id}", response_model=shared_schemas.TaskWithAssignee)
def read_task(
        task_id: int = Path(..., title="The ID of the task to get"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    task = crud.task.get(db, id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=shared_schemas.Task)
def update_task(
        task_id: int = Path(..., title="The ID of the task to update"),
        task_in: shared_schemas.TaskUpdate = Body(..., title="Task update data"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    task = crud.task.get(db, id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.task.update(db, db_obj=task, obj_in=task_in)


@router.delete("/{task_id}", status_code=204)
def delete_task(
        task_id: int = Path(..., title="The ID of the task to delete"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    task = crud.task.get(db, id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    crud.task.remove(db, id=task_id)


@router.post("/{task_id}/complete", response_model=shared_schemas.Task)
def complete_task(
        task_id: int = Path(..., title="The ID of the task to complete"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    task = crud.task.get(db, id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.task.complete(db, db_obj=task)


@router.post("/{task_id}/comment", response_model=shared_schemas.TaskComment)
def add_task_comment(
        task_id: int = Path(..., title="The ID of the task to comment on"),
        comment: shared_schemas.TaskCommentCreate = Body(..., title="Task comment data"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.task.add_comment(db, task_id=task_id, comment=comment, user_id=current_user.id)


@router.get("/{task_id}/comments", response_model=List[shared_schemas.TaskComment])
def get_task_comments(
        task_id: int = Path(..., title="The ID of the task to get comments for"),
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.task.get_comments(db, task_id=task_id, skip=skip, limit=limit)

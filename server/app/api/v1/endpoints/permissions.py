# /server/app/api/v1/endpoints/permissions.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .... import crud, models, schemas
from ....api import deps

router = APIRouter()


@router.post("/", response_model=schemas.Permission)
def create_permission(
        permission: schemas.PermissionCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    new_permission = crud.permission.create(db=db, obj_in=permission)
    return schemas.Permission.model_validate(new_permission)


@router.get("/", response_model=List[schemas.Permission])
def read_permissions(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    permissions = crud.permission.get_multi(db, skip=skip, limit=limit)
    return [schemas.Permission.model_validate(perm) for perm in permissions]


@router.get("/{permission_id}", response_model=schemas.Permission)
def read_permission(
        permission_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    permission = crud.permission.get(db, id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return schemas.Permission.model_validate(permission)


@router.put("/{permission_id}", response_model=schemas.Permission)
def update_permission(
        permission_id: int,
        permission_in: schemas.PermissionUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    permission = crud.permission.get(db, id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    updated_permission = crud.permission.update(db, db_obj=permission, obj_in=permission_in)
    return schemas.Permission.model_validate(updated_permission)


@router.delete("/{permission_id}", response_model=schemas.Permission)
def delete_permission(
        permission_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    permission = crud.permission.get(db, id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    deleted_permission = crud.permission.remove(db, id=permission_id)
    return schemas.Permission.model_validate(deleted_permission)

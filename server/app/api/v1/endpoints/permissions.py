# /server/app/api/v1/endpoints/permissions.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .... import crud, models
from public_api import shared_schemas
from ....api import deps

router = APIRouter()


@router.post("/", response_model=shared_schemas.Permission)
def create_permission(
        permission: shared_schemas.PermissionCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    new_permission = crud.permission.create(db=db, obj_in=permission)
    return shared_schemas.Permission.model_validate(new_permission)


@router.get("/", response_model=List[shared_schemas.Permission])
def read_permissions(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.permission.get_multi(db, skip=skip, limit=limit)


@router.get("/{permission_id}", response_model=shared_schemas.Permission)
def read_permission(
        permission_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    permission = crud.permission.get(db, id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return shared_schemas.Permission.model_validate(permission)


@router.put("/{permission_id}", response_model=shared_schemas.Permission)
def update_permission(
        permission_id: int,
        permission_in: shared_schemas.PermissionUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    permission = crud.permission.get(db, id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    updated_permission = crud.permission.update(db, db_obj=permission, obj_in=permission_in)
    return shared_schemas.Permission.model_validate(updated_permission)


@router.delete("/{permission_id}", response_model=shared_schemas.Permission)
def delete_permission(
        permission_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    permission = crud.permission.get(db, id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    deleted_permission = crud.permission.remove(db, id=permission_id)
    return shared_schemas.Permission.model_validate(deleted_permission)

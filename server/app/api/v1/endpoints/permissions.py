# /server/app/api/v1/endpoints/permissions.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps
from public_api import shared_schemas

router = APIRouter()


@router.post("/", response_model=shared_schemas.Permission)
def create_permission(
        permission: shared_schemas.PermissionCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    return crud.permission.create(db=db, obj_in=permission)


@router.get("/", response_model=list[shared_schemas.Permission])
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
    return permission


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
    return crud.permission.update(db, db_obj=permission, obj_in=permission_in)


@router.delete("/{permission_id}", status_code=204)
def delete_permission(
        permission_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    permission = crud.permission.get(db, id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    crud.permission.remove(db, id=permission_id)

# /server/app/api/v1/endpoints/roles.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps
from public_api import shared_schemas

router = APIRouter()


@router.get("/", response_model=list[shared_schemas.Role])
def read_roles(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    roles = crud.role.get_multi(db, skip=skip, limit=limit)
    return [shared_schemas.Role.model_validate(role) for role in roles]


@router.post("/", response_model=shared_schemas.Role)
def create_role(
        role: shared_schemas.RoleCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    db_role = crud.role.create(db=db, obj_in=role)
    return shared_schemas.Role.model_validate(db_role)


@router.get("/permissions", response_model=shared_schemas.AllPermissions)
def read_permissions(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    permissions = crud.permission.get_multi(db)
    return shared_schemas.AllPermissions(permissions=permissions)


@router.post("/permissions", response_model=shared_schemas.Permission)
def create_permission(
        permission: shared_schemas.PermissionCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    return crud.permission.create(db=db, obj_in=permission)


@router.put("/permissions/{permission_id}", response_model=shared_schemas.Permission)
def update_permission(
        permission_id: int,
        permission: shared_schemas.PermissionUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    db_permission = crud.permission.get(db, id=permission_id)
    if not db_permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return crud.permission.update(db=db, db_obj=db_permission, obj_in=permission)


@router.delete("/permissions/{permission_id}", status_code=204)
def delete_permission(
        permission_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    permission = crud.permission.get(db, id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    crud.permission.remove(db=db, id=permission_id)


@router.get("/{role_id}", response_model=shared_schemas.Role)
def read_role(
        role_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.put("/{role_id}", response_model=shared_schemas.Role)
def update_role(
        role_id: int,
        role: shared_schemas.RoleUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    db_role = crud.role.get(db, id=role_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    updated_role = crud.role.update(db=db, db_obj=db_role, obj_in=role)
    return shared_schemas.Role.model_validate(updated_role)


@router.delete("/{role_id}", status_code=204)
def delete_role(
        role_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    crud.role.remove(db=db, id=role_id)

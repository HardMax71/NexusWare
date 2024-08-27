# /server/app/api/v1/endpoints/roles.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from public_api import shared_schemas
from .... import crud, models
from ....api import deps

router = APIRouter()


@router.post("/", response_model=shared_schemas.Role)
def create_role(
        role: shared_schemas.RoleCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    return crud.role.create_with_permissions(db=db, obj_in=role)


@router.get("/", response_model=list[shared_schemas.Role])
def read_roles(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.role.get_multi(db, skip=skip, limit=limit)


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
    return crud.role.update_with_permissions(db=db, db_obj=db_role, obj_in=role)


@router.delete("/{role_id}", status_code=204)
def delete_role(
        role_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    crud.role.remove(db, id=role_id)

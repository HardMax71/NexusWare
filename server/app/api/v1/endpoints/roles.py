# /server/app/api/v1/endpoints/roles.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .... import crud, models, schemas
from ....api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Role])
def read_roles(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    roles = crud.role.get_multi(db, skip=skip, limit=limit)
    return [schemas.Role.model_validate(role) for role in roles]


@router.get("/{role_id}", response_model=schemas.Role)
def read_role(
        role_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return schemas.Role.model_validate(role)


@router.put("/{role_id}", response_model=schemas.Role)
def update_role(
        role_id: int,
        role_in: schemas.RoleUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    updated_role = crud.role.update(db, db_obj=role, obj_in=role_in)
    return schemas.Role.model_validate(updated_role)


@router.delete("/{role_id}", response_model=schemas.Role)
def delete_role(
        role_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    deleted_role = crud.role.remove(db, id=role_id)
    return schemas.Role.model_validate(deleted_role)

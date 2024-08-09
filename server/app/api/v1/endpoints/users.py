# /server/app/api/v1/endpoints/users.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .... import crud, models, schemas
from ....api import deps
from ....core import security
from ....core.email import send_reset_password_email

router = APIRouter()


@router.post("/login", response_model=schemas.Token)
def login(
        db: Session = Depends(deps.get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
):
    user = crud.user.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token = security.create_access_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=schemas.User)
def register_user(
        user: schemas.UserCreate,
        db: Session = Depends(deps.get_db)
):
    db_user = crud.user.get_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.user.create(db=db, obj_in=user)


@router.post("/reset-password", response_model=schemas.Message)
def reset_password(
        email: str = Body(..., embed=True),
        db: Session = Depends(deps.get_db)
):
    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = security.generate_password_reset_token(email=email)
    crud.user.set_reset_password_token(db, user=user, token=token)

    result = send_reset_password_email(email=email, token=token)
    return {"message": result}


@router.get("/me", response_model=schemas.User)
def read_users_me(
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return current_user


@router.put("/me", response_model=schemas.User)
def update_user_me(
        user_in: schemas.UserUpdate,
        current_user: models.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)
):
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/", response_model=List[schemas.User])
def read_users(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=schemas.User)
def create_user(
        user: schemas.UserCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    db_user = crud.user.get_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.user.create(db=db, obj_in=user)


@router.get("/{user_id}", response_model=schemas.User)
def read_user(
        user_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    user = crud.user.get(db, id=user_id)
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return user


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
        user_id: int,
        user_in: schemas.UserUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}", response_model=schemas.User)
def delete_user(
        user_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = crud.user.remove(db, id=user_id)
    return user


# Role management
@router.post("/roles", response_model=schemas.Role)
def create_role(
        role: schemas.RoleCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    return crud.role.create(db=db, obj_in=role)


@router.get("/roles", response_model=List[schemas.Role])
def read_roles(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    roles = crud.role.get_multi(db, skip=skip, limit=limit)
    return roles


@router.get("/roles/{role_id}", response_model=schemas.Role)
def read_role(
        role_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.put("/roles/{role_id}", response_model=schemas.Role)
def update_role(
        role_id: int,
        role_in: schemas.RoleUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    role = crud.role.update(db, db_obj=role, obj_in=role_in)
    return role


@router.delete("/roles/{role_id}", response_model=schemas.Role)
def delete_role(
        role_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    role = crud.role.remove(db, id=role_id)
    return role


# Permission management
@router.post("/permissions", response_model=schemas.Permission)
def create_permission(
        permission: schemas.PermissionCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    return crud.permission.create(db=db, obj_in=permission)


@router.get("/permissions", response_model=List[schemas.Permission])
def read_permissions(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    permissions = crud.permission.get_multi(db, skip=skip, limit=limit)
    return permissions


@router.get("/permissions/{permission_id}", response_model=schemas.Permission)
def read_permission(
        permission_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    permission = crud.permission.get(db, id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission


@router.put("/permissions/{permission_id}", response_model=schemas.Permission)
def update_permission(
        permission_id: int,
        permission_in: schemas.PermissionUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    permission = crud.permission.get(db, id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    permission = crud.permission.update(db, db_obj=permission, obj_in=permission_in)
    return permission


@router.delete("/permissions/{permission_id}", response_model=schemas.Permission)
def delete_permission(
        permission_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    permission = crud.permission.get(db, id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    permission = crud.permission.remove(db, id=permission_id)
    return permission

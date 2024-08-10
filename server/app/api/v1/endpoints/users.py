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
    new_user = crud.user.create(db=db, obj_in=user)
    return schemas.User.model_validate(new_user)


@router.post("/reset-password", response_model=schemas.Message)
def reset_password(
        email: str = Body(..., embed=True),
        db: Session = Depends(deps.get_db)
):
    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )

    token = security.generate_password_reset_token(email=email)
    crud.user.set_reset_password_token(db, user=user, token=token)

    result = send_reset_password_email(email=email, token=token)
    return {"message": result}


@router.get("/me", response_model=schemas.User)
def read_users_me(
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return schemas.User.model_validate(current_user)


@router.put("/me", response_model=schemas.User)
def update_user_me(
        user_in: schemas.UserUpdate,
        current_user: models.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)
):
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return schemas.User.model_validate(user)


@router.get("/", response_model=List[schemas.User])
def read_users(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return [schemas.User.model_validate(user) for user in users]


@router.post("/", response_model=schemas.User)
def create_user(
        user: schemas.UserCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    db_user = crud.user.get_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = crud.user.create(db=db, obj_in=user)
    return schemas.User.model_validate(new_user)


@router.get("/{user_id}", response_model=schemas.User)
def read_user(
        user_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.user_id:
        return schemas.User.model_validate(user)
    if not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return schemas.User.model_validate(user)


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
    updated_user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return schemas.User.model_validate(updated_user)


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
    return schemas.User.model_validate(user)


# Role management
@router.get("/roles", response_model=List[schemas.Role])
def read_roles(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    roles = crud.role.get_multi(db, skip=skip, limit=limit)
    return [schemas.Role.model_validate(role) for role in roles]


@router.get("/roles/{role_id}", response_model=schemas.Role)
def read_role(
        role_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return schemas.Role.model_validate(role)


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
    updated_role = crud.role.update(db, db_obj=role, obj_in=role_in)
    return schemas.Role.model_validate(updated_role)


@router.delete("/roles/{role_id}", response_model=schemas.Role)
def delete_role(
        role_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    deleted_role = crud.role.remove(db, id=role_id)
    return schemas.Role.model_validate(deleted_role)


@router.post("/permissions", response_model=schemas.Permission)
def create_permission(
        permission: schemas.PermissionCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    new_permission = crud.permission.create(db=db, obj_in=permission)
    return schemas.Permission.model_validate(new_permission)


@router.get("/permissions", response_model=List[schemas.Permission])
def read_permissions(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    permissions = crud.permission.get_multi(db, skip=skip, limit=limit)
    return [schemas.Permission.model_validate(perm) for perm in permissions]


@router.get("/permissions/{permission_id}", response_model=schemas.Permission)
def read_permission(
        permission_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    permission = crud.permission.get(db, id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return schemas.Permission.model_validate(permission)


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
    updated_permission = crud.permission.update(db, db_obj=permission, obj_in=permission_in)
    return schemas.Permission.model_validate(updated_permission)


@router.delete("/permissions/{permission_id}", response_model=schemas.Permission)
def delete_permission(
        permission_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    permission = crud.permission.get(db, id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    deleted_permission = crud.permission.remove(db, id=permission_id)
    return schemas.Permission.model_validate(deleted_permission)

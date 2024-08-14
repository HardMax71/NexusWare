# /server/app/api/v1/endpoints/users.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload

from .... import crud, models
from public_api import shared_schemas
from ....api import deps
from ....core import security
from ....core.email import send_reset_password_email

router = APIRouter()


@router.post("/login", response_model=shared_schemas.Token)
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


@router.post("/register", response_model=shared_schemas.User)
def register_user(
        user: shared_schemas.UserCreate,
        db: Session = Depends(deps.get_db)
):
    db_user = crud.user.get_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = crud.user.create(db=db, obj_in=user)
    return shared_schemas.User.model_validate(new_user)


@router.post("/reset_password", response_model=shared_schemas.Message)
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


@router.get("/me", response_model=shared_schemas.UserSanitizedWithRole)
def read_users_me(
        current_user: models.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)
):
    user = (db.query(models.User)
            .options(joinedload(models.User.role))
            .filter(models.User.id == current_user.id)
            .first())
    return shared_schemas.UserSanitizedWithRole.model_validate(user)


@router.put("/me", response_model=shared_schemas.User)
def update_user_me(
        user_in: shared_schemas.UserUpdate,
        current_user: models.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)
):
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return shared_schemas.User.model_validate(user)


@router.get("/", response_model=List[shared_schemas.UserSanitizedWithRole])
def read_users(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    users = crud.user.get_multi_with_role(db, skip=skip, limit=limit)
    return [shared_schemas.UserSanitizedWithRole.model_validate(user) for user in users]


@router.post("/", response_model=shared_schemas.UserSanitizedWithRole)
def create_user(
        user: shared_schemas.UserCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    db_user = crud.user.get_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = crud.user.create(db=db, obj_in=user)
    return shared_schemas.UserSanitizedWithRole.model_validate(new_user)


@router.get("/{user_id}", response_model=shared_schemas.UserSanitizedWithRole)
def read_user(
        user_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.user_id:
        return shared_schemas.User.model_validate(user)
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return shared_schemas.UserSanitizedWithRole.model_validate(user)


@router.put("/{user_id}", response_model=shared_schemas.User)
def update_user(
        user_id: int,
        user_in: shared_schemas.UserUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return shared_schemas.User.model_validate(updated_user)


@router.delete("/{user_id}", response_model=shared_schemas.User)
def delete_user(
        user_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = crud.user.remove(db, id=user_id)
    return shared_schemas.User.model_validate(user)





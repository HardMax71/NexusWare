# /server/app/api/v1/endpoints/users.py
from datetime import datetime

import pyotp
from fastapi import APIRouter, Depends, HTTPException, Body, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from public_api.shared_schemas import user as user_schemas
from app import crud, models
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.email import send_reset_password_email

router = APIRouter()


@router.post("/login", response_model=user_schemas.Token)
def login(
        db: Session = Depends(deps.get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
):
    user = crud.user.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")

    token = crud.token.create_user_tokens(db, user.id)
    return user_schemas.Token(
        access_token=token.access_token,
        refresh_token=token.refresh_token,
        token_type="bearer",
        expires_in=(token.access_token_expires_at - int(datetime.utcnow().timestamp()))
    )


@router.post("/login/2fa", response_model=user_schemas.Token)
def login_2fa(
        db: Session = Depends(deps.get_db),
        login_data: user_schemas.TwoFactorLogin = Body(...)
):
    user = crud.user.authenticate(db, email=login_data.username, password=login_data.password)
    if not user or not user.two_factor_auth_enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials or 2FA not enabled")

    totp = pyotp.TOTP(user.two_factor_auth_secret)
    if not totp.verify(login_data.two_factor_code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid 2FA code")

    return create_token_for_user(user)


def create_token_for_user(user: models.User) -> user_schemas.Token:
    access_token = security.create_access_token(str(user.id))
    refresh_token = security.create_refresh_token(str(user.id))
    return user_schemas.Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES  # * 60
    )


@router.post("/refresh-token", response_model=user_schemas.Token)
def refresh_token(
        db: Session = Depends(deps.get_db),
        refresh_token: str = Body(..., embed=True)
):
    token = crud.token.get_by_refresh_token(db, refresh_token)
    if not token or not token.is_active or token.refresh_token_expires_at < int(datetime.utcnow().timestamp()):
        raise HTTPException(status_code=400, detail="Invalid or expired refresh token")

    crud.token.revoke_token(db, token)
    new_token = crud.token.create_user_tokens(db, token.user_id)

    return user_schemas.Token(
        access_token=new_token.access_token,
        refresh_token=new_token.refresh_token,
        token_type="bearer",
        expires_in=(new_token.access_token_expires_at - int(datetime.utcnow().timestamp()))
    )


@router.post("/logout")
def logout(
        current_user: models.User = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    crud.token.revoke_all_user_tokens(db, current_user.id)
    return {"detail": "Successfully logged out"}


@router.post("/register", response_model=user_schemas.UserSanitized)
def register_user(
        user: user_schemas.UserCreate,
        db: Session = Depends(deps.get_db)
):
    db_user = crud.user.get_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.user.create(db=db, obj_in=user)


@router.post("/reset_password", response_model=user_schemas.Message)
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


@router.post("/change_password", response_model=user_schemas.Message)
def change_user_password(
        current_password: str = Body(...),
        new_password: str = Body(...),
        current_user: models.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)
):
    if not crud.user.authenticate(db, email=current_user.email, password=current_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")

    crud.user.update(db, db_obj=current_user, obj_in={"password": new_password})
    return {"message": "Password updated successfully"}


@router.put("/me", response_model=user_schemas.UserSanitized)
def update_user_me(
        user_in: user_schemas.UserUpdate,
        current_user: models.User = Depends(deps.get_current_active_user),
        db: Session = Depends(deps.get_db)
):
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user_schemas.UserSanitized.model_validate(user)


@router.get("/me", response_model=user_schemas.UserSanitized)
def read_user_me(
        current_user: models.User = Depends(deps.get_current_active_user),
):
    return user_schemas.UserSanitized.model_validate(current_user)


@router.get("/permissions", response_model=user_schemas.AllPermissions)
def get_all_permissions(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    return {"permissions": crud.user.get_all_permissions(db)}


@router.get("/my_permissions", response_model=user_schemas.UserWithPermissions)
def get_my_permissions(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.user.get_user_with_permissions(db, current_user.id)


@router.get("/roles", response_model=user_schemas.AllRoles)
def get_all_roles(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    roles = crud.user.get_all_roles(db)
    return user_schemas.AllRoles(roles=roles)


@router.get("/", response_model=list[user_schemas.UserSanitized])
def read_users(
        filter_params: user_schemas.UserFilter = Depends(),
        skip: int = Query(0),
        limit: int = Query(100),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    users = crud.user.get_multi_with_filters(
        db,
        filter_params=filter_params,
        skip=skip,
        limit=limit
    )
    return users


@router.post("/", response_model=user_schemas.UserSanitized)
def create_user(
        user: user_schemas.UserCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    db_user = crud.user.get_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user.password = security.get_password_hash(user.password)
    return crud.user.create(db=db, obj_in=user)

@router.get("/search", response_model=list[user_schemas.UserSearchResult])
def search_users(
    query: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    users = crud.user.search(db, query=query, skip=skip, limit=limit)
    return users

@router.get("/{user_id}/permissions", response_model=user_schemas.UserWithPermissions)
def get_user_permissions(
        user_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
):
    if not crud.user.is_admin(current_user) and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    user_with_permissions = crud.user.get_user_with_permissions(db, user_id)
    if not user_with_permissions:
        raise HTTPException(status_code=404, detail="User not found")
    return user_with_permissions


@router.put("/{user_id}/permissions", response_model=user_schemas.UserWithPermissions)
def update_user_permissions(
        user_id: int,
        permission_update: user_schemas.UserPermissionUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin),
):
    return crud.user.update_user_permissions(db, user_id=user_id, permissions=permission_update.permissions)


@router.get("/{user_id}", response_model=user_schemas.UserSanitized)
def read_user(
        user_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    user = crud.user.get_user_with_permissions(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        return user_schemas.UserSanitized.model_validate(user)
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return user_schemas.UserSanitized.model_validate(user)


@router.put("/{user_id}", response_model=user_schemas.UserSanitized)
def update_user(
        user_id: int,
        user_in: user_schemas.UserUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user_schemas.UserSanitized.model_validate(updated_user)


@router.delete("/{user_id}", status_code=204)
def delete_user(
        user_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    crud.user.remove(db, id=user_id)


@router.get("/roles/{role_id}", response_model=user_schemas.Role)
def get_role(
        role_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    db_role = crud.role.get(db, id=role_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role


@router.post("/roles", response_model=user_schemas.Role)
def create_role(
        role: user_schemas.RoleCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    return crud.role.create(db=db, obj_in=role)


@router.put("/roles/{role_id}", response_model=user_schemas.Role)
def update_role(
        role_id: int,
        role_update: user_schemas.RoleUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    db_role = crud.role.get(db, id=role_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    updated_role = crud.role.update(db=db, db_obj=db_role, obj_in=role_update)
    return updated_role


@router.delete("/roles/{role_id}", status_code=204)
def delete_role(
        role_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    db_role = crud.role.get(db, id=role_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    crud.role.remove(db=db, id=role_id)
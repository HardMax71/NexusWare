# /server/app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from public_api.permissions import PermissionName, PermissionType, PermissionManager
from app import crud, models
from app.core.config import settings
from app.db.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "access_token":
            raise HTTPException(status_code=401, detail="Invalid token type")
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> models.User:
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user = crud.user.get(db, id=int(user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    token_obj = crud.token.get_by_access_token(db, token)
    if token_obj is None or not token_obj.is_active:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")

    return user


def get_current_active_user(
        current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_admin(
        current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.role.name.lower() == "admin":
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


def get_permission_manager(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_active_user)
) -> PermissionManager:
    permissions = crud.user.get_user_permissions(db, current_user.id)
    return PermissionManager(permissions)


def has_permission(name: PermissionName, action: PermissionType):
    def permission_checker(
            permission_manager: PermissionManager = Depends(get_permission_manager)
    ):
        if not permission_manager.has_permission(name, action):
            raise HTTPException(
                status_code=403,
                detail=f"Not enough permissions to {action.value} {name.value}"
            )
        return True

    return permission_checker

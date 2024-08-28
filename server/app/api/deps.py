# /server/app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from public_api.permissions import PermissionName, PermissionType
from public_api.permissions.permission_manager import PermissionManager
from public_api.shared_schemas import user as user_schemas
from server.app import crud, models
from server.app.core.config import settings
from server.app.db.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")


def get_current_user(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
) -> models.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = user_schemas.TokenData(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    user = crud.user.get_by_username(db, username=token_data.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_active_user(
        current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_admin(
        current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_admin(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
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

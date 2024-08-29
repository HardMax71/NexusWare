# /server/app/crud/user.py
import time
from datetime import timedelta, datetime

from sqlalchemy.orm import Session, joinedload

from public_api.shared_schemas import user as user_schemas
from server.app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from server.app.models import User, Permission, Role, RolePermission, Token
from .base import CRUDBase
from ..core.config import settings


class CRUDUser(CRUDBase[User, user_schemas.UserCreate, user_schemas.UserUpdate]):
    def get_by_email(self, db: Session, email: str) -> user_schemas.UserSanitized | None:
        user = db.query(User).filter(User.email == email).first()
        return user_schemas.UserSanitized.model_validate(user) if user else None

    def get_multi_with_filters(
            self,
            db: Session,
            filter_params: user_schemas.UserFilter,
            skip: int = 0,
            limit: int = 100
    ) -> list[user_schemas.UserSanitized]:
        query = db.query(User)

        if filter_params.role_id is not None:
            query = query.filter(User.role_id == filter_params.role_id)
        if filter_params.username is not None:
            query = query.filter(User.username.ilike(f"%{filter_params.username}%"))
        if filter_params.email is not None:
            query = query.filter(User.email.ilike(f"%{filter_params.email}%"))
        if filter_params.is_active is not None:
            query = query.filter(User.is_active == filter_params.is_active)

        users = query.offset(skip).limit(limit).all()
        return [user_schemas.UserSanitized.model_validate(user) for user in users]

    def get_by_username(self, db: Session, username: str) -> user_schemas.UserSanitized | None:
        user = db.query(User).filter(User.username == username).first()
        return user_schemas.UserSanitized.model_validate(user) if user else None

    def update(self, db: Session, *, db_obj: User, obj_in: user_schemas.UserUpdate) -> user_schemas.UserSanitized:
        update_data = obj_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> user_schemas.UserSanitized | None:
        user = db.query(User).options(
            joinedload(User.role).joinedload(Role.role_permissions).joinedload(RolePermission.permission)
        ).filter(User.email == email).first()
        if not user or not verify_password(password, user.password):
            return None

        # Update last login timestamp
        user.last_login = int(time.time())
        db.add(user)
        db.commit()
        db.refresh(user)

        return user_schemas.UserSanitized.model_validate(user)

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_admin(self, user: User) -> bool:
        return user.role.name.lower() == "admin"

    def change_role(self, db: Session, *, user_id: int, new_role_id: int) -> user_schemas.UserSanitized | None:
        user = self.get(db, id=user_id)
        if user:
            user.role_id = new_role_id
            db.commit()
            db.refresh(user)
        return user_schemas.UserSanitized.model_validate(user) if user else None

    def set_reset_password_token(self, db: Session, *, user: User, token: str) -> user_schemas.UserSanitized:
        user.password_reset_token = token
        user.password_reset_expiration = int((datetime.utcnow() + timedelta(hours=1)).timestamp())
        db.add(user)
        db.commit()
        db.refresh(user)
        return user_schemas.UserSanitized.model_validate(user)

    def get_user_with_permissions(self, db: Session, user_id: int) -> user_schemas.UserWithPermissions | None:
        user = db.query(User).options(
            joinedload(User.role).joinedload(Role.role_permissions).joinedload(RolePermission.permission)
        ).filter(User.id == user_id).first()

        if not user:
            return None

        user_permissions = [
            user_schemas.UserPermission(
                id=role_permission.permission.id,
                name=role_permission.permission.name,
                can_read=role_permission.can_read,
                can_write=role_permission.can_write,
                can_edit=role_permission.can_edit,
                can_delete=role_permission.can_delete
            )
            for role_permission in user.role.role_permissions
        ]

        return user_schemas.UserWithPermissions(
            **user_schemas.UserSanitized.model_validate(user).model_dump(),
            permissions=user_permissions
        )

    def update_user_permissions(
            self,
            db: Session,
            *,
            user_id: int,
            permissions: list[user_schemas.RolePermissionCreate]
    ) -> user_schemas.UserWithPermissions:
        user = self.get(db, id=user_id)
        if not user:
            raise ValueError("User not found")

        # Clear existing role permissions
        db.query(RolePermission).filter(RolePermission.role_id == user.role_id).delete()

        # Add new role permissions
        for perm in permissions:
            permission = db.query(Permission).filter(Permission.id == perm.permission_id).first()
            if permission:
                role_permission = RolePermission(
                    role_id=user.role_id,
                    permission_id=permission.id,
                    can_read=perm.can_read,
                    can_write=perm.can_write,
                    can_edit=perm.can_edit,
                    can_delete=perm.can_delete
                )
                db.add(role_permission)

        db.commit()
        db.refresh(user)
        return self.get_user_with_permissions(db, user_id)

    def get_user_permissions(self, db: Session, user_id: int) -> list[Permission]:
        user = self.get_user_with_permissions(db, user_id)
        return user.permissions if user else []

    def check_permission(self, db: Session, user_id: int, permission_name: str, action: str) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        role_permission = db.query(RolePermission).join(Permission).filter(
            RolePermission.role_id == user.role_id,
            Permission.name == permission_name
        ).first()

        if not role_permission:
            return False

        return getattr(role_permission, f"can_{action}", False)

    def get_all_permissions(self, db: Session) -> list[Permission]:
        return db.query(Permission).all()

    def get_all_roles(self, db: Session) -> list[Role]:
        return db.query(Role).all()

    def create_user_tokens(self, db: Session, user_id: int) -> Token:
        access_token = create_access_token(str(user_id))
        refresh_token = create_refresh_token(str(user_id))

        now = datetime.utcnow()
        token = Token(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expires_at=int((now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
            refresh_token_expires_at=int((now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()),
            is_active=True
        )
        db.add(token)
        db.commit()
        db.refresh(token)
        return token

    def revoke_user_tokens(self, db: Session, user_id: int):
        db.query(Token).filter(Token.user_id == user_id, Token.is_active == True).update({"is_active": False})
        db.commit()

    def get_user_by_token(self, db: Session, access_token: str) -> User | None:
        token = db.query(Token).filter(Token.access_token == access_token, Token.is_active == True).first()
        if token and token.access_token_expires_at > int(time.time()):
            return token.user
        return None

    def refresh_tokens(self, db: Session, refresh_token: str) -> Token | None:
        token = db.query(Token).filter(Token.refresh_token == refresh_token, Token.is_active == True).first()
        if not token or token.refresh_token_expires_at < int(time.time()):
            return None

        # Revoke the old token
        token.is_active = False
        db.add(token)

        # Create new tokens
        new_token = self.create_user_tokens(db, token.user_id)
        db.commit()

        return new_token

    def get_active_token(self, db: Session, jti: str) -> Token | None:
        return db.query(Token).filter(Token.access_token.contains(jti), Token.is_active == True).first()


user = CRUDUser(User)

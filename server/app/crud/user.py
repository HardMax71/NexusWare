# /server/app/crud/user.py
import time
from datetime import timedelta, datetime

from sqlalchemy.orm import Session, joinedload

from public_api.shared_schemas import user as user_schemas
from server.app.core.security import get_password_hash, verify_password
from server.app.models import User, Permission, Role
from .base import CRUDBase


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
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> user_schemas.UserSanitized | None:
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password):
            return None

        # updating last login timestamp
        current_time = int(time.time())
        user.last_login = current_time
        db.add(user)
        db.commit()
        db.refresh(user)

        return user_schemas.UserSanitized.model_validate(user)

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_admin(self, user: User) -> bool:
        return user.role.role_name.lower() == user_schemas.RoleName.ADMIN.value

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
            joinedload(User.role).joinedload(Role.permissions)
        ).filter(User.id == user_id).first()
        return user_schemas.UserWithPermissions.model_validate(user) if user else None

    def update_user_permissions(self,
                                db: Session,
                                *,
                                user_id: int,
                                permission_ids: list[int]) -> user_schemas.UserWithPermissions:
        user = self.get(db, id=user_id)
        if not user:
            raise ValueError("User not found")

        permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
        user.permissions = permissions
        db.add(user)
        db.commit()
        db.refresh(user)
        return user_schemas.UserWithPermissions.model_validate(user)

    def get_user_permissions(self, db: Session, user_id: int) -> list[Permission]:
        user = self.get_user_with_permissions(db, user_id)
        return user.permissions if user else []

    def check_permission(self, db: Session, user_id: int, name: str, action: str) -> bool:
        user_permissions = self.get_user_permissions(db, user_id)
        for perm in user_permissions:
            if perm.permission_name == name:
                if action == 'read' and perm.can_read:
                    return True
                if action == 'write' and perm.can_write:
                    return True
                if action == 'delete' and perm.can_delete:
                    return True
        return False

    def get_all_permissions(self, db: Session) -> list[Permission]:
        return db.query(Permission).all()

    def get_all_roles(self, db: Session) -> list[Role]:
        return db.query(Role).all()


user = CRUDUser(User)

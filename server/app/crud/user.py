from datetime import timedelta, datetime
from typing import Optional, List, Any, Dict, Union

from sqlalchemy.orm import Session, joinedload

from public_api.shared_schemas import UserCreate, UserUpdate, UserFilter
from server.app.core.security import get_password_hash, verify_password
from server.app.models import User, Permission, Role
from .base import CRUDBase


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):

    def get_multi_with_filters(
            self,
            db: Session,
            filter_params: UserFilter,
            skip: int = 0,
            limit: int = 100
    ) -> List[User]:
        query = db.query(User)

        if filter_params.role_id is not None:
            query = query.filter(User.role_id == filter_params.role_id)
        if filter_params.username is not None:
            query = query.filter(User.username.ilike(f"%{filter_params.username}%"))
        if filter_params.email is not None:
            query = query.filter(User.email.ilike(f"%{filter_params.email}%"))
        if filter_params.is_active is not None:
            query = query.filter(User.is_active == filter_params.is_active)

        return query.offset(skip).limit(limit).all()

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def update(self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["password_hash"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_admin(self, user: User) -> bool:
        return user.role.role_name.lower() == "admin"


    def change_role(self, db: Session, *, user_id: int, new_role_id: int) -> Optional[User]:
        user = self.get(db, id=user_id)
        if user:
            user.role_id = new_role_id
            db.commit()
            db.refresh(user)
        return user

    def set_reset_password_token(self, db: Session, *, user: User, token: str) -> User:
        user.password_reset_token = token
        user.password_reset_expiration = int((datetime.utcnow() + timedelta(hours=1)).timestamp())
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_user_with_permissions(self, db: Session, user_id: int) -> Optional[User]:
        return db.query(User).options(
            joinedload(User.role).joinedload(Role.permissions)
        ).filter(User.id == user_id).first()

    def update_user_permissions(self, db: Session, *, user_id: int, permission_ids: List[int]) -> User:
        user = self.get(db, id=user_id)
        if not user:
            raise ValueError("User not found")

        permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
        user.permissions = permissions
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_all_permissions(self, db: Session) -> List[Permission]:
        return db.query(Permission).all()

    def get_all_roles(self, db: Session) -> List[Role]:
        return db.query(Role).all()


user = CRUDUser(User)

# /server/app/crud/user.py
from datetime import datetime, timedelta
from typing import Optional, List, Any, Dict, Union

from sqlalchemy.orm import Session

from server.app.core.security import get_password_hash, verify_password
from server.app.models import User
from server.app.schemas import UserCreate, UserUpdate, User as UserSchema
from .base import CRUDBase


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[UserSchema]:
        user = db.query(User).filter(User.email == email).first()
        return UserSchema.model_validate(user) if user else None

    def get_by_username(self, db: Session, *, username: str) -> Optional[UserSchema]:
        user = db.query(User).filter(User.username == username).first()
        return UserSchema.model_validate(user) if user else None

    def get_by_id(self, db: Session, *, user_id: int) -> Optional[UserSchema]:
        user = db.query(User).filter(User.user_id == user_id).first()
        return UserSchema.model_validate(user) if user else None

    def create(self, db: Session, *, obj_in: UserCreate) -> UserSchema:
        db_obj = User(
            email=obj_in.email,
            password_hash=get_password_hash(obj_in.password_hash),
            username=obj_in.username,
            role_id=obj_in.role_id,
            is_active=obj_in.is_active
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return UserSchema.model_validate(db_obj)

    def update(self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]) -> UserSchema:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["password_hash"] = hashed_password
        updated_user = super().update(db, db_obj=db_obj, obj_in=update_data)
        return UserSchema.model_validate(updated_user)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[UserSchema]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def is_active(self, user: UserSchema) -> bool:
        return user.is_active

    def is_superuser(self, user: UserSchema) -> bool:
        return user.role.role_name == "superuser"

    def get_multi_by_role(self, db: Session, *, role_id: int, skip: int = 0, limit: int = 100) -> List[UserSchema]:
        users = db.query(User).filter(User.role_id == role_id).offset(skip).limit(limit).all()
        return [UserSchema.model_validate(user) for user in users]

    def change_role(self, db: Session, *, user_id: int, new_role_id: int) -> Optional[UserSchema]:
        user = self.get(db, id=user_id)
        if user:
            user.role_id = new_role_id
            db.commit()
            db.refresh(user)
        return UserSchema.model_validate(user) if user else None

    def set_reset_password_token(self, db: Session, *, user: UserSchema, token: str) -> UserSchema:
        user.password_reset_token = token
        user.password_reset_expiration = datetime.utcnow() + timedelta(hours=1)
        db.add(user)
        db.commit()
        db.refresh(user)
        return UserSchema.model_validate(user)


user = CRUDUser(User)

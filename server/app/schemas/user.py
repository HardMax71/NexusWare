# /server/app/schemas/user.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class PermissionBase(BaseModel):
    permission_name: str


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    permission_name: Optional[str] = None


class Permission(PermissionBase):
    permission_id: int

    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    role_name: str


class RoleCreate(RoleBase):
    permissions: list[int]


class RoleUpdate(BaseModel):
    role_name: Optional[str] = None
    permissions: Optional[list[int]] = None


class Role(RoleBase):
    role_id: int
    permissions: list[Permission] = []

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True
    role_id: int


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    role_id: Optional[int] = None
    password: Optional[str] = None


class User(UserBase):
    user_id: int
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserInDB(User):
    password_hash: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class Message(BaseModel):
    message: str

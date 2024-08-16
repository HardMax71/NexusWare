# /server/app/shared_schemas/user.py
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, EmailStr


class RoleName(str, Enum):
    admin = "admin"
    manager = "manager"
    user = "user"


class PermissionBase(BaseModel):
    permission_name: str
    can_read: bool = False
    can_write: bool = False
    can_delete: bool = False


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(PermissionBase):
    permission_name: Optional[str] = None


class Permission(PermissionBase):
    id: int

    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    role_name: RoleName


class RoleCreate(RoleBase):
    permissions: List[int]


class RoleUpdate(BaseModel):
    role_name: Optional[RoleName] = None
    permissions: Optional[List[int]] = None


class Role(RoleBase):
    id: int
    permissions: List[Permission] = []

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


class UserSanitizedWithRole(UserBase):
    id: int
    created_at: int
    last_login: Optional[int] = None
    role: Role

    class Config:
        from_attributes = True


class User(UserBase):
    id: int
    created_at: int
    last_login: Optional[int] = None
    password_hash: str
    password_reset_token: Optional[str] = None
    password_reset_expiration: Optional[int] = None

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


class RolePermission(BaseModel):
    role_id: int
    permission_id: int

    class Config:
        from_attributes = True


class UserWithRole(User):
    role: Role


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class UserFilter(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    role_id: Optional[int] = None


class UserActivity(BaseModel):
    user_id: int
    username: str
    last_login: Optional[int]
    total_logins: int
    total_actions: int


class RoleWithUsers(Role):
    users: List[User] = []


class UserPermissions(BaseModel):
    user_id: int
    username: str
    permissions: List[Permission]


class BulkUserCreate(BaseModel):
    users: List[UserCreate]


class BulkUserCreateResult(BaseModel):
    success_count: int
    failure_count: int
    errors: List[str]


class UserPermissionUpdate(BaseModel):
    user_id: int
    permissions: List[int]


class UserWithPermissions(UserSanitizedWithRole):
    permissions: List[Permission]

    class Config:
        from_attributes = True


class AllRoles(BaseModel):
    roles: List[Role]


class AllPermissions(BaseModel):
    permissions: List[Permission]

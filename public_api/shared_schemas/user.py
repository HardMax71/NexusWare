# /server/app/shared_schemas/user.py

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class PermissionBase(BaseModel):
    name: str


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(PermissionBase):
    name: str | None = None


class Permission(PermissionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RolePermissionBase(BaseModel):
    can_read: bool = False
    can_write: bool = False
    can_edit: bool = False
    can_delete: bool = False



class RolePermissionCreate(RolePermissionBase):
    permission_id: int


class RolePermissionUpdate(RolePermissionBase):
    pass


class RolePermission(RolePermissionBase):
    id: int
    role_id: int
    permission_id: int
    permission: Permission

    model_config = ConfigDict(from_attributes=True)



class RoleBase(BaseModel):
    name: str


class RoleCreate(RoleBase):
    permissions: list[RolePermissionCreate]


class RoleUpdate(RoleBase):
    name: str | None = None
    permissions: list[RolePermissionCreate] | None = None


class Role(RoleBase):
    id: int
    permissions: list[RolePermission] = []

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True
    role_id: int
    two_factor_auth_enabled: bool = False

    model_config = ConfigDict(from_attributes=True, extra='ignore')


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    two_factor_auth_secret: str | None = None


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None
    role_id: int | None = None
    password: str | None = Field(None, min_length=8)
    two_factor_auth_enabled: bool | None = None
    two_factor_auth_secret: str | None = None


class UserSanitized(UserBase):
    id: int
    created_at: int
    last_login: int | None = None
    role: Role

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserSanitized):
    password: str
    password_reset_token: str | None = None
    password_reset_expiration: int | None = None
    two_factor_auth_secret: str | None = None


class UserPermission(BaseModel):
    id: int
    name: str
    can_read: bool
    can_write: bool
    can_edit: bool
    can_delete: bool


class UserWithPermissions(UserSanitized):
    permissions: list[UserPermission]


class TwoFactorLogin(BaseModel):
    username: str
    password: str
    two_factor_code: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    username: str | None = None


class Message(BaseModel):
    message: str


class UserFilter(BaseModel):
    username: str | None = None
    email: str | None = None
    is_active: bool | None = None
    role_id: int | None = None


class UserPermissionUpdate(BaseModel):
    permissions: list[RolePermissionCreate]


class AllRoles(BaseModel):
    roles: list[Role]


class AllPermissions(BaseModel):
    permissions: list[Permission]


class RefreshTokenRequest(BaseModel):
    refresh_token: str

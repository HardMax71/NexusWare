from public_api.shared_schemas import (
    UserCreate, UserUpdate, UserSanitized, Token,
    Message, UserFilter, AllPermissions, AllRoles, UserWithPermissions,
    UserPermissionUpdate, TwoFactorLogin
)
from .client import APIClient
from ..permission_manager import PermissionManager
from ..shared_schemas.user import UserPermission, RoleCreate, Role, RoleUpdate, PermissionCreate, Permission, \
    PermissionUpdate


class UsersAPI:
    def __init__(self, client: APIClient):
        self.client = client
        self._permission_manager = None

    def login(self, username: str, password: str) -> Token:
        data = {
            "username": username,
            "password": password,
        }
        response = self.client.post("/users/login", data=data)
        token = Token.model_validate(response)
        self.client.set_tokens(token.access_token, token.refresh_token, token.expires_in)
        return token

    def login_2fa(self, username: str, password: str, two_factor_code: str) -> Token:
        data = TwoFactorLogin(
            username=username,
            password=password,
            two_factor_code=two_factor_code
        )
        response = self.client.post("/users/login/2fa", json=data.model_dump())
        token = Token.model_validate(response)
        self.client.set_tokens(token.access_token, token.refresh_token, token.expires_in)
        return token

    def register(self, user: UserCreate) -> UserSanitized:
        response = self.client.post("/users/register", json=user.model_dump())
        return UserSanitized.model_validate(response)

    def reset_password(self, email: str) -> Message:
        response = self.client.post("/users/reset_password", json={"email": email})
        return Message.model_validate(response)

    def change_password(self, current_password: str, new_password: str) -> Message:
        data = {"current_password": current_password, "new_password": new_password}
        response = self.client.post("/users/change_password", json=data)
        return Message.model_validate(response)

    def refresh_token(self) -> Token:
        refresh_token = self.client.refresh_token
        if not refresh_token:
            raise ValueError("No refresh token available")

        response = self.client.post("/users/refresh-token", json={
            "refresh_token": refresh_token
        })
        token = Token.model_validate(response)
        self.client.set_tokens(token.access_token, token.refresh_token, token.expires_in)
        return token

    def update_current_user(self, user_update: UserUpdate) -> UserSanitized:
        response = self.client.put("/users/me", json=user_update.model_dump(exclude_unset=True))
        return UserSanitized.model_validate(response)

    def get_current_user(self) -> UserSanitized:
        response = self.client.get("/users/me")
        return UserSanitized.model_validate(response)

    def get_all_permissions(self) -> AllPermissions:
        response = self.client.get("/users/permissions")
        return AllPermissions.model_validate(response)

    def get_my_permissions(self) -> list[UserPermission]:
        response = self.client.get("/users/my_permissions")
        user_with_permissions = UserWithPermissions.model_validate(response)
        return user_with_permissions.permissions

    def get_all_roles(self) -> AllRoles:
        response = self.client.get("/users/roles")
        return AllRoles.model_validate(response)

    def get_users(self, filter_params: UserFilter | None = None,
                  skip: int = 0, limit: int = 100) -> list[UserSanitized]:
        params = {"skip": skip, "limit": limit}
        if filter_params:
            params.update(filter_params.model_dump(exclude_unset=True))
        response = self.client.get("/users/", params=params)
        return [UserSanitized.model_validate(item) for item in response]

    def create_user(self, user: UserCreate) -> UserSanitized:
        response = self.client.post("/users/", json=user.model_dump())
        return UserSanitized.model_validate(response)

    def get_user_permissions(self, user_id: int) -> UserWithPermissions:
        response = self.client.get(f"/users/{user_id}/permissions")
        return UserWithPermissions.model_validate(response)

    def update_user_permissions(self, user_id: int, permission_update: UserPermissionUpdate) -> UserWithPermissions:
        response = self.client.put(f"/users/{user_id}/permissions", json=permission_update.model_dump())
        return UserWithPermissions.model_validate(response)

    def get_user(self, user_id: int) -> UserSanitized:
        response = self.client.get(f"/users/{user_id}")
        return UserSanitized.model_validate(response)

    def update_user(self, user_id: int, user_update: UserUpdate) -> UserSanitized:
        response = self.client.put(f"/users/{user_id}", json=user_update.model_dump(exclude_unset=True))
        return UserSanitized.model_validate(response)

    def delete_user(self, user_id: int) -> None:
        self.client.delete(f"/users/{user_id}")

    def get_current_user_permissions(self) -> PermissionManager:
        if not self._permission_manager:
            permissions = self.get_my_permissions()
            self._permission_manager = PermissionManager(permissions)
        return self._permission_manager

    def has_permission(self, permission_name: str, action: str) -> bool:
        return self.get_current_user_permissions().has_permission(permission_name, action)

    def clear_permissions_cache(self):
        self._permission_manager = None

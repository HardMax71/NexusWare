from typing import List, Optional

from public_api.shared_schemas import (
    UserCreate, UserUpdate, User, UserSanitizedWithRole, Token,
    Message, PasswordResetConfirm, UserFilter,
    UserActivity, RoleWithUsers, BulkUserCreate,
    BulkUserCreateResult, AllPermissions, AllRoles, UserWithPermissions, UserPermissionUpdate
)
from .client import APIClient


class UsersAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def login(self, username: str, password: str) -> Token:
        data = {
            "grant_type": "password",
            "username": username,
            "password": password,
        }
        headers = {"content-type": "application/x-www-form-urlencoded"}

        response = self.client.post("/users/login", data=data, headers=headers)
        access_token = response.get("access_token")

        if access_token:
            self.client.set_token(access_token)

        return Token.model_validate(response)

    def register(self, user: UserCreate) -> User:
        response = self.client.post("/users/register", json=user.model_dump(mode="json"))
        return User.model_validate(response)

    def reset_password(self, email: str) -> Message:
        response = self.client.post("/users/reset_password", json={"email": email})
        return Message.model_validate(response)

    def get_current_user(self) -> UserSanitizedWithRole:
        response = self.client.get("/users/me")
        return UserSanitizedWithRole.model_validate(response)

    def update_current_user(self, user_update: UserUpdate) -> User:
        response = self.client.put("/users/me", json=user_update.model_dump(mode="json", exclude_unset=True))
        return User.model_validate(response)

    def get_users(self, filter_params: Optional[UserFilter] = None, skip: int = 0, limit: int = 100) -> List[UserSanitizedWithRole]:
        params = {"skip": skip, "limit": limit}
        if filter_params:
            params.update(filter_params.model_dump(exclude_unset=True))
        response = self.client.get("/users/", params=params)
        return [UserSanitizedWithRole.model_validate(item) for item in response]

    def create_user(self, user: UserCreate) -> UserSanitizedWithRole:
        response = self.client.post("/users/", json=user.model_dump(mode="json"))
        return UserSanitizedWithRole.model_validate(response)

    def get_user(self, user_id: int) -> UserSanitizedWithRole:
        response = self.client.get(f"/users/{user_id}")
        return UserSanitizedWithRole.model_validate(response)

    def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        response = self.client.put(f"/users/{user_id}", json=user_update.model_dump(mode="json", exclude_unset=True))
        return User.model_validate(response)

    def delete_user(self, user_id: int) -> User:
        response = self.client.delete(f"/users/{user_id}")
        return User.model_validate(response)

    def confirm_password_reset(self, token: str, new_password: str) -> Message:
        data = PasswordResetConfirm(token=token, new_password=new_password)
        response = self.client.post("/users/reset_password_confirm", json=data.model_dump(mode="json"))
        return Message.model_validate(response)

    def get_filtered_users(self, user_filter: UserFilter) -> List[UserSanitizedWithRole]:
        response = self.client.get("/users/filter", params=user_filter.model_dump(mode="json", exclude_unset=True))
        return [UserSanitizedWithRole.model_validate(item) for item in response]

    def get_user_activity(self) -> List[UserActivity]:
        response = self.client.get("/users/activity")
        return [UserActivity.model_validate(item) for item in response]

    def get_role_with_users(self, role_id: int) -> RoleWithUsers:
        response = self.client.get(f"/users/role/{role_id}")
        return RoleWithUsers.model_validate(response)

    def bulk_create_users(self, users: BulkUserCreate) -> BulkUserCreateResult:
        response = self.client.post("/users/bulk", json=users.model_dump(mode="json"))
        return BulkUserCreateResult.model_validate(response)

    def get_all_permissions(self) -> AllPermissions:
        response = self.client.get("/users/permissions")
        return AllPermissions.model_validate(response)

    def get_all_roles(self) -> AllRoles:
        response = self.client.get("/users/roles")
        return AllRoles.model_validate(response)

    def get_user_permissions(self, user_id: int) -> UserWithPermissions:
        response = self.client.get(f"/users/{user_id}/permissions")
        return UserWithPermissions.model_validate(response)

    def update_user_permissions(self, user_id: int, permissions: List[int]) -> UserWithPermissions:
        data = UserPermissionUpdate(user_id=user_id, permissions=permissions)
        response = self.client.put(f"/users/{user_id}/permissions", json=data.model_dump())
        return UserWithPermissions.model_validate(response)

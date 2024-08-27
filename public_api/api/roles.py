# /public_api/api/roles_api.py

from typing import List

from public_api.shared_schemas import (
    Role, RoleCreate, RoleUpdate, Permission, PermissionCreate, PermissionUpdate, AllPermissions
)
from .client import APIClient


class RolesAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def get_all_permissions(self) -> List[Permission]:
        response = self.client.get("/roles/permissions")
        all_permissions = AllPermissions.model_validate(response)
        return all_permissions.permissions

    def create_permission(self, permission: PermissionCreate) -> Permission:
        response = self.client.post("/roles/permissions", json=permission.model_dump())
        return Permission.model_validate(response)

    def update_permission(self, permission_id: int, permission_update: PermissionUpdate) -> Permission:
        response = self.client.put(f"/roles/permissions/{permission_id}", json=permission_update.model_dump())
        return Permission.model_validate(response)

    def delete_permission(self, permission_id: int) -> None:
        self.client.delete(f"/roles/permissions/{permission_id}")

    def get_all_roles(self) -> List[Role]:
        response = self.client.get("/roles")
        return [Role.model_validate(role) for role in response]

    def create_role(self, role: RoleCreate) -> Role:
        response = self.client.post("/roles", json=role.model_dump())
        return Role.model_validate(response)

    def get_role(self, role_id: int) -> Role:
        response = self.client.get(f"/roles/{role_id}")
        return Role.model_validate(response)

    def update_role(self, role_id: int, role_update: RoleUpdate) -> Role:
        response = self.client.put(f"/roles/{role_id}", json=role_update.model_dump())
        return Role.model_validate(response)

    def delete_role(self, role_id: int) -> None:
        self.client.delete(f"/roles/{role_id}")

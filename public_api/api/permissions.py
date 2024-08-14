from typing import List

from public_api.shared_schemas import PermissionCreate, PermissionUpdate, Permission
from .client import APIClient


class PermissionsAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_permission(self, permission_data: PermissionCreate) -> Permission:
        response = self.client.post("/permissions/", json=permission_data.model_dump(mode="json"))
        return Permission.model_validate(response)

    def get_permissions(self, skip: int = 0, limit: int = 100) -> List[Permission]:
        response = self.client.get("/permissions/", params={"skip": skip, "limit": limit})
        return [Permission.model_validate(item) for item in response]

    def get_permission(self, permission_id: int) -> Permission:
        response = self.client.get(f"/permissions/{permission_id}")
        return Permission.model_validate(response)

    def update_permission(self, permission_id: int, permission_data: PermissionUpdate) -> Permission:
        response = self.client.put(f"/permissions/{permission_id}",
                                   json=permission_data.model_dump(mode="json", exclude_unset=True))
        return Permission.model_validate(response)

    def delete_permission(self, permission_id: int) -> Permission:
        response = self.client.delete(f"/permissions/{permission_id}")
        return Permission.model_validate(response)

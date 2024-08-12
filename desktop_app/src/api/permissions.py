from .client import APIClient


class PermissionsAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_permission(self, permission_data: dict):
        return self.client.post("/permissions/", json=permission_data)

    def get_permissions(self, skip: int = 0, limit: int = 100):
        return self.client.get("/permissions/", params={"skip": skip, "limit": limit})

    def get_permission(self, permission_id: int):
        return self.client.get(f"/permissions/{permission_id}")

    def update_permission(self, permission_id: int, permission_data: dict):
        return self.client.put(f"/permissions/{permission_id}", json=permission_data)

    def delete_permission(self, permission_id: int):
        return self.client.delete(f"/permissions/{permission_id}")

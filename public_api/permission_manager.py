from typing import List
from public_api.shared_schemas.user import Permission


class PermissionManager:
    def __init__(self, permissions: List[Permission]):
        self.permissions = {p.permission_name: p for p in permissions}

    def has_permission(self, permission_name: str, action: str) -> bool:
        if permission_name in self.permissions:
            permission = self.permissions[permission_name]
            if action == 'read' and permission.can_read:
                return True
            if action == 'write' and permission.can_write:
                return True
            if action == 'delete' and permission.can_delete:
                return True
        return False

    def has_read_permission(self, permission_name: str) -> bool:
        return self.has_permission(permission_name, 'read')

    def has_write_permission(self, permission_name: str) -> bool:
        return self.has_permission(permission_name, 'write')

    def has_delete_permission(self, permission_name: str) -> bool:
        return self.has_permission(permission_name, 'delete')
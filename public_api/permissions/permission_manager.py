from typing import List

from public_api.permissions.permission_enums import PermissionType, PermissionName
from public_api.shared_schemas import UserPermission

class PermissionManager:
    def __init__(self, permissions: List[UserPermission]):
        # enum values are with "_", so we need to replace " " with "_"
        # cause in DB we have " " instead of "_"
        self.permissions = {PermissionName[p.name.replace(" ", "_").upper()]: p for p in permissions}

    def has_permission(self, tab: PermissionName, action: PermissionType) -> bool:
        if tab in self.permissions:
            permission = self.permissions[tab]
            if action == PermissionType.READ and permission.can_read:
                return True
            if action == PermissionType.WRITE and permission.can_write:
                return True
            if action == PermissionType.EDIT and permission.can_edit:
                return True
            if action == PermissionType.DELETE and permission.can_delete:
                return True
        return False

    def has_read_permission(self, permission: PermissionName) -> bool:
        return self.has_permission(permission, PermissionType.READ)

    def has_write_permission(self, permission: PermissionName) -> bool:
        return self.has_permission(permission, PermissionType.WRITE)

    def has_edit_permission(self, permission: PermissionName) -> bool:
        return self.has_permission(permission, PermissionType.EDIT)

    def has_delete_permission(self, permission: PermissionName) -> bool:
        return self.has_permission(permission, PermissionType.DELETE)

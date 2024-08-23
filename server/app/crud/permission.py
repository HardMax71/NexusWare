# /server/app/crud/permission.py

from sqlalchemy.orm import Session

from public_api.shared_schemas import PermissionCreate, PermissionUpdate, \
    Permission as PermissionSchema
from server.app.models import Permission
from .base import CRUDBase


class CRUDPermission(CRUDBase[Permission, PermissionCreate, PermissionUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> PermissionSchema | None:
        current_permission = db.query(Permission).filter(Permission.permission_name == name).first()
        return PermissionSchema.model_validate(current_permission) if current_permission else None


permission = CRUDPermission(Permission)

# /server/app/crud/permission.py
from typing import Optional

from sqlalchemy.orm import Session

from server.app.models import Permission
from public_api.shared_schemas import PermissionCreate, PermissionUpdate, \
    Permission as PermissionSchema
from .base import CRUDBase


class CRUDPermission(CRUDBase[Permission, PermissionCreate, PermissionUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[PermissionSchema]:
        current_permission = db.query(Permission).filter(Permission.permission_name == name).first()
        return PermissionSchema.model_validate(current_permission) if current_permission else None


permission = CRUDPermission(Permission)

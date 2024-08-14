# /server/app/crud/role.py
from typing import Optional, Any, Dict, Union

from sqlalchemy.orm import Session

from public_api.shared_schemas import RoleCreate, RoleUpdate, Role as RoleSchema
from server.app.models import Role, RolePermission
from .base import CRUDBase


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    def create(self, db: Session, *, obj_in: RoleCreate) -> RoleSchema:
        db_obj = Role(role_name=obj_in.role_name)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        for permission_id in obj_in.permissions:
            db.add(RolePermission(role_id=db_obj.role_id, permission_id=permission_id))
        db.commit()

        return RoleSchema.model_validate(db_obj)

    def update(self, db: Session, *, db_obj: Role, obj_in: Union[RoleUpdate, Dict[str, Any]]) -> RoleSchema:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if "permissions" in update_data:
            db.query(RolePermission).filter(RolePermission.role_id == db_obj.role_id).delete()
            for permission_id in update_data["permissions"]:
                db.add(RolePermission(role_id=db_obj.role_id, permission_id=permission_id))
            del update_data["permissions"]

        updated_role = super().update(db, db_obj=db_obj, obj_in=update_data)
        return RoleSchema.model_validate(updated_role)

    def get_by_name(self, db: Session, *, name: str) -> Optional[RoleSchema]:
        current_role = db.query(Role).filter(Role.role_name == name).first()
        return RoleSchema.model_validate(current_role) if current_role else None


role = CRUDRole(Role)

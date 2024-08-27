from sqlalchemy.orm import Session

from public_api.shared_schemas import RoleCreate, RoleUpdate
from server.app.models.user import Role as RoleModel, RolePermission as RolePermissionModel
from .base import CRUDBase


class CRUDRole(CRUDBase[RoleModel, RoleCreate, RoleUpdate]):
    def create(self, db: Session, *, obj_in: RoleCreate) -> RoleModel:
        db_obj = RoleModel(name=obj_in.name)
        db.add(db_obj)
        db.flush()

        for perm in obj_in.permissions:
            role_permission = RolePermissionModel(
                role_id=db_obj.id,
                permission_id=perm.permission_id,
                can_read=perm.can_read,
                can_write=perm.can_write,
                can_edit=perm.can_edit,
                can_delete=perm.can_delete
            )
            db.add(role_permission)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: RoleModel, obj_in: RoleUpdate) -> RoleModel:
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        if name := update_data.get("name"):
            db_obj.name = name

        if "permissions" in update_data:
            # Delete existing permissions
            db.query(RolePermissionModel).filter(RolePermissionModel.role_id == db_obj.id).delete(
                synchronize_session=False)
            db.flush()  # Ensure deletion is flushed before adding new permissions

            # Add new permissions
            for perm in update_data["permissions"]:
                role_permission = RolePermissionModel(
                    role_id=db_obj.id,
                    permission_id=perm["permission_id"],
                    can_read=perm["can_read"],
                    can_write=perm["can_write"],
                    can_edit=perm["can_edit"],
                    can_delete=perm["can_delete"]
                )
                db.add(role_permission)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: int) -> RoleModel | None:
        return db.query(RoleModel).filter(RoleModel.id == id).first()

    def get_by_name(self, db: Session, *, name: str) -> RoleModel | None:
        return db.query(RoleModel).filter(RoleModel.name == name).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> list[RoleModel]:
        return db.query(RoleModel).offset(skip).limit(limit).all()

    def remove(self, db: Session, *, id: int) -> RoleModel | None:
        obj = db.query(RoleModel).get(id)
        if obj:
            # Delete related role permissions first
            db.query(RolePermissionModel).filter(RolePermissionModel.role_id == id).delete(synchronize_session=False)
            db.delete(obj)
            db.commit()
        return obj


role = CRUDRole(RoleModel)

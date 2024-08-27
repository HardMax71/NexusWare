from sqlalchemy.orm import Session

from public_api.shared_schemas import RoleCreate, RoleUpdate, Role as RoleSchema, RolePermission, Permission
from server.app.models import Role as RoleModel, RolePermission as RolePermissionModel
from .base import CRUDBase


class CRUDRole(CRUDBase[RoleModel, RoleCreate, RoleUpdate]):
    def create(self, db: Session, *, obj_in: RoleCreate) -> RoleSchema:
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
        return self._to_schema(db_obj)

    def update(self, db: Session, *, db_obj: RoleModel, obj_in: RoleUpdate) -> RoleSchema:
        if obj_in.name is not None:
            db_obj.name = obj_in.name

        if obj_in.permissions is not None:
            # Delete existing permissions
            db.query(RolePermissionModel).filter(RolePermissionModel.role_id == db_obj.id).delete()

            # Add new permissions
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
        return self._to_schema(db_obj)

    def get(self, db: Session, id: int) -> RoleSchema | None:
        db_obj = db.query(RoleModel).filter(RoleModel.id == id).first()
        return self._to_schema(db_obj) if db_obj else None

    def get_by_name(self, db: Session, *, name: str) -> RoleSchema | None:
        db_obj = db.query(RoleModel).filter(RoleModel.name == name).first()
        return self._to_schema(db_obj) if db_obj else None

    def remove(self, db: Session, *, id: int) -> None:
        db_obj = db.query(RoleModel).filter(RoleModel.id == id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()

    def _to_schema(self, db_obj: RoleModel) -> RoleSchema:
        return RoleSchema(
            id=db_obj.id,
            name=db_obj.name,
            permissions=[
                RolePermission(
                    id=rp.id,
                    role_id=rp.role_id,
                    permission_id=rp.permission_id,
                    can_read=rp.can_read,
                    can_write=rp.can_write,
                    can_edit=rp.can_edit,
                    can_delete=rp.can_delete,
                    permission=Permission(id=rp.permission.id, name=rp.permission.name)
                ) for rp in db_obj.role_permissions
            ]
        )


role = CRUDRole(RoleModel)

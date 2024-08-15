# /server/app/crud/asset_maintenance.py

from sqlalchemy.orm import Session

from public_api.shared_schemas import (
    AssetMaintenance as AssetMaintenanceSchema,
    AssetMaintenanceCreate,
    AssetMaintenanceUpdate,
    AssetMaintenanceFilter
)
from server.app.models import AssetMaintenance
from .base import CRUDBase


class CRUDAssetMaintenance(CRUDBase[AssetMaintenance, AssetMaintenanceCreate, AssetMaintenanceUpdate]):
    def get_multi_with_filter(self, db: Session, *,
                              skip: int = 0, limit: int = 100,
                              filter_params: AssetMaintenanceFilter) -> list[AssetMaintenanceSchema]:
        query = db.query(self.model)
        if filter_params.asset_id:
            query = query.filter(self.model.asset_id == filter_params.asset_id)
        if filter_params.maintenance_type:
            query = query.filter(self.model.maintenance_type == filter_params.maintenance_type)
        if filter_params.scheduled_date_from:
            query = query.filter(self.model.scheduled_date >= filter_params.scheduled_date_from)
        if filter_params.scheduled_date_to:
            query = query.filter(self.model.scheduled_date <= filter_params.scheduled_date_to)
        if filter_params.completed_date_from:
            query = query.filter(self.model.completed_date >= filter_params.completed_date_from)
        if filter_params.completed_date_to:
            query = query.filter(self.model.completed_date <= filter_params.completed_date_to)
        if filter_params.performed_by:
            query = query.filter(self.model.performed_by == filter_params.performed_by)

        maintenance_records = query.offset(skip).limit(limit).all()
        return [AssetMaintenanceSchema.model_validate(record) for record in maintenance_records]

    def get_all_types(self, db: Session) -> list[str]:
        return [maintenance_type for (maintenance_type,) in db.query(self.model.maintenance_type).distinct().all()]


asset_maintenance = CRUDAssetMaintenance(AssetMaintenance)

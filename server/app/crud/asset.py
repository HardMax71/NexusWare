from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session, joinedload

from server.app.models import Asset, AssetMaintenance, Location
from public_api.shared_schemas import (
    Asset as AssetSchema,
    Location as LocationSchema,
    AssetWithMaintenance as AssetWithMaintenanceSchema,
    AssetCreate,
    AssetUpdate,
    AssetFilter
)
from .base import CRUDBase


class CRUDAsset(CRUDBase[Asset, AssetCreate, AssetUpdate]):

    def get_due_for_maintenance(self, db: Session) -> List[AssetWithMaintenanceSchema]:
        current_timestamp = int(datetime.now().timestamp())
        assets = db.query(self.model).join(AssetMaintenance).filter(
            AssetMaintenance.scheduled_date <= current_timestamp,
            AssetMaintenance.completed_date.is_(None)
        ).all()
        return [AssetWithMaintenanceSchema.model_validate(asset) for asset in assets]

    def transfer(self, db: Session, asset_id: int, new_location_id: int) -> Optional[AssetSchema]:
        current_asset = db.query(self.model).filter(self.model.id == asset_id).first()
        if current_asset:
            location = db.query(Location).filter(Location.id == new_location_id).first()
            if location:
                current_asset.location = location.name
                db.commit()
                db.refresh(current_asset)
                return AssetSchema.model_validate(current_asset)
        return None

    def get_asset_location(self, db: Session, asset_id: int) -> Optional[LocationSchema]:
        asset = db.query(self.model).filter(self.model.id == asset_id).first()
        if asset and asset.location:
            location = db.query(Location).filter(Location.name == asset.location).first()
            if location:
                return LocationSchema.model_validate(location)
        return None

    def get_with_maintenance(self, db: Session, id: int) -> Optional[AssetWithMaintenanceSchema]:
        asset = db.query(self.model).filter(self.model.id == id).options(
            joinedload(self.model.maintenance_records)
        ).first()
        if asset:
            return AssetWithMaintenanceSchema.model_validate(asset)
        return None

    def get_multi_with_filter(self, db: Session, *,
                              skip: int = 0, limit: int = 100, filter_params: AssetFilter) -> List[AssetSchema]:
        query = db.query(self.model)
        if filter_params.asset_type:
            query = query.filter(self.model.asset_type == filter_params.asset_type)
        if filter_params.status:
            query = query.filter(self.model.status == filter_params.status)
        if filter_params.purchase_date_from:
            query = query.filter(self.model.purchase_date >= filter_params.purchase_date_from)
        if filter_params.purchase_date_to:
            query = query.filter(self.model.purchase_date <= filter_params.purchase_date_to)
        if filter_params.location_id:
            query = query.filter(self.model.location_id == filter_params.location_id)

        assets = query.offset(skip).limit(limit).all()
        return [AssetSchema.model_validate(asset) for asset in assets]

    def count_with_filter(self, db: Session, *, filter_params: AssetFilter) -> int:
        query = db.query(self.model)
        if filter_params.asset_type:
            query = query.filter(self.model.asset_type == filter_params.asset_type)
        if filter_params.status:
            query = query.filter(self.model.status == filter_params.status)
        if filter_params.purchase_date_from:
            query = query.filter(self.model.purchase_date >= filter_params.purchase_date_from)
        if filter_params.purchase_date_to:
            query = query.filter(self.model.purchase_date <= filter_params.purchase_date_to)

        return query.count()

    def get_all_types(self, db: Session) -> List[str]:
        return [asset_type for (asset_type,) in db.query(self.model.asset_type).distinct().all()]

    def get_all_statuses(self, db: Session) -> List[str]:
        return [status for (status,) in db.query(self.model.status).distinct().all()]


asset = CRUDAsset(Asset)

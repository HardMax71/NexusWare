# /server/app/crud/asset.py
from datetime import date, datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from server.app.schemas import AssetCreate, AssetUpdate, AssetFilter, AssetMaintenanceCreate, AssetMaintenanceUpdate, \
    AssetMaintenanceFilter, AssetLocation, AssetMaintenance, Location, Asset
from .base import CRUDBase


class CRUDAsset(CRUDBase[Asset, AssetCreate, AssetUpdate]):
    def get_with_maintenance(self, db: Session, id: int) -> Optional[Asset]:
        return db.query(self.model).filter(self.model.asset_id == id).outerjoin(AssetMaintenance).first()

    def get_multi_with_filter(self, db: Session, *, skip: int = 0, limit: int = 100, filter_params: AssetFilter) -> \
            list[Asset]:
        query = db.query(self.model)
        if filter_params.asset_type:
            query = query.filter(self.model.asset_type == filter_params.asset_type)
        if filter_params.status:
            query = query.filter(self.model.status == filter_params.status)
        if filter_params.purchase_date_from:
            query = query.filter(self.model.purchase_date >= filter_params.purchase_date_from)
        if filter_params.purchase_date_to:
            query = query.filter(self.model.purchase_date <= filter_params.purchase_date_to)
        return query.offset(skip).limit(limit).all()

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

    def get_all_types(self, db: Session) -> list[str]:
        return db.query(self.model.asset_type).distinct().all()

    def get_all_statuses(self, db: Session) -> list[str]:
        return db.query(self.model.status).distinct().all()


class CRUDAssetMaintenance(CRUDBase[AssetMaintenance, AssetMaintenanceCreate, AssetMaintenanceUpdate]):
    def get_multi_with_filter(self, db: Session, *, skip: int = 0, limit: int = 100,
                              filter_params: AssetMaintenanceFilter) -> list[AssetMaintenance]:
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
        return query.offset(skip).limit(limit).all()

    def get_multi_by_asset(self, db: Session, *, asset_id: int, skip: int = 0, limit: int = 100) -> list[
        AssetMaintenance]:
        return db.query(self.model).filter(self.model.asset_id == asset_id).offset(skip).limit(limit).all()

    def get_all_types(self, db: Session) -> list[str]:
        return db.query(self.model.maintenance_type).distinct().all()

    def get_current_location(self, db: Session, asset_id: int) -> Optional[Location]:
        return db.query(Location).join(AssetLocation).filter(AssetLocation.asset_id == asset_id).order_by(
            AssetLocation.timestamp.desc()).first()

    def transfer(self, db: Session, asset_id: int, new_location_id: int) -> Asset:
        asset = self.get(db, id=asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")

        new_location = db.query(Location).get(new_location_id)
        if not new_location:
            raise HTTPException(status_code=404, detail="Location not found")

        asset_location = AssetLocation(asset_id=asset_id,
                                       location_id=new_location_id,
                                       timestamp=datetime.utcnow())
        db.add(asset_location)
        db.commit()
        db.refresh(asset)
        return asset

    def get_due_for_maintenance(self, db: Session) -> list[Asset]:
        today = date.today()
        return db.query(Asset).join(AssetMaintenance).filter(
            AssetMaintenance.scheduled_date <= today,
            AssetMaintenance.completed_date is None
        ).all()


asset = CRUDAsset(Asset)
asset_maintenance = CRUDAssetMaintenance(AssetMaintenance)

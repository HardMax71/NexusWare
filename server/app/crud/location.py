# /server/app/crud/location.py
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from server.app.models import (
    Location
)
from server.app.schemas import (
    LocationCreate,
    LocationUpdate, LocationWithInventory as LocationWithInventorySchema, LocationFilter
)
from .base import CRUDBase


class CRUDLocation(CRUDBase[Location, LocationCreate, LocationUpdate]):
    def get_multi_with_inventory(
            self, db: Session,
            skip: int = 0, limit: int = 100,
            filter_params: Optional[LocationFilter] = None) -> list[LocationWithInventorySchema]:
        query = db.query(Location).options(joinedload(Location.inventory_items))

        if filter_params:
            if filter_params.zone_id:
                query = query.filter(Location.zone_id == filter_params.zone_id)
            if filter_params.aisle:
                query = query.filter(Location.aisle == filter_params.aisle)
            if filter_params.rack:
                query = query.filter(Location.rack == filter_params.rack)
            if filter_params.shelf:
                query = query.filter(Location.shelf == filter_params.shelf)
            if filter_params.bin:
                query = query.filter(Location.bin == filter_params.bin)

        locations = query.offset(skip).limit(limit).all()
        return [LocationWithInventorySchema.model_validate(location) for location in locations]

    def get_with_inventory(self, db: Session, id: int) -> Optional[LocationWithInventorySchema]:
        location = db.query(Location).filter(Location.location_id == id).options(
            joinedload(Location.inventory_items)).first()
        return LocationWithInventorySchema.model_validate(location) if location else None


location = CRUDLocation(Location)

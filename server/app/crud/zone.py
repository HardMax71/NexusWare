# /server/app/crud/zone.py
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from server.app.models import (
    Zone
)
from public_api.shared_schemas import (
    ZoneCreate, ZoneUpdate, LocationFilter, ZoneWithLocations
)
from .base import CRUDBase


class CRUDZone(CRUDBase[Zone, ZoneCreate, ZoneUpdate]):
    def get_warehouse_layout(self, db: Session) -> list[ZoneWithLocations]:
        zones = db.query(Zone).options(joinedload(Zone.locations)).all()
        return [ZoneWithLocations.model_validate(zone) for zone in zones]

    def get_multi_with_locations(
            self, db: Session,
            skip: int = 0, limit: int = 100,
            filter_params: Optional[LocationFilter] = None) -> list[ZoneWithLocations]:
        query = db.query(Zone).options(joinedload(Zone.locations))

        if filter_params:
            if filter_params.name:
                query = query.filter(Zone.name.ilike(f"%{filter_params.name}%"))

        zones = query.offset(skip).limit(limit).all()
        return [ZoneWithLocations.model_validate(zone) for zone in zones]

    def get_with_locations(self, db: Session, id: int) -> Optional[ZoneWithLocations]:
        zone = db.query(Zone).filter(Zone.zone_id == id).options(joinedload(Zone.locations)).first()
        return ZoneWithLocations.model_validate(zone) if zone else None


zone = CRUDZone(Zone)

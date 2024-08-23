from sqlalchemy.orm import Session, joinedload

from public_api.shared_schemas import (
    ZoneCreate, ZoneUpdate, LocationFilter, ZoneWithLocations, WarehouseLayout
)
from server.app.models import (
    Zone
)
from .base import CRUDBase


class CRUDZone(CRUDBase[Zone, ZoneCreate, ZoneUpdate]):
    def get_warehouse_layout(self, db: Session) -> WarehouseLayout:
        zones = db.query(Zone).options(joinedload(Zone.locations)).all()
        zone_layouts = []
        for zone in zones:
            zone_layout = ZoneWithLocations.model_validate(zone)
            # Sort locations by aisle, rack, shelf, and bin
            zone_layout.locations.sort(key=lambda loc: (
                loc.aisle or '',
                loc.rack or '',
                loc.shelf or '',
                loc.bin or ''
            ))
            zone_layouts.append(zone_layout)
        return WarehouseLayout(zones=zone_layouts)

    def get_multi_with_locations(
            self, db: Session,
            skip: int = 0, limit: int = 100,
            filter_params: LocationFilter | None = None) -> list[ZoneWithLocations]:
        query = db.query(Zone).options(joinedload(Zone.locations))

        if filter_params:
            if filter_params.name:
                query = query.filter(Zone.name.ilike(f"%{filter_params.name}%"))

        zones = query.offset(skip).limit(limit).all()
        return [ZoneWithLocations.model_validate(zone) for zone in zones]

    def get_with_locations(self, db: Session, id: int) -> ZoneWithLocations | None:
        zone = db.query(Zone).filter(Zone.id == id).options(joinedload(Zone.locations)).first()
        return ZoneWithLocations.model_validate(zone) if zone else None


zone = CRUDZone(Zone)

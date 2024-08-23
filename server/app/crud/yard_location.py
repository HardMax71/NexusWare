from sqlalchemy.orm import Session, selectinload

from public_api.shared_schemas import (
    YardLocation as YardLocationSchema,
    YardLocationCreate, YardLocationUpdate,
    YardLocationFilter, YardLocationWithAppointments
)
from server.app.models import YardLocation
from .base import CRUDBase


class CRUDYardLocation(CRUDBase[YardLocation, YardLocationCreate, YardLocationUpdate]):
    def get_multi_with_filter(self, db: Session, *, skip: int = 0, limit: int = 100,
                              filter_params: YardLocationFilter) -> list[YardLocationSchema]:
        query = db.query(self.model)
        if filter_params.name:
            query = query.filter(YardLocation.name.ilike(f"%{filter_params.name}%"))
        if filter_params.type:
            query = query.filter(YardLocation.type == filter_params.type)
        if filter_params.status:
            query = query.filter(YardLocation.status == filter_params.status)
        locations = query.offset(skip).limit(limit).all()
        return [YardLocationSchema.model_validate(location) for location in locations]

    def get_with_appointments(self, db: Session, id: int) -> YardLocationWithAppointments | None:
        location = (db.query(self.model)
                    .filter(self.model.id == id)
                    .options(selectinload(YardLocation.appointments))
                    .first())
        return YardLocationWithAppointments.model_validate(location) if location else None


yard_location = CRUDYardLocation(YardLocation)

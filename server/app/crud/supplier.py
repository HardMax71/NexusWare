# /server/app/crud/supplier.py

from sqlalchemy.orm import Session

from server.app.models import Supplier
from server.app.schemas import (
    Supplier as SupplierSchema,
    SupplierCreate, SupplierUpdate,
    SupplierFilter
)
from .base import CRUDBase


class CRUDSupplier(CRUDBase[Supplier, SupplierCreate, SupplierUpdate]):
    def get_multi_with_filter(self, db: Session, *,
                              skip: int = 0, limit: int = 100,
                              filter_params: SupplierFilter) -> list[SupplierSchema]:
        query = db.query(self.model)
        if filter_params.name:
            query = query.filter(Supplier.name.ilike(f"%{filter_params.name}%"))
        if filter_params.contact_person:
            query = query.filter(Supplier.contact_person.ilike(f"%{filter_params.contact_person}%"))
        suppliers = query.offset(skip).limit(limit).all()
        return [SupplierSchema.model_validate(supplier) for supplier in suppliers]


supplier = CRUDSupplier(Supplier)

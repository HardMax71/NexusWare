# /server/app/crud/customer.py

from sqlalchemy.orm import Session

from server.app.models import Customer
from public_api.shared_schemas import (
    Customer as CustomerSchema,
    CustomerCreate, CustomerUpdate,
    CustomerFilter
)
from .base import CRUDBase


class CRUDCustomer(CRUDBase[Customer, CustomerCreate, CustomerUpdate]):
    def get_multi_with_filter(self, db: Session, *,
                              skip: int = 0, limit: int = 100,
                              filter_params: CustomerFilter) -> list[CustomerSchema]:
        query = db.query(self.model)
        if filter_params.name:
            query = query.filter(Customer.name.ilike(f"%{filter_params.name}%"))
        if filter_params.email:
            query = query.filter(Customer.email == filter_params.email)
        customers = query.offset(skip).limit(limit).all()
        return [CustomerSchema.model_validate(x) for x in customers]


customer = CRUDCustomer(Customer)

# /server/app/crud/product.py

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from public_api.shared_schemas import (
    ProductCreate, ProductUpdate,
    ProductFilter, ProductWithCategoryAndInventory
)
from server.app.models import (
    Product
)
from .base import CRUDBase


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):

    def get_multi_with_category_and_inventory(
            self, db: Session, *,
            skip: int = 0, limit: int = 100,
            filter_params: ProductFilter) -> list[ProductWithCategoryAndInventory]:
        query = db.query(Product).options(
            joinedload(Product.category),
            joinedload(Product.inventory_items)
        )
        if filter_params.name:
            query = query.filter(Product.name.ilike(f"%{filter_params.name}%"))
        if filter_params.category_id:
            query = query.filter(Product.category_id == filter_params.category_id)
        if filter_params.sku:
            query = query.filter(Product.sku == filter_params.sku)
        if filter_params.barcode:
            query = query.filter(Product.barcode == filter_params.barcode)

        products = query.offset(skip).limit(limit).all()
        return [ProductWithCategoryAndInventory.model_validate(product) for product in products]

    def get_max_id(self, db: Session) -> int:
        max_id = db.query(func.max(Product.id)).scalar()
        return max_id if max_id is not None else 0


product = CRUDProduct(Product)

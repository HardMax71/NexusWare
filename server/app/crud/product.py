# /server/app/crud/product.py
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from server.app.models import (
    Product
)
from server.app.schemas import (
    Product as ProductSchema,
    ProductWithInventory as ProductWithInventorySchema,
    ProductCreate, ProductUpdate,
    ProductFilter
)
from .base import CRUDBase


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    def get_with_category_and_inventory(self, db: Session, id: int) -> Optional[ProductWithInventorySchema]:
        current_product = db.query(Product).filter(Product.product_id == id).options(
            joinedload(Product.category),
            joinedload(Product.inventory_items)
        ).first()
        return ProductWithInventorySchema.model_validate(current_product) if current_product else None

    def get_multi_with_category_and_inventory(
            self, db: Session,
            skip: int = 0, limit: int = 100,
            filter_params: Optional[ProductFilter] = None) -> list[ProductWithInventorySchema]:
        query = db.query(Product).options(
            joinedload(Product.category),
            joinedload(Product.inventory_items)
        )

        if filter_params:
            if filter_params.name:
                query = query.filter(Product.name.ilike(f"%{filter_params.name}%"))
            if filter_params.category_id:
                query = query.filter(Product.category_id == filter_params.category_id)
            if filter_params.sku:
                query = query.filter(Product.sku == filter_params.sku)
            if filter_params.barcode:
                query = query.filter(Product.barcode == filter_params.barcode)

        products = query.offset(skip).limit(limit).all()
        return [ProductWithInventorySchema.model_validate(product) for product in products]

    def get_by_barcode(self, db: Session, barcode: str) -> Optional[ProductSchema]:
        current_product = db.query(Product).filter(Product.barcode == barcode).first()
        return ProductSchema.model_validate(current_product) if current_product else None


product = CRUDProduct(Product)
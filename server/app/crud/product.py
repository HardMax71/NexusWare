# /server/app/crud/product.py

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from public_api.shared_schemas import (
    ProductCreate, ProductUpdate,
    ProductFilter, ProductWithCategoryAndInventory
)
from server.app.models import (
    Product, Inventory
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

    def advanced_search(
            self,
            db: Session,
            *,
            q: str | None = None,
            category_id: int | None = None,
            min_price: float | None = None,
            max_price: float | None = None,
            in_stock: bool | None = None,
            sort_by: str | None = None,
            sort_order: str | None = "asc",
            skip: int = 0,
            limit: int = 100
    ) -> list[ProductWithCategoryAndInventory]:
        query = db.query(Product).options(
            joinedload(Product.category),
            joinedload(Product.inventory_items)
        )

        # Apply filters
        if q:
            query = query.filter(
                or_(
                    Product.name.ilike(f"%{q}%"),
                    Product.description.ilike(f"%{q}%"),
                    Product.sku.ilike(f"%{q}%")
                )
            )

        if category_id is not None:
            query = query.filter(Product.category_id == category_id)

        if min_price is not None:
            query = query.filter(Product.price >= min_price)

        if max_price is not None:
            query = query.filter(Product.price <= max_price)

        if in_stock is not None:
            if in_stock:
                query = query.join(Inventory).filter(Inventory.quantity > 0)
            else:
                query = query.outerjoin(Inventory).group_by(Product.id).having(func.sum(Inventory.quantity) == 0)

        if sort_by:
            sort_column = getattr(Product, sort_by, None)
            if sort_column is not None:
                if sort_order and sort_order.lower() == "desc":
                    sort_column = sort_column.desc()
                query = query.order_by(sort_column)

        # Apply pagination
        products = query.offset(skip).limit(limit).all()

        return [ProductWithCategoryAndInventory.model_validate(product) for product in products]


product = CRUDProduct(Product)

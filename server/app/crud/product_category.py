# /server/app/crud/product_category.py

from app.crud.base import CRUDBase
from app.models import ProductCategory
from public_api.shared_schemas import (
    ProductCategoryCreate, ProductCategoryUpdate
)


class CRUDProductCategory(CRUDBase[ProductCategory, ProductCategoryCreate, ProductCategoryUpdate]):
    pass


product_category = CRUDProductCategory(ProductCategory)

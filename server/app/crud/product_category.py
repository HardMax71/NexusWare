# /server/app/crud/product_category.py

from server.app.models import (
    ProductCategory
)
from public_api.shared_schemas import (
    ProductCategoryCreate, ProductCategoryUpdate
)
from .base import CRUDBase


class CRUDProductCategory(CRUDBase[ProductCategory, ProductCategoryCreate, ProductCategoryUpdate]):
    pass


product_category = CRUDProductCategory(ProductCategory)

# /server/app/crud/product_category.py

from server.app.models import (
    ProductCategory
)
from server.app.schemas import (
    ProductCategoryCreate, ProductCategoryUpdate
)
from .base import CRUDBase


class CRUDProductCategory(CRUDBase[ProductCategory, ProductCategoryCreate, ProductCategoryUpdate]):
    pass


product_category = CRUDProductCategory(ProductCategory)

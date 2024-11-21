# public_api/api/categories.py

from typing import List

from public_api.api.client import APIClient
from public_api.shared_schemas import ProductCategory, ProductCategoryCreate, ProductCategoryUpdate


class CategoriesAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_category(self, category: ProductCategoryCreate) -> ProductCategory:
        response = self.client.post("/product_categories/", json=category.model_dump())
        return ProductCategory.model_validate(response)

    def get_categories(self, skip: int = 0, limit: int = 100) -> List[ProductCategory]:
        response = self.client.get(f"/product_categories/?skip={skip}&limit={limit}")
        return [ProductCategory.model_validate(item) for item in response]

    def get_category(self, category_id: int) -> ProductCategory:
        response = self.client.get(f"/product_categories/{category_id}")
        return ProductCategory.model_validate(response)

    def update_category(self, category_id: int, category: ProductCategoryUpdate) -> ProductCategory:
        response = self.client.put(f"/product_categories/{category_id}", json=category.model_dump())
        return ProductCategory.model_validate(response)

    def delete_category(self, category_id: int) -> None:
        self.client.delete(f"/product_categories/{category_id}")

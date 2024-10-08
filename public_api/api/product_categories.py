from typing import List

from public_api.shared_schemas.inventory import ProductCategoryCreate, ProductCategoryUpdate, ProductCategory
from .client import APIClient


class ProductCategoriesAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_category(self, category_data: ProductCategoryCreate) -> ProductCategory:
        response = self.client.post("/product_categories/", json=category_data.model_dump(mode="json"))
        return ProductCategory.model_validate(response)

    def get_categories(self, skip: int = 0, limit: int = 100) -> List[ProductCategory]:
        response = self.client.get("/product_categories/", params={"skip": skip, "limit": limit})
        return [ProductCategory.model_validate(item) for item in response]

    def get_category(self, category_id: int) -> ProductCategory:
        response = self.client.get(f"/product_categories/{category_id}")
        return ProductCategory.model_validate(response)

    def update_category(self, category_id: int, category_data: ProductCategoryUpdate) -> ProductCategory:
        response = self.client.put(f"/product_categories/{category_id}",
                                   json=category_data.model_dump(mode="json", exclude_unset=True))
        return ProductCategory.model_validate(response)

    def delete_category(self, category_id: int) -> None:
        self.client.delete(f"/product_categories/{category_id}")

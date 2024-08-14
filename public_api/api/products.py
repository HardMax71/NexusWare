from typing import List, Optional

from public_api.shared_schemas.inventory import (
    ProductCreate, ProductUpdate, Product, ProductWithCategoryAndInventory,
    ProductFilter, BarcodeData
)
from .client import APIClient


class ProductsAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_product(self, product_data: ProductCreate) -> Product:
        response = self.client.post("/products/", json=product_data.model_dump(mode="json"))
        return Product.model_validate(response)

    def get_products(self, skip: int = 0, limit: int = 100,
                     product_filter: Optional[ProductFilter] = None) -> List[ProductWithCategoryAndInventory]:
        params = {"skip": skip, "limit": limit}
        if product_filter:
            params.update(product_filter.model_dump(mode="json", exclude_unset=True))
        response = self.client.get("/products/", params=params)
        return [ProductWithCategoryAndInventory.model_validate(item) for item in response]

    def get_product(self, product_id: int) -> ProductWithCategoryAndInventory:
        response = self.client.get(f"/products/{product_id}")
        return ProductWithCategoryAndInventory.model_validate(response)

    def update_product(self, product_id: int, product_data: ProductUpdate) -> Product:
        response = self.client.put(f"/products/{product_id}",
                                   json=product_data.model_dump(mode="json", exclude_unset=True))
        return Product.model_validate(response)

    def delete_product(self, product_id: int) -> Product:
        response = self.client.delete(f"/products/{product_id}")
        return Product.model_validate(response)

    def get_product_by_barcode(self, barcode: str) -> Product:
        barcode_data = BarcodeData(barcode=barcode)
        response = self.client.post("/products/barcode", json=barcode_data.model_dump(mode="json"))
        return Product.model_validate(response)

    def get_product_substitutes(self, product_id: int) -> List[Product]:
        response = self.client.get(f"/products/{product_id}/substitutes")
        return [Product.model_validate(item) for item in response]

    def add_product_substitute(self, product_id: int, substitute_id: int) -> Product:
        response = self.client.post(f"/products/{product_id}/substitutes", json={"substitute_id": substitute_id})
        return Product.model_validate(response)

    def get_max_product_id(self) -> int:
        response = self.client.get("/products/max_id")
        return response

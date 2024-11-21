from public_api.shared_schemas import Product, Order
from public_api.api.client import APIClient


class SearchAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def search_products(
            self,
            q: str | None = None,
            category_id: int | None = None,
            min_price: float | None = None,
            max_price: float | None = None,
            in_stock: bool | None = None,
            min_quantity: int | None = None,
            sort_by: str | None = None,
            sort_order: str | None = "asc"
    ) -> list[Product]:
        params = {
            "q": q,
            "category_id": category_id,
            "min_price": min_price,
            "max_price": max_price,
            "in_stock": in_stock,
            "min_quantity": min_quantity,
            "sort_by": sort_by,
            "sort_order": sort_order
        }
        response = self.client.get("/search/products", params={k: v for k, v in params.items() if v is not None})
        return [Product.model_validate(item) for item in response]

    def search_orders(
            self,
            q: str | None = None,
            status: str | None = None,
            min_total: float | None = None,
            max_total: float | None = None,
            start_date: int | None = None,
            end_date: int | None = None,
            customer_id: int | None = None,
            sort_by: str | None = None,
            sort_order: str | None = "asc"
    ) -> list[Order]:
        params = {
            "q": q,
            "status": status,
            "min_total": min_total,
            "max_total": max_total,
            "start_date": start_date,
            "end_date": end_date,
            "customer_id": customer_id,
            "sort_by": sort_by,
            "sort_order": sort_order
        }
        response = self.client.get("/search/orders", params={k: v for k, v in params.items() if v is not None})
        return [Order.model_validate(item) for item in response]

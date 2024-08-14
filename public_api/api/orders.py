from typing import List, Optional

from public_api.shared_schemas import (
    OrderCreate, OrderUpdate, Order, OrderWithDetails, OrderFilter,
    OrderSummary, ShippingInfo, OrderItemCreate, BulkOrderImportData,
    BulkOrderImportResult, OrderProcessingTimes
)
from .client import APIClient


class OrdersAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_order(self, order_data: OrderCreate) -> Order:
        response = self.client.post("/orders/", json=order_data.model_dump(mode="json"))
        return Order.model_validate(response)

    def get_orders(self, skip: int = 0, limit: int = 100,
                   filter_params: Optional[OrderFilter] = None) -> List[OrderWithDetails]:
        params = {"skip": skip, "limit": limit}
        if filter_params:
            params.update(filter_params.model_dump(mode="json", exclude_unset=True))
        response = self.client.get("/orders/", params=params)
        return [OrderWithDetails.model_validate(item) for item in response]

    def get_order(self, order_id: int) -> OrderWithDetails:
        response = self.client.get(f"/orders/{order_id}")
        return OrderWithDetails.model_validate(response)

    def update_order(self, order_id: int, order_data: OrderUpdate) -> Order:
        response = self.client.put(f"/orders/{order_id}", json=order_data.model_dump(mode="json", exclude_unset=True))
        return Order.model_validate(response)

    def delete_order(self, order_id: int) -> Order:
        response = self.client.delete(f"/orders/{order_id}")
        return Order.model_validate(response)

    def get_order_summary(self, date_from: Optional[int] = None,
                          date_to: Optional[int] = None) -> OrderSummary:
        params = {}
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        response = self.client.get("/orders/summary", params=params)
        return OrderSummary.model_validate(response)

    def cancel_order(self, order_id: int) -> Order:
        response = self.client.post(f"/orders/{order_id}/cancel")
        return Order.model_validate(response)

    def ship_order(self, order_id: int, shipping_info: ShippingInfo) -> Order:
        response = self.client.post(f"/orders/{order_id}/ship", json=shipping_info.model_dump(mode="json"))
        return Order.model_validate(response)

    def cancel_order_item(self, order_id: int, item_id: int) -> Order:
        response = self.client.post(f"/orders/{order_id}/cancel_item", json={"item_id": item_id})
        return Order.model_validate(response)

    def add_order_item(self, order_id: int, item_data: OrderItemCreate) -> Order:
        response = self.client.post(f"/orders/{order_id}/add_item", json=item_data.model_dump(mode="json"))
        return Order.model_validate(response)

    def get_backorders(self) -> List[Order]:
        response = self.client.get("/orders/backorders")
        return [Order.model_validate(item) for item in response]

    def bulk_import_orders(self, import_data: BulkOrderImportData) -> BulkOrderImportResult:
        response = self.client.post("/orders/bulk_import", json=import_data.model_dump(mode="json"))
        return BulkOrderImportResult.model_validate(response)

    def get_order_processing_times(self, start_date: int, end_date: int) -> OrderProcessingTimes:
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        response = self.client.get("/orders/processing_times", params=params)
        return OrderProcessingTimes.model_validate(response)

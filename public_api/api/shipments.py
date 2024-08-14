from typing import List, Optional

from public_api.shared_schemas import (
    Shipment, ShipmentCreate, ShipmentUpdate, ShipmentFilter,
    CarrierRate, ShippingLabel, ShipmentTracking
)
from .client import APIClient


class ShipmentsAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def get_shipments(self, skip: int = 0, limit: int = 100,
                      filter_params: Optional[ShipmentFilter] = None) -> List[Shipment]:
        params = {"skip": skip, "limit": limit}
        if filter_params:
            params.update(filter_params.model_dump(mode="json", exclude_unset=True))
        response = self.client.get("/shipments/", params=params)
        return [Shipment.model_validate(item) for item in response]

    def get_shipment(self, shipment_id: int) -> Shipment:
        response = self.client.get(f"/shipments/{shipment_id}")
        return Shipment.model_validate(response)

    def create_shipment(self, shipment_data: ShipmentCreate) -> Shipment:
        response = self.client.post("/shipments/", json=shipment_data.model_dump(mode="json"))
        return Shipment.model_validate(response)

    def update_shipment(self, shipment_id: int, shipment_data: ShipmentUpdate) -> Shipment:
        response = self.client.put(f"/shipments/{shipment_id}",
                                   json=shipment_data.model_dump(mode="json", exclude_unset=True))
        return Shipment.model_validate(response)

    def delete_shipment(self, shipment_id: int) -> Shipment:
        response = self.client.delete(f"/shipments/{shipment_id}")
        return Shipment.model_validate(response)

    def generate_shipping_label(self, shipment_id: int) -> ShippingLabel:
        response = self.client.post(f"/shipments/{shipment_id}/generate_label")
        return ShippingLabel.model_validate(response)

    def get_carrier_rates(self, weight: float, dimensions: str, destination_zip: str) -> List[CarrierRate]:
        params = {"weight": weight, "dimensions": dimensions, "destination_zip": destination_zip}
        response = self.client.get("/shipments/carrier_rates", params=params)
        return [CarrierRate.model_validate(item) for item in response]

    def track_shipment(self, shipment_id: int) -> ShipmentTracking:
        response = self.client.post(f"/shipments/{shipment_id}/track")
        return ShipmentTracking.model_validate(response)

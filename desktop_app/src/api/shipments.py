from .client import APIClient


class ShipmentsAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def get_shipments(self, skip=0, limit=100, filter_params=None):
        return self.client.get("/shipments/", params={"skip": skip, "limit": limit, **filter_params})

    def get_shipment(self, shipment_id):
        return self.client.get(f"/shipments/{shipment_id}")

    def create_shipment(self, shipment_data):
        return self.client.post("/shipments/", json=shipment_data)

    def update_shipment(self, shipment_id, shipment_data):
        return self.client.put(f"/shipments/{shipment_id}", json=shipment_data)

    def delete_shipment(self, shipment_id):
        return self.client.delete(f"/shipments/{shipment_id}")

    def generate_shipping_label(self, shipment_id):
        return self.client.post(f"/shipments/{shipment_id}/generate_label")

    def get_carrier_rates(self, weight, dimensions, destination_zip):
        params = {"weight": weight, "dimensions": dimensions, "destination_zip": destination_zip}
        return self.client.get("/shipments/carrier_rates", params=params)

    def track_shipment(self, shipment_id):
        return self.client.post(f"/shipments/{shipment_id}/track")

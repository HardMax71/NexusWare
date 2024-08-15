# /server/app/crud/shipment.py
from typing import Optional, List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from public_api.shared_schemas import CarrierCreate, CarrierUpdate
from public_api.shared_schemas import (Shipment as ShipmentSchema, ShipmentCreate, ShipmentUpdate,
                                       ShipmentFilter, ShipmentTracking, CarrierRate, ShippingLabel)
from server.app.models import Order, Shipment, Carrier
from .base import CRUDBase
from ..utils.generate_label import shipengine_api_call


class CRUDShipment(CRUDBase[Shipment, ShipmentCreate, ShipmentUpdate]):
    def get_multi_with_filter(self, db: Session, *,
                              skip: int = 0, limit: int = 100, filter_params: ShipmentFilter) -> list[ShipmentSchema]:
        query = db.query(self.model)
        if filter_params.status:
            query = query.filter(Shipment.status == filter_params.status)
        if filter_params.order_id:
            query = query.filter(Shipment.order_id == filter_params.order_id)
        if filter_params.carrier_id:
            query = query.filter(Shipment.carrier_id == filter_params.carrier_id)
        if filter_params.date_from:
            query = query.filter(Shipment.ship_date >= filter_params.date_from)
        if filter_params.date_to:
            query = query.filter(Shipment.ship_date <= filter_params.date_to)
        shipments = query.offset(skip).limit(limit).all()
        return [ShipmentSchema.model_validate(shipment) for shipment in shipments]

    def get_carrier_rates(self, db: Session, weight: float, dimensions: str, destination_zip: str) -> List[CarrierRate]:
        try:
            params = {
                "weight": weight,
                "dimensions": dimensions,
                "destination_zip": destination_zip
            }
            response = shipengine_api_call("rates/estimate", method="GET", data=params)

            return [CarrierRate(
                carrier_id=rate["carrier_id"],
                carrier_name=rate["carrier_name"],
                rate=rate["shipping_amount"]["amount"],
                estimated_delivery_time=rate["delivery_days"]
            ) for rate in response]
        except HTTPException as e:
            if e.status_code == 401:
                raise HTTPException(status_code=401, detail="Invalid ShipEngine API key")
            raise e

    def track(self, db: Session, *, shipment_id: int) -> Optional[ShipmentTracking]:
        shipment = self.get(db, id=shipment_id)
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")

        try:
            tracking_data = shipengine_api_call(
                f"tracking?carrier_code={shipment.carrier.name}&tracking_number={shipment.tracking_number}")

            return ShipmentTracking(
                shipment_id=shipment.id,
                tracking_number=shipment.tracking_number,
                current_status=tracking_data["status_description"],
                estimated_delivery_date=tracking_data.get("estimated_delivery_date"),
                tracking_history=tracking_data["events"]
            )
        except HTTPException as e:
            if e.status_code == 401:
                raise HTTPException(status_code=401, detail="Invalid ShipEngine API key")
            raise e

    def generate_label(self, db: Session, shipment_id: int) -> ShippingLabel:
        shipment = self.get(db, id=shipment_id)
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")

        order = db.query(Order).filter(Order.id == shipment.order_id).first()
        carrier = db.query(Carrier).filter(Carrier.id == shipment.carrier_id).first()

        if not order or not carrier:
            raise HTTPException(status_code=404, detail="Related order or carrier not found")

        label_data = {
            "shipment": {
                "service_code": "usps_priority_mail",
                "ship_to": {
                    "name": order.shipping_name,
                    "address_line1": order.shipping_address_line1,
                    "city_locality": order.shipping_city,
                    "state_province": order.shipping_state,
                    "postal_code": order.shipping_postal_code,
                    "country_code": order.shipping_country,
                    "phone": order.shipping_phone
                },
                "ship_from": {
                    "company_name": "Your Company Name",
                    "address_line1": "Your Address Line 1",
                    "city_locality": "Your City",
                    "state_province": "Your State",
                    "postal_code": "Your Postal Code",
                    "country_code": "US",
                    "phone": "Your Phone Number"
                },
                "packages": [
                    {
                        "weight": {
                            "value": 1.0,
                            "unit": "pound"
                        }
                    }
                ]
            }
        }

        try:
            response = shipengine_api_call("labels", method="POST", data=label_data)

            shipment.tracking_number = response["tracking_number"]
            shipment.label_id = response["label_id"]
            shipment.label_download_url = response["label_download"]["pdf"]
            db.commit()

            return ShippingLabel(
                shipment_id=shipment_id,
                tracking_number=shipment.tracking_number,
                label_id=shipment.label_id,
                label_download_url=shipment.label_download_url
            )
        except HTTPException as e:
            if e.status_code == 401:
                raise HTTPException(status_code=401, detail="Invalid ShipEngine API key")
            raise e


class CRUDCarrier(CRUDBase[Carrier, CarrierCreate, CarrierUpdate]):
    pass


shipment = CRUDShipment(Shipment)
carrier = CRUDCarrier(Carrier)

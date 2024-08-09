# /server/app/crud/warehouse.py
from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from server.app.models import (PickList, PickListItem,
                               Receipt, ReceiptItem, Shipment, Carrier, Order)
from server.app.schemas import (PickListCreate, PickListUpdate,
                                PickListItemCreate, PickListItemUpdate, ReceiptCreate,
                                ReceiptUpdate, ReceiptItemCreate, ReceiptItemUpdate,
                                ShipmentCreate, ShipmentUpdate,
                                CarrierCreate, CarrierUpdate, PickListFilter, InventoryAdjustment, LocationInventory,
                                InventoryMovement, WarehouseStats, ShipmentFilter, ReceiptFilter, ShipmentTracking,
                                CarrierRate, ShippingLabel, QualityCheckCreate, PickingPerformance,
                                OptimizedPickingRoute)
from .base import CRUDBase
from ..schemas.warehouse import InventoryMovementCreate, InventoryAdjustmentCreate
from ..utils.generate_label import shipengine_api_call


class CRUDPickList(CRUDBase[PickList, PickListCreate, PickListUpdate]):
    def create_with_items(self, db: Session, *, obj_in: PickListCreate) -> PickList:
        db_obj = PickList(
            order_id=obj_in.order_id,
            status=obj_in.status
        )
        db.add(db_obj)
        db.flush()
        for item in obj_in.items:
            db_item = PickListItem(**item.dict(), pick_list_id=db_obj.pick_list_id)
            db.add(db_item)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_with_items(self, db: Session, *, db_obj: PickList, obj_in: PickListUpdate) -> PickList:
        update_data = obj_in.dict(exclude_unset=True)
        if "items" in update_data:
            items = update_data.pop("items")
            for item in db_obj.pick_list_items:
                db.delete(item)
            for item in items:
                db_item = PickListItem(**item, pick_list_id=db_obj.pick_list_id)
                db.add(db_item)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def get_multi_with_filter(self, db: Session, *,
                              skip: int = 0, limit: int = 100,
                              filter_params: PickListFilter) -> list[PickList]:
        query = db.query(self.model)
        if filter_params.status:
            query = query.filter(PickList.status == filter_params.status)
        if filter_params.order_id:
            query = query.filter(PickList.order_id == filter_params.order_id)
        if filter_params.date_from:
            query = query.filter(PickList.created_at >= filter_params.date_from)
        if filter_params.date_to:
            query = query.filter(PickList.created_at <= filter_params.date_to)
        return query.offset(skip).limit(limit).all()

    def get_performance(self, db: Session, start_date: datetime, end_date: datetime) -> PickingPerformance:
        completed_pick_lists = db.query(PickList).filter(
            PickList.status == "completed",
            PickList.completed_at.between(start_date, end_date)
        ).all()

        total_time = sum((pl.completed_at - pl.created_at).total_seconds() for pl in completed_pick_lists)
        total_items = sum(sum(item.picked_quantity for item in pl.pick_list_items) for pl in completed_pick_lists)

        if len(completed_pick_lists) > 0:
            average_picking_time = total_time / len(completed_pick_lists) / 60  # in minutes
            items_picked_per_hour = (total_items / (total_time / 3600)) if total_time > 0 else 0
            accuracy_rate = sum(1 for pl in completed_pick_lists for item in pl.pick_list_items if
                                item.quantity == item.picked_quantity) / total_items if total_items > 0 else 1
        else:
            average_picking_time = 0
            items_picked_per_hour = 0
            accuracy_rate = 1

        return PickingPerformance(
            average_picking_time=average_picking_time,
            items_picked_per_hour=items_picked_per_hour,
            accuracy_rate=accuracy_rate
        )

    def optimize_route(self, db: Session, pick_list_id: int) -> OptimizedPickingRoute:
        pick_list = db.query(PickList).filter(PickList.pick_list_id == pick_list_id).first()
        if not pick_list:
            raise ValueError("Pick list not found")

        # Simple optimization: sort items by location
        optimized_items = sorted(pick_list.pick_list_items, key=lambda x: (
            x.location.zone_id, x.location.aisle, x.location.rack, x.location.shelf, x.location.bin))

        return OptimizedPickingRoute(
            pick_list_id=pick_list_id,
            optimized_route=[PickListItem.from_orm(item) for item in optimized_items]
        )

    def start(self, db: Session, *, pick_list_id: int, user_id: int) -> PickList:
        pick_list = db.query(PickList).filter(PickList.pick_list_id == pick_list_id).first()
        pick_list.status = "in_progress"
        db.commit()
        db.refresh(pick_list)
        return pick_list

    def complete(self, db: Session, *, pick_list_id: int, user_id: int) -> PickList:
        pick_list = db.query(PickList).filter(PickList.pick_list_id == pick_list_id).first()
        pick_list.status = "completed"
        pick_list.completed_at = func.now()
        db.commit()
        db.refresh(pick_list)
        return pick_list


class CRUDPickListItem(CRUDBase[PickListItem, PickListItemCreate, PickListItemUpdate]):
    pass


class CRUDReceipt(CRUDBase[Receipt, ReceiptCreate, ReceiptUpdate]):
    def create_with_items(self, db: Session, *, obj_in: ReceiptCreate) -> Receipt:
        db_obj = Receipt(
            po_id=obj_in.po_id,
            status=obj_in.status
        )
        db.add(db_obj)
        db.flush()
        for item in obj_in.items:
            db_item = ReceiptItem(**item.dict(), receipt_id=db_obj.receipt_id)
            db.add(db_item)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_with_items(self, db: Session, *, db_obj: Receipt, obj_in: ReceiptUpdate) -> Receipt:
        update_data = obj_in.dict(exclude_unset=True)
        if "items" in update_data:
            items = update_data.pop("items")
            for item in db_obj.receipt_items:
                db.delete(item)
            for item in items:
                db_item = ReceiptItem(**item, receipt_id=db_obj.receipt_id)
                db.add(db_item)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def get_multi_with_filter(self, db: Session, *,
                              skip: int = 0, limit: int = 100, filter_params: ReceiptFilter) -> list[Receipt]:
        query = db.query(self.model)
        if filter_params.status:
            query = query.filter(Receipt.status == filter_params.status)
        if filter_params.po_id:
            query = query.filter(Receipt.po_id == filter_params.po_id)
        if filter_params.date_from:
            query = query.filter(Receipt.received_date >= filter_params.date_from)
        if filter_params.date_to:
            query = query.filter(Receipt.received_date <= filter_params.date_to)
        return query.offset(skip).limit(limit).all()

    def report_discrepancy(self, db: Session, *, receipt_id: int, item_id: int, discrepancy: int) -> ReceiptItem:
        item = db.query(ReceiptItem).filter(ReceiptItem.receipt_id == receipt_id,
                                            ReceiptItem.receipt_item_id == item_id).first()
        item.quantity_received += discrepancy
        db.commit()
        db.refresh(item)
        return item

    def get_expected_today(self, db: Session) -> int:
        return db.query(func.sum(ReceiptItem.quantity_received)).filter(
            func.date(Receipt.received_date) == func.current_date()).scalar()

    def perform_quality_check(self, db: Session, receipt_id: int,
                              quality_check: QualityCheckCreate) -> Receipt:
        receipt = db.query(Receipt).filter(Receipt.receipt_id == receipt_id).first()
        if not receipt:
            raise ValueError("Receipt not found")

        # Implement quality check logic here
        receipt_item = next((item for item in receipt.receipt_items if item.product_id == quality_check.product_id),
                            None)
        if receipt_item:
            receipt_item.quality_check_result = quality_check.result
            receipt_item.quality_check_notes = quality_check.notes

        receipt.status = "quality_checked"
        db.commit()
        db.refresh(receipt)
        return receipt


class CRUDReceiptItem(CRUDBase[ReceiptItem, ReceiptItemCreate, ReceiptItemUpdate]):
    pass


class CRUDShipment(CRUDBase[Shipment, ShipmentCreate, ShipmentUpdate]):
    def get_multi_with_filter(self, db: Session, *,
                              skip: int = 0, limit: int = 100, filter_params: ShipmentFilter) -> list[Shipment]:
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
        return query.offset(skip).limit(limit).all()

    def track(self, db: Session, *, shipment_id: int) -> Optional[ShipmentTracking]:
        shipment = db.query(Shipment).filter(Shipment.shipment_id == shipment_id).first()
        if not shipment:
            return None

        # Use ShipEngine API to get tracking information
        tracking_data = shipengine_api_call(f"tracking/{shipment.tracking_number}", method="GET")

        return ShipmentTracking(
            shipment_id=shipment.shipment_id,
            tracking_number=shipment.tracking_number,
            current_status=tracking_data["status"],
            estimated_delivery_date=tracking_data.get("estimated_delivery_date"),
            tracking_history=tracking_data["events"]
        )

    def get_carrier_rates(self, db: Session, weight: float,
                          dimensions: str, destination_zip: str) -> list[CarrierRate]:
        carriers = db.query(Carrier).all()
        # This is a placeholder implementation. In a real-world scenario, 
        # you would integrate with carrier APIs
        return [
            CarrierRate(
                carrier_id=carrier.carrier_id,
                carrier_name=carrier.name,
                rate=weight * 2.5,  # Placeholder calculation
                estimated_delivery_time="3-5 business days"
            )
            for carrier in carriers
        ]

    def generate_label(self, db: Session, shipment_id: int) -> ShippingLabel:
        shipment = db.query(Shipment).filter(Shipment.shipment_id == shipment_id).first()
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")

        # Fetch related order and carrier information
        order = db.query(Order).filter(Order.order_id == shipment.order_id).first()
        carrier = db.query(Carrier).filter(Carrier.carrier_id == shipment.carrier_id).first()

        if not order or not carrier:
            raise HTTPException(status_code=404, detail="Related order or carrier not found")

        # Prepare data for ShipEngine API
        label_data = {
            "shipment": {
                "service_code": "usps_priority_mail",
                # This should be dynamically selected based on the carrier and service
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

        # Call ShipEngine API to create label
        response = shipengine_api_call("labels", method="POST", data=label_data)

        # Update shipment with tracking information
        shipment.tracking_number = response["tracking_number"]
        shipment.label_id = response["label_id"]
        shipment.label_download_url = response["label_download_url"]
        db.commit()

        return ShippingLabel(
            shipment_id=shipment_id,
            tracking_number=shipment.tracking_number,
            label_id=shipment.label_id,
            label_download_url=shipment.label_download_url
        )


class CRUDCarrier(CRUDBase[Carrier, CarrierCreate, CarrierUpdate]):
    pass


class CRUDWarehouse:
    def get_stats(self, db: Session) -> WarehouseStats:
        total_pick_lists = db.query(func.count(PickList.pick_list_id)).scalar()
        completed_pick_lists = db.query(func.count(PickList.pick_list_id)).filter(
            PickList.status == "completed").scalar()
        total_receipts = db.query(func.count(Receipt.receipt_id)).scalar()
        completed_receipts = db.query(func.count(Receipt.receipt_id)).filter(Receipt.status == "completed").scalar()
        total_shipments = db.query(func.count(Shipment.shipment_id)).scalar()
        completed_shipments = db.query(func.count(Shipment.shipment_id)).filter(Shipment.status == "completed").scalar()

        return WarehouseStats(
            total_pick_lists=total_pick_lists,
            completed_pick_lists=completed_pick_lists,
            total_receipts=total_receipts,
            completed_receipts=completed_receipts,
            total_shipments=total_shipments,
            completed_shipments=completed_shipments
        )

    def get_location_inventory(self, db: Session, *, location_id: int) -> list[LocationInventory]:
        return db.query(LocationInventory).filter(LocationInventory.location_id == location_id).all()

    def update_location_inventory(self, db: Session, *, location_id: int, product_id: int,
                                  quantity: int) -> LocationInventory:
        inventory = db.query(LocationInventory).filter(
            and_(
                LocationInventory.location_id == location_id,
                LocationInventory.product_id == product_id
            )
        ).first()
        if not inventory:
            inventory = LocationInventory(location_id=location_id, product_id=product_id, quantity=quantity)
            db.add(inventory)
        else:
            inventory.quantity = quantity
        db.commit()
        db.refresh(inventory)
        return inventory

    def move_inventory(self, db: Session, *, movement: InventoryMovementCreate) -> InventoryMovement:
        # Decrease quantity in the source location
        self.update_location_inventory(
            db,
            location_id=movement.from_location_id,
            product_id=movement.product_id,
            quantity=db.query(LocationInventory.quantity).filter(
                LocationInventory.location_id == movement.from_location_id,
                LocationInventory.product_id == movement.product_id
            ).scalar() - movement.quantity
        )

        # Increase quantity in the destination location
        self.update_location_inventory(
            db,
            location_id=movement.to_location_id,
            product_id=movement.product_id,
            quantity=db.query(LocationInventory.quantity).filter(
                LocationInventory.location_id == movement.to_location_id,
                LocationInventory.product_id == movement.product_id
            ).scalar() + movement.quantity
        )

        # Record the movement
        db_movement = InventoryMovement(**movement.dict())
        db.add(db_movement)
        db.commit()
        db.refresh(db_movement)
        return db_movement

    def adjust_inventory(self, db: Session, *, adjustment: InventoryAdjustmentCreate) -> InventoryAdjustment:
        self.update_location_inventory(
            db,
            location_id=adjustment.location_id,
            product_id=adjustment.product_id,
            quantity=db.query(LocationInventory.quantity).filter(
                LocationInventory.location_id == adjustment.location_id,
                LocationInventory.product_id == adjustment.product_id
            ).scalar() + adjustment.quantity_change
        )

        # Record the adjustment
        db_adjustment = InventoryAdjustment(**adjustment.dict())
        db.add(db_adjustment)
        db.commit()
        db.refresh(db_adjustment)
        return db_adjustment


pick_list = CRUDPickList(PickList)
receipt = CRUDReceipt(Receipt)
shipment = CRUDShipment(Shipment)
carrier = CRUDCarrier(Carrier)
whole_warehouse = CRUDWarehouse()
pick_list_item = CRUDPickListItem(PickListItem)
receipt_item = CRUDReceiptItem(ReceiptItem)

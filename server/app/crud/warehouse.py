# /server/app/crud/warehouse.py
from server.app.models import (PickList, PickListItem,
                               Receipt, ReceiptItem, Shipment, Carrier)
from server.app.schemas import (PickListCreate, PickListUpdate,
                                PickListItemCreate, PickListItemUpdate, ReceiptCreate,
                                ReceiptUpdate, ReceiptItemCreate, ReceiptItemUpdate,
                                ShipmentCreate, ShipmentUpdate,
                                CarrierCreate, CarrierUpdate)

from .base import CRUDBase


class CRUDPickList(CRUDBase[PickList, PickListCreate, PickListUpdate]):
    pass


class CRUDPickListItem(CRUDBase[PickListItem, PickListItemCreate, PickListItemUpdate]):
    pass


class CRUDReceipt(CRUDBase[Receipt, ReceiptCreate, ReceiptUpdate]):
    pass


class CRUDReceiptItem(CRUDBase[ReceiptItem, ReceiptItemCreate, ReceiptItemUpdate]):
    pass


class CRUDShipment(CRUDBase[Shipment, ShipmentCreate, ShipmentUpdate]):
    pass


class CRUDCarrier(CRUDBase[Carrier, CarrierCreate, CarrierUpdate]):
    pass


pick_list = CRUDPickList(PickList)
pick_list_item = CRUDPickListItem(PickListItem)
receipt = CRUDReceipt(Receipt)
receipt_item = CRUDReceiptItem(ReceiptItem)
shipment = CRUDShipment(Shipment)
carrier = CRUDCarrier(Carrier)

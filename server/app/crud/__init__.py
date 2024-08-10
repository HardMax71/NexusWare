# /server/app/crud/__init__.py
from .asset import asset, asset_maintenance
from .audit import audit_log
from .inventory import product, product_category, inventory, location, zone
from .order import order, order_item, customer, purchase_order, po_item, supplier
from .permission import permission
from .pick_list import pick_list, pick_list_item
from .quality import quality_check, quality_standard, quality_alert
from .receipt import receipt, receipt_item
from .reports import reports
from .role import role
from .shipment import shipment, carrier
from .task import task
from .user import user
from .warehouse import whole_warehouse
from .yard import yard_location, dock_appointment

import random
import time
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from server.app.core.config import settings
from server.app.core.security import get_password_hash
from server.app.models import (
    Asset, AssetMaintenance, AuditLog, Carrier, Customer, DockAppointment,
    Inventory, LocationInventory, InventoryMovement, InventoryAdjustment,
    Location, Order, OrderItem, PurchaseOrder, POItem, Product, ProductCategory,
    QualityCheck, QualityStandard, QualityAlert, Task, TaskComment, User, Role,
    Permission, RolePermission, PickList, PickListItem, Receipt, ReceiptItem,
    Shipment, Supplier, YardLocation, Zone, Base
)

# Establish the database connection
engine = sa.create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in the database
Base.metadata.create_all(bind=engine)


# Helper function to generate a random timestamp in the past or future
def random_timestamp(past_days=0, future_days=0) -> int:
    now = int(time.time())
    offset = random.randint(-past_days * 86400, future_days * 86400)
    return now + offset


def add_sample_data():
    db = SessionLocal()

    # Roles and Permissions
    admin_role = Role(role_name="Admin")
    user_role = Role(role_name="User")
    manager_role = Role(role_name="Manager")
    db.add_all([admin_role, user_role, manager_role])
    db.commit()

    permissions = [
        Permission(permission_name="create_order"),
        Permission(permission_name="update_inventory"),
        Permission(permission_name="manage_users"),
        Permission(permission_name="view_reports"),
        Permission(permission_name="manage_shipments"),
    ]
    db.add_all(permissions)
    db.commit()

    # Users
    admin_user = User(
        username="admin",
        email="admin@example.com",
        password_hash=get_password_hash("admin"),
        role_id=admin_role.id,
        is_active=True
    )
    regular_user = User(
        username="user",
        email="user@example.com",
        password_hash=get_password_hash("user"),
        role_id=user_role.id,
        is_active=True
    )
    manager_user = User(
        username="manager",
        email="manager@example.com",
        password_hash=get_password_hash("manager"),
        role_id=manager_role.id,
        is_active=True
    )
    db.add_all([admin_user, regular_user, manager_user])
    db.commit()
    # Product Categories
    categories = [
        ProductCategory(name="Electronics"),
        ProductCategory(name="Clothing"),
        ProductCategory(name="Home & Garden"),
        ProductCategory(name="Books"),
        ProductCategory(name="Toys"),
    ]
    db.add_all(categories)
    db.commit()
    # Products
    products = [
        Product(sku="SKU001", name="Smartphone", category_id=categories[0].id, price=599.99,
                unit_of_measure="piece", weight=0.2, dimensions="15x7x1"),
        Product(sku="SKU002", name="T-shirt", category_id=categories[1].id, price=19.99,
                unit_of_measure="piece", weight=0.1, dimensions="30x20x2"),
        Product(sku="SKU003", name="Garden Hose", category_id=categories[2].id, price=29.99,
                unit_of_measure="piece", weight=1.5, dimensions="100x10x10"),
        Product(sku="SKU004", name="Novel", category_id=categories[3].id, price=14.99, unit_of_measure="piece",
                weight=0.3, dimensions="20x15x3"),
        Product(sku="SKU005", name="Action Figure", category_id=categories[4].id, price=24.99,
                unit_of_measure="piece", weight=0.1, dimensions="10x5x15"),
    ]
    db.add_all(products)
    db.commit()
    # Zones and Locations
    zones = [Zone(name="Main Warehouse", description="Primary storage area"),
             Zone(name="Overflow Storage", description="Secondary storage for excess inventory")]
    db.add_all(zones)
    db.commit()
    locations = []
    for zone in zones:
        for aisle in ['A', 'B', 'C']:
            for rack in range(1, 4):
                for shelf in range(1, 4):
                    location = Location(zone_id=zone.id, aisle=aisle, rack=str(rack), shelf=str(shelf),
                                        name=f"{zone.name}-{aisle}{rack}-{shelf}")
                    locations.append(location)
    db.add_all(locations)
    db.commit()
    # Inventory
    for product in products:
        for _ in range(3):  # Multiple inventory entries per product
            location = random.choice(locations)
            inventory = Inventory(
                product_id=product.id,
                location_id=location.id,
                quantity=random.randint(50, 200),
                expiration_date=random_timestamp(future_days=365)
            )
            db.add(inventory)
    db.commit()
    # Customers
    customers = [
        Customer(name="John Doe", email="john@example.com", phone="1234567890", address="123 Main St"),
        Customer(name="Jane Smith", email="jane@example.com", phone="0987654321", address="456 Elm St"),
        Customer(name="Bob Johnson", email="bob@example.com", phone="1122334455", address="789 Oak St"),
    ]
    db.add_all(customers)
    db.commit()
    # Orders and Order Items
    for _ in range(20):  # Create 20 orders
        customer = random.choice(customers)
        order = Order(
            customer_id=customer.id,
            status=random.choice(["Pending", "Processing", "Shipped", "Delivered"]),
            total_amount=0,
            shipping_name=customer.name,
            shipping_address_line1=customer.address,
            shipping_city="Sample City",
            shipping_state="Sample State",
            shipping_postal_code="12345",
            shipping_country="Sample Country",
            shipping_phone=customer.phone,
            order_date=random_timestamp(past_days=30)  # Set order date
        )
        db.add(order)
        db.flush()  # Flush to get the order_id

        # Generate 1 to 5 order items for each order
        for _ in range(random.randint(1, 5)):
            product = random.choice(products)
            quantity = random.randint(1, 10)
            unit_price = product.price
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price
            )
            db.add(order_item)
            order.total_amount += quantity * unit_price

        # Update the order's total amount
        db.add(order)
    db.commit()
    # Suppliers
    suppliers = [
        Supplier(name="Acme Corp", contact_person="John Acme", email="john@acme.com", phone="1111111111",
                 address="1 Acme Way"),
        Supplier(name="XYZ Distributors", contact_person="Jane XYZ", email="jane@xyz.com", phone="2222222222",
                 address="2 XYZ Street"),
    ]
    db.add_all(suppliers)
    db.commit()
    # Purchase Orders
    for _ in range(10):  # Create 10 purchase orders
        supplier = random.choice(suppliers)
        po = PurchaseOrder(
            supplier_id=supplier.id,
            status=random.choice(["Pending", "Ordered", "Received"]),
            expected_delivery_date=random_timestamp(future_days=30)
        )
        for product in random.sample(products, random.randint(1, 3)):
            quantity = random.randint(10, 50)
            POItem(po_id=po.id, product_id=product.id, quantity=quantity,
                   unit_price=int(product.price) * 0.7)
        db.add(po)
    db.commit()
    # Assets
    asset_types = ["Forklift", "Pallet Jack", "Conveyor Belt", "Scanning Device"]
    assets = []
    for i in range(10):
        asset_type = random.choice(asset_types)
        asset = Asset(
            asset_type=asset_type,
            asset_name=f"{asset_type} {i + 1}",
            serial_number=f"{asset_type[:2].upper()}{i + 1:03d}",
            purchase_date=random_timestamp(past_days=1000),
            status=random.choice(["Active", "Under Maintenance", "Inactive"]),
            location_id=random.choice(locations).id
        )
        assets.append(asset)
    db.add_all(assets)
    db.commit()
    # Asset Maintenance
    for asset in assets:
        for _ in range(random.randint(1, 3)):
            maintenance = AssetMaintenance(
                asset_id=asset.id,
                maintenance_type=random.choice(["Routine Check", "Repair", "Upgrade"]),
                scheduled_date=random_timestamp(future_days=90),
                completed_date=random_timestamp(past_days=30),
                performed_by=random.choice([admin_user.id, manager_user.id]),
                notes="Sample maintenance notes"
            )
            db.add(maintenance)
    db.commit()
    # Quality Checks
    for _ in range(50):  # Create 50 quality checks
        product = random.choice(products)
        check = QualityCheck(
            product_id=product.id,
            performed_by=random.choice([admin_user.id, manager_user.id, regular_user.id]),
            result=random.choice(["Pass", "Fail", "Pending Review"]),
            notes=f"Quality check for {product.name}"
        )
        db.add(check)
    db.commit()
    # Quality Standards
    for product in products:
        standard = QualityStandard(
            product_id=product.id,
            criteria=f"Standard for {product.name}",
            acceptable_range="90-100%"
        )
        db.add(standard)
    db.commit()
    # Quality Alerts
    for _ in range(10):
        alert = QualityAlert(
            product_id=random.choice(products).id,
            alert_type=random.choice(["Minor Issue", "Major Problem", "Critical Failure"]),
            description="Sample quality alert description",
            resolved_at=random.choice([None, random_timestamp(past_days=10)])
        )
        db.add(alert)
    db.commit()
    # Tasks
    task_types = ["Inventory Count", "Equipment Maintenance", "Order Processing", "Shipment Preparation"]
    for _ in range(20):  # Create 20 tasks
        task = Task(
            task_type=random.choice(task_types),
            description=f"Perform {random.choice(task_types).lower()} task",
            assigned_to=random.choice([admin_user.id, manager_user.id, regular_user.id]),
            due_date=random_timestamp(future_days=30),
            priority=random.choice(["Low", "Medium", "High"]),
            status=random.choice(["Pending", "In Progress", "Completed"])
        )
        db.add(task)
        db.commit()
        # Add some task comments
        for _ in range(random.randint(0, 3)):
            comment = TaskComment(
                task_id=task.id,
                user_id=random.choice([admin_user.id, manager_user.id, regular_user.id]),
                comment="Sample task comment"
            )
            db.add(comment)
    db.commit()
    # Warehouse Operations
    for order in db.query(Order).filter(Order.status == "Processing").limit(5):
        pick_list = PickList(order_id=order.id, status="In Progress")
        db.add(pick_list)
        for order_item in order.order_items:
            PickListItem(
                pick_list_id=pick_list.id,
                product_id=order_item.product_id,
                location_id=random.choice(locations).id,
                quantity=order_item.quantity,
                picked_quantity=random.randint(0, order_item.quantity)
            )
    db.commit()
    carriers = [
        Carrier(name="Fast Shipping", contact_info="contact@fastshipping.com"),
        Carrier(name="Global Logistics", contact_info="support@globallogistics.com"),
        Carrier(name="Quick Delivery", contact_info="info@quickdelivery.com"),
    ]
    db.add_all(carriers)
    db.commit()
    # Yard Management
    yard_locations = [
        YardLocation(name="Dock 1", type="Loading", status="Available", capacity=2),
        YardLocation(name="Dock 2", type="Unloading", status="Available", capacity=2),
        YardLocation(name="Parking Spot 1", type="Parking", status="Occupied", capacity=1),
    ]
    db.add_all(yard_locations)
    db.commit()
    for _ in range(10):  # Create 10 dock appointments
        appointment = DockAppointment(
            yard_location_id=random.choice(yard_locations).id,
            appointment_time=random_timestamp(future_days=30),
            carrier_id=random.choice(carriers).id,
            type=random.choice(["Inbound", "Outbound"]),
            status=random.choice(["Scheduled", "In Progress", "Completed"]),
            actual_arrival_time=random_timestamp(past_days=5),
            actual_departure_time=random_timestamp(future_days=5)
        )
        db.add(appointment)
    db.commit()
    # Shipments
    for order in db.query(Order).filter(Order.status == "Shipped").limit(10):
        shipment = Shipment(
            order_id=order.id,
            carrier_id=random.choice(carriers).id,
            tracking_number=f"TRK{random.randint(1000000, 9999999)}",
            ship_date=random_timestamp(past_days=10),
            status=random.choice(["In Transit", "Delivered"]),
            label_id=f"LBL{random.randint(1000000, 9999999)}",
            label_download_url=f"https://example.com/labels/LBL{random.randint(1000000, 9999999)}.pdf"
        )
        db.add(shipment)
    db.commit()
    # Receipts
    for po in db.query(PurchaseOrder).filter(PurchaseOrder.status == "Received").limit(5):
        receipt = Receipt(
            po_id=po.id,
            received_date=random_timestamp(past_days=30),
            status="Completed"
        )
        for po_item in po.po_items:
            ReceiptItem(
                receipt_id=receipt.id,
                product_id=po_item.id,
                quantity_received=po_item.quantity,
                location_id=random.choice(locations).id
            )
        db.add(receipt)
    db.commit()
    # Audit Logs
    for _ in range(50):  # Create 50 audit log entries
        audit_log = AuditLog(
            user_id=random.choice([admin_user.id, manager_user.id, regular_user.id]),
            action_type=random.choice(["Create", "Update", "Delete"]),
            table_name=random.choice(["orders", "products", "inventory", "users"]),
            record_id=random.randint(1, 100),
            old_value="{'sample': 'old_value'}",
            new_value="{'sample': 'new_value'}"
        )
        db.add(audit_log)
    db.commit()
    # Inventory Movements
    for _ in range(30):  # Create 30 inventory movements
        product = random.choice(products)
        from_location = random.choice(locations)
        to_location = random.choice([loc for loc in locations if loc != from_location])
        movement = InventoryMovement(
            product_id=product.id,
            from_location_id=from_location.id,
            to_location_id=to_location.id,
            quantity=random.randint(1, 50),
            reason=random.choice(["Restock", "Relocation", "Order Fulfillment"]),
            timestamp=random_timestamp(past_days=60, future_days=00)
        )
        db.add(movement)
    db.commit()
    # Inventory Adjustments
    for _ in range(20):  # Create 20 inventory adjustments
        product = random.choice(products)
        location = random.choice(locations)
        adjustment = InventoryAdjustment(
            product_id=product.id,
            location_id=location.id,
            quantity_change=random.randint(-10, 10),
            reason=random.choice(["Damage", "Theft", "Found", "Miscounted"])
        )
        db.add(adjustment)
    db.commit()
    # Role Permissions
    for role in [admin_role, user_role, manager_role]:
        for permission in permissions:
            if role == admin_role or (role == manager_role and permission.permission_name != "manage_users"):
                role_permission = RolePermission(role_id=role.id, permission_id=permission.id)
                db.add(role_permission)
    db.commit()
    # Location Inventory
    for location in locations:
        for product in random.sample(products, k=random.randint(1, len(products))):
            location_inventory = LocationInventory(
                location_id=location.id,
                product_id=product.id,
                quantity=random.randint(0, 100)
            )
            db.add(location_inventory)

        # Commit all changes
    db.commit()
    db.close()


if __name__ == "__main__":
    add_sample_data()
    print("Sample data added successfully!")

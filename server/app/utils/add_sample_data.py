import random
from datetime import datetime, timedelta

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from server.app.core.config import settings
from server.app.core.security import get_password_hash
from server.app.models import ProductCategory, Product, Location
from server.app.models.asset import Asset, AssetMaintenance
from server.app.models.base import Base
from server.app.models.inventory import Inventory, Zone
from server.app.models.order import Order, OrderItem, Customer, PurchaseOrder, POItem, Supplier
from server.app.models.quality import QualityCheck
from server.app.models.task import Task
from server.app.models.user import User, Role, Permission
from server.app.models.warehouse import PickList, Carrier
from server.app.models.yard_location import YardLocation, DockAppointment

# Establish the database connection
engine = sa.create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in the database
Base.metadata.create_all(bind=engine)


def add_sample_data():
    db = SessionLocal()

    # Roles and Permissions
    admin_role = Role(role_name="Admin")
    user_role = Role(role_name="User")
    db.add_all([admin_role, user_role])

    permissions = [
        Permission(permission_name="create_order"),
        Permission(permission_name="update_inventory"),
        Permission(permission_name="manage_users"),
    ]
    db.add_all(permissions)

    # Users
    admin_user = User(
        username="admin",
        email="admin@gmail.com",
        password_hash=get_password_hash("admin"),
        role_id=admin_role.role_id
    )
    regular_user = User(
        username="user",
        email="user@gmail.com",
        password_hash=get_password_hash("user"),
        role_id=user_role.role_id
    )
    db.add_all([admin_user, regular_user])

    # Product Categories
    categories = [
        ProductCategory(name="Electronics"),
        ProductCategory(name="Clothing"),
        ProductCategory(name="Home & Garden"),
    ]
    db.add_all(categories)

    # Products
    products = [
        Product(sku="SKU001", name="Smartphone", category_id=categories[0].category_id, price=599.99),
        Product(sku="SKU002", name="T-shirt", category_id=categories[1].category_id, price=19.99),
        Product(sku="SKU003", name="Garden Hose", category_id=categories[2].category_id, price=29.99),
    ]
    db.add_all(products)

    # Zones and Locations
    zone = Zone(name="Main Warehouse")
    db.add(zone)

    locations = [
        Location(zone=zone, aisle="A", rack="1", shelf="1"),
        Location(zone=zone, aisle="B", rack="1", shelf="1"),
        Location(zone=zone, aisle="C", rack="1", shelf="1"),
    ]
    db.add_all(locations)

    # Inventory
    for product, location in zip(products, locations):
        inventory = Inventory(product=product, location=location, quantity=100)
        db.add(inventory)

    # Customers
    customers = [
        Customer(name="John Doe", email="john@example.com"),
        Customer(name="Jane Smith", email="jane@example.com"),
    ]
    db.add_all(customers)

    # Orders
    for customer in customers:
        order = Order(customer=customer, status="Pending", total_amount=0)
        for product in random.sample(products, 2):
            quantity = random.randint(1, 5)
            OrderItem(order=order, product=product, quantity=quantity, unit_price=product.price)
            order.total_amount += quantity * product.price
        db.add(order)

    # Suppliers
    suppliers = [
        Supplier(name="Acme Corp", email="acme@example.com"),
        Supplier(name="XYZ Distributors", email="xyz@example.com"),
    ]
    db.add_all(suppliers)

    # Purchase Orders
    for supplier in suppliers:
        po = PurchaseOrder(supplier=supplier, status="Pending")
        for product in random.sample(products, 2):
            quantity = random.randint(10, 50)
            POItem(purchase_order=po, product=product, quantity=quantity, unit_price=product.price * 0.7)
        db.add(po)

    # Assets
    assets = [
        Asset(asset_type="Forklift", asset_name="Forklift 1", serial_number="FL001",
              purchase_date=datetime.now().date(), status="Active"),
        Asset(asset_type="Pallet Jack", asset_name="Pallet Jack 1", serial_number="PJ001",
              purchase_date=datetime.now().date(), status="Active"),
    ]
    db.add_all(assets)

    # Asset Maintenance
    for asset in assets:
        maintenance = AssetMaintenance(
            asset=asset,
            maintenance_type="Routine Check",
            scheduled_date=datetime.now().date() + timedelta(days=30),
            performed_by=admin_user.user_id
        )
        db.add(maintenance)

    # Quality Checks
    for product in products:
        check = QualityCheck(
            product=product,
            performed_by=admin_user.user_id,
            result="Pass",
            notes="Routine quality check"
        )
        db.add(check)

    # Tasks
    task = Task(
        task_type="Inventory Count",
        description="Perform inventory count in Aisle A",
        assigned_to=regular_user.user_id,
        due_date=datetime.now() + timedelta(days=7),
        priority="High",
        status="Pending"
    )
    db.add(task)

    # Warehouse Operations
    pick_list = PickList(order_id=1, status="In Progress")
    db.add(pick_list)

    carrier = Carrier(name="Fast Shipping", contact_info="contact@fastshipping.com")
    db.add(carrier)

    # Yard Management
    yard_location = YardLocation(name="Dock 1", type="Loading", status="Available")
    db.add(yard_location)

    appointment = DockAppointment(
        yard_location=yard_location,
        appointment_time=datetime.now() + timedelta(days=1),
        carrier=carrier,
        type="Inbound",
        status="Scheduled"
    )
    db.add(appointment)

    # Commit all changes
    db.commit()
    db.close()


if __name__ == "__main__":
    add_sample_data()
    print("Sample data added successfully!")

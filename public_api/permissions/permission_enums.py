from enum import Enum


class PermissionType(str, Enum):
    READ = "read"
    WRITE = "write"
    EDIT = "edit"
    DELETE = "delete"


class PermissionName(str, Enum):
    ASSET = "Asset"
    ASSET_MAINTENANCE = "Asset Maintenance"
    AUDIT_LOGS = "Audit Logs"
    DASHBOARD = "Dashboard"
    INVENTORY = "Inventory"
    ORDERS = "Orders"
    PRODUCTS = "Products"
    SUPPLIERS = "Suppliers"
    CUSTOMERS = "Customers"
    SHIPMENTS = "Shipments"
    REPORTS = "Reports"
    USER_MANAGEMENT = "User Management"
    SETTINGS = "Settings"
    NOTIFICATIONS = "Notifications"
    TASKS_MANAGEMENT = "Tasks Management"
    ADVANCED_SEARCH = "Advanced Search"
    SIMULATION = "Simulation"

"""Initial migration

Revision ID: bdc371f2e628
Revises: 
Create Date: 2024-08-08 00:48:15.531737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bdc371f2e628'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('assets',
    sa.Column('asset_id', sa.Integer(), nullable=False),
    sa.Column('asset_type', sa.String(length=50), nullable=True),
    sa.Column('asset_name', sa.String(length=100), nullable=True),
    sa.Column('serial_number', sa.String(length=50), nullable=True),
    sa.Column('purchase_date', sa.Date(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('asset_id')
    )
    op.create_index(op.f('ix_assets_asset_id'), 'assets', ['asset_id'], unique=False)
    op.create_table('carriers',
    sa.Column('carrier_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('contact_info', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('carrier_id')
    )
    op.create_index(op.f('ix_carriers_carrier_id'), 'carriers', ['carrier_id'], unique=False)
    op.create_table('customers',
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('address', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('customer_id')
    )
    op.create_index(op.f('ix_customers_customer_id'), 'customers', ['customer_id'], unique=False)
    op.create_table('permissions',
    sa.Column('permission_id', sa.Integer(), nullable=False),
    sa.Column('permission_name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('permission_id'),
    sa.UniqueConstraint('permission_name')
    )
    op.create_index(op.f('ix_permissions_permission_id'), 'permissions', ['permission_id'], unique=False)
    op.create_table('product_categories',
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('parent_category_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_category_id'], ['product_categories.category_id'], ),
    sa.PrimaryKeyConstraint('category_id')
    )
    op.create_index(op.f('ix_product_categories_category_id'), 'product_categories', ['category_id'], unique=False)
    op.create_table('roles',
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('role_name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('role_id'),
    sa.UniqueConstraint('role_name')
    )
    op.create_index(op.f('ix_roles_role_id'), 'roles', ['role_id'], unique=False)
    op.create_table('suppliers',
    sa.Column('supplier_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('contact_person', sa.String(length=100), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('address', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('supplier_id')
    )
    op.create_index(op.f('ix_suppliers_supplier_id'), 'suppliers', ['supplier_id'], unique=False)
    op.create_table('yard_locations',
    sa.Column('yard_location_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('type', sa.String(length=20), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('yard_location_id')
    )
    op.create_index(op.f('ix_yard_locations_yard_location_id'), 'yard_locations', ['yard_location_id'], unique=False)
    op.create_table('zones',
    sa.Column('zone_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('zone_id')
    )
    op.create_index(op.f('ix_zones_zone_id'), 'zones', ['zone_id'], unique=False)
    op.create_table('dock_appointments',
    sa.Column('appointment_id', sa.Integer(), nullable=False),
    sa.Column('yard_location_id', sa.Integer(), nullable=True),
    sa.Column('appointment_time', sa.DateTime(), nullable=True),
    sa.Column('carrier_id', sa.Integer(), nullable=True),
    sa.Column('type', sa.String(length=20), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['carrier_id'], ['carriers.carrier_id'], ),
    sa.ForeignKeyConstraint(['yard_location_id'], ['yard_locations.yard_location_id'], ),
    sa.PrimaryKeyConstraint('appointment_id')
    )
    op.create_index(op.f('ix_dock_appointments_appointment_id'), 'dock_appointments', ['appointment_id'], unique=False)
    op.create_table('locations',
    sa.Column('location_id', sa.Integer(), nullable=False),
    sa.Column('zone_id', sa.Integer(), nullable=True),
    sa.Column('aisle', sa.String(length=10), nullable=True),
    sa.Column('rack', sa.String(length=10), nullable=True),
    sa.Column('shelf', sa.String(length=10), nullable=True),
    sa.Column('bin', sa.String(length=10), nullable=True),
    sa.ForeignKeyConstraint(['zone_id'], ['zones.zone_id'], ),
    sa.PrimaryKeyConstraint('location_id')
    )
    op.create_index(op.f('ix_locations_location_id'), 'locations', ['location_id'], unique=False)
    op.create_table('orders',
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=True),
    sa.Column('order_date', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('total_amount', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.customer_id'], ),
    sa.PrimaryKeyConstraint('order_id')
    )
    op.create_index(op.f('ix_orders_order_id'), 'orders', ['order_id'], unique=False)
    op.create_table('products',
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('sku', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('unit_of_measure', sa.String(length=20), nullable=True),
    sa.Column('weight', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('dimensions', sa.String(length=50), nullable=True),
    sa.Column('barcode', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['product_categories.category_id'], ),
    sa.PrimaryKeyConstraint('product_id'),
    sa.UniqueConstraint('sku')
    )
    op.create_index(op.f('ix_products_product_id'), 'products', ['product_id'], unique=False)
    op.create_table('purchase_orders',
    sa.Column('po_id', sa.Integer(), nullable=False),
    sa.Column('supplier_id', sa.Integer(), nullable=True),
    sa.Column('order_date', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('expected_delivery_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.supplier_id'], ),
    sa.PrimaryKeyConstraint('po_id')
    )
    op.create_index(op.f('ix_purchase_orders_po_id'), 'purchase_orders', ['po_id'], unique=False)
    op.create_table('role_permissions',
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('permission_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['permission_id'], ['permissions.permission_id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['roles.role_id'], ),
    sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )
    op.create_table('users',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('last_login', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['roles.role_id'], ),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=False)
    op.create_table('asset_maintenance',
    sa.Column('maintenance_id', sa.Integer(), nullable=False),
    sa.Column('asset_id', sa.Integer(), nullable=True),
    sa.Column('maintenance_type', sa.String(length=50), nullable=True),
    sa.Column('scheduled_date', sa.Date(), nullable=True),
    sa.Column('completed_date', sa.Date(), nullable=True),
    sa.Column('performed_by', sa.Integer(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['asset_id'], ['assets.asset_id'], ),
    sa.ForeignKeyConstraint(['performed_by'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('maintenance_id')
    )
    op.create_index(op.f('ix_asset_maintenance_maintenance_id'), 'asset_maintenance', ['maintenance_id'], unique=False)
    op.create_table('audit_log',
    sa.Column('log_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('action_type', sa.String(length=50), nullable=True),
    sa.Column('table_name', sa.String(length=50), nullable=True),
    sa.Column('record_id', sa.Integer(), nullable=True),
    sa.Column('old_value', sa.Text(), nullable=True),
    sa.Column('new_value', sa.Text(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('log_id')
    )
    op.create_index(op.f('ix_audit_log_log_id'), 'audit_log', ['log_id'], unique=False)
    op.create_table('inventory',
    sa.Column('inventory_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('location_id', sa.Integer(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('last_updated', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['location_id'], ['locations.location_id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], ),
    sa.PrimaryKeyConstraint('inventory_id')
    )
    op.create_index(op.f('ix_inventory_inventory_id'), 'inventory', ['inventory_id'], unique=False)
    op.create_table('order_items',
    sa.Column('order_item_id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('unit_price', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['orders.order_id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], ),
    sa.PrimaryKeyConstraint('order_item_id')
    )
    op.create_index(op.f('ix_order_items_order_item_id'), 'order_items', ['order_item_id'], unique=False)
    op.create_table('pick_lists',
    sa.Column('pick_list_id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['orders.order_id'], ),
    sa.PrimaryKeyConstraint('pick_list_id')
    )
    op.create_index(op.f('ix_pick_lists_pick_list_id'), 'pick_lists', ['pick_list_id'], unique=False)
    op.create_table('po_items',
    sa.Column('po_item_id', sa.Integer(), nullable=False),
    sa.Column('po_id', sa.Integer(), nullable=True),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('unit_price', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.ForeignKeyConstraint(['po_id'], ['purchase_orders.po_id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], ),
    sa.PrimaryKeyConstraint('po_item_id')
    )
    op.create_index(op.f('ix_po_items_po_item_id'), 'po_items', ['po_item_id'], unique=False)
    op.create_table('quality_checks',
    sa.Column('check_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('check_date', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('performed_by', sa.Integer(), nullable=True),
    sa.Column('result', sa.String(length=20), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['performed_by'], ['users.user_id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], ),
    sa.PrimaryKeyConstraint('check_id')
    )
    op.create_index(op.f('ix_quality_checks_check_id'), 'quality_checks', ['check_id'], unique=False)
    op.create_table('receipts',
    sa.Column('receipt_id', sa.Integer(), nullable=False),
    sa.Column('po_id', sa.Integer(), nullable=True),
    sa.Column('received_date', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['po_id'], ['purchase_orders.po_id'], ),
    sa.PrimaryKeyConstraint('receipt_id')
    )
    op.create_index(op.f('ix_receipts_receipt_id'), 'receipts', ['receipt_id'], unique=False)
    op.create_table('shipments',
    sa.Column('shipment_id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('carrier_id', sa.Integer(), nullable=True),
    sa.Column('tracking_number', sa.String(length=50), nullable=True),
    sa.Column('ship_date', sa.DateTime(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['carrier_id'], ['carriers.carrier_id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['orders.order_id'], ),
    sa.PrimaryKeyConstraint('shipment_id')
    )
    op.create_index(op.f('ix_shipments_shipment_id'), 'shipments', ['shipment_id'], unique=False)
    op.create_table('tasks',
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('task_type', sa.String(length=50), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('assigned_to', sa.Integer(), nullable=True),
    sa.Column('due_date', sa.DateTime(), nullable=True),
    sa.Column('priority', sa.String(length=20), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['assigned_to'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('task_id')
    )
    op.create_index(op.f('ix_tasks_task_id'), 'tasks', ['task_id'], unique=False)
    op.create_table('pick_list_items',
    sa.Column('pick_list_item_id', sa.Integer(), nullable=False),
    sa.Column('pick_list_id', sa.Integer(), nullable=True),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('location_id', sa.Integer(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('picked_quantity', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['location_id'], ['locations.location_id'], ),
    sa.ForeignKeyConstraint(['pick_list_id'], ['pick_lists.pick_list_id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], ),
    sa.PrimaryKeyConstraint('pick_list_item_id')
    )
    op.create_index(op.f('ix_pick_list_items_pick_list_item_id'), 'pick_list_items', ['pick_list_item_id'], unique=False)
    op.create_table('receipt_items',
    sa.Column('receipt_item_id', sa.Integer(), nullable=False),
    sa.Column('receipt_id', sa.Integer(), nullable=True),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('quantity_received', sa.Integer(), nullable=True),
    sa.Column('location_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['location_id'], ['locations.location_id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], ),
    sa.ForeignKeyConstraint(['receipt_id'], ['receipts.receipt_id'], ),
    sa.PrimaryKeyConstraint('receipt_item_id')
    )
    op.create_index(op.f('ix_receipt_items_receipt_item_id'), 'receipt_items', ['receipt_item_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_receipt_items_receipt_item_id'), table_name='receipt_items')
    op.drop_table('receipt_items')
    op.drop_index(op.f('ix_pick_list_items_pick_list_item_id'), table_name='pick_list_items')
    op.drop_table('pick_list_items')
    op.drop_index(op.f('ix_tasks_task_id'), table_name='tasks')
    op.drop_table('tasks')
    op.drop_index(op.f('ix_shipments_shipment_id'), table_name='shipments')
    op.drop_table('shipments')
    op.drop_index(op.f('ix_receipts_receipt_id'), table_name='receipts')
    op.drop_table('receipts')
    op.drop_index(op.f('ix_quality_checks_check_id'), table_name='quality_checks')
    op.drop_table('quality_checks')
    op.drop_index(op.f('ix_po_items_po_item_id'), table_name='po_items')
    op.drop_table('po_items')
    op.drop_index(op.f('ix_pick_lists_pick_list_id'), table_name='pick_lists')
    op.drop_table('pick_lists')
    op.drop_index(op.f('ix_order_items_order_item_id'), table_name='order_items')
    op.drop_table('order_items')
    op.drop_index(op.f('ix_inventory_inventory_id'), table_name='inventory')
    op.drop_table('inventory')
    op.drop_index(op.f('ix_audit_log_log_id'), table_name='audit_log')
    op.drop_table('audit_log')
    op.drop_index(op.f('ix_asset_maintenance_maintenance_id'), table_name='asset_maintenance')
    op.drop_table('asset_maintenance')
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    op.drop_table('users')
    op.drop_table('role_permissions')
    op.drop_index(op.f('ix_purchase_orders_po_id'), table_name='purchase_orders')
    op.drop_table('purchase_orders')
    op.drop_index(op.f('ix_products_product_id'), table_name='products')
    op.drop_table('products')
    op.drop_index(op.f('ix_orders_order_id'), table_name='orders')
    op.drop_table('orders')
    op.drop_index(op.f('ix_locations_location_id'), table_name='locations')
    op.drop_table('locations')
    op.drop_index(op.f('ix_dock_appointments_appointment_id'), table_name='dock_appointments')
    op.drop_table('dock_appointments')
    op.drop_index(op.f('ix_zones_zone_id'), table_name='zones')
    op.drop_table('zones')
    op.drop_index(op.f('ix_yard_locations_yard_location_id'), table_name='yard_locations')
    op.drop_table('yard_locations')
    op.drop_index(op.f('ix_suppliers_supplier_id'), table_name='suppliers')
    op.drop_table('suppliers')
    op.drop_index(op.f('ix_roles_role_id'), table_name='roles')
    op.drop_table('roles')
    op.drop_index(op.f('ix_product_categories_category_id'), table_name='product_categories')
    op.drop_table('product_categories')
    op.drop_index(op.f('ix_permissions_permission_id'), table_name='permissions')
    op.drop_table('permissions')
    op.drop_index(op.f('ix_customers_customer_id'), table_name='customers')
    op.drop_table('customers')
    op.drop_index(op.f('ix_carriers_carrier_id'), table_name='carriers')
    op.drop_table('carriers')
    op.drop_index(op.f('ix_assets_asset_id'), table_name='assets')
    op.drop_table('assets')
    # ### end Alembic commands ###

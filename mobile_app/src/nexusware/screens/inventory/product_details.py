# src/nexusware/screens/inventory/product_details.py
import asyncio
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from ..base import BaseScreen
from public_api.api.inventory import InventoryAPI
from public_api.shared_schemas import (
    InventoryUpdate, InventoryTransfer, InventoryAdjustment,
    ProductWithCategoryAndInventory
)


class ProductDetailsScreen(BaseScreen):
    def __init__(self, product_id: int):
        super().__init__()
        self.inventory_api = InventoryAPI(self.window.app.api_client)
        self.product_id = product_id
        self.product: ProductWithCategoryAndInventory | None = None
        self.inventory_movements = []
        self.setup_product_screen()

    async def setup_product_screen(self):
        """Initialize product screen with data"""
        try:
            # Load product details and inventory data
            self.product = await asyncio.to_thread(
                self.inventory_api.get_inventory_item,
                self.product_id
            )
            self.inventory_movements = await asyncio.to_thread(
                self.inventory_api.get_inventory_movement_history,
                self.product_id
            )
            self.render_product_details()
        except Exception as e:
            self.show_error(str(e))

    def render_product_details(self):
        main_box = toga.Box(style=Pack(
            direction=ROW,
            padding=20,
            flex=1
        ))

        # Left panel - Product details
        details_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=(0, 20, 0, 0),
            flex=1
        ))

        # Header with actions
        header_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 0, 20, 0)
        ))

        title = toga.Label(
            f'{self.product.name}',
            style=Pack(
                font_size=24,
                font_weight='bold',
                flex=1
            )
        )
        header_box.add(title)

        edit_btn = toga.Button(
            'Edit',
            on_press=self.show_edit_dialog,
            style=Pack(padding=(5, 10))
        )
        header_box.add(edit_btn)

        details_box.add(header_box)

        # Product info
        fields = [
            ('SKU', self.product.sku),
            ('Category', self.product.category.name if self.product.category else 'N/A'),
            ('Description', self.product.description or 'N/A'),
            ('Barcode', self.product.barcode or 'N/A'),
            ('Unit of Measure', self.product.unit_of_measure or 'N/A'),
            ('Weight', f'{self.product.weight} kg' if self.product.weight else 'N/A'),
            ('Dimensions', self.product.dimensions or 'N/A'),
            ('Price', f'${self.product.price:.2f}'),
        ]

        for label, value in fields:
            field_box = toga.Box(style=Pack(
                direction=ROW,
                padding=(0, 0, 10, 0)
            ))

            field_box.add(toga.Label(
                f'{label}:',
                style=Pack(width=150, font_weight='bold')
            ))
            field_box.add(toga.Label(str(value)))

            details_box.add(field_box)

        main_box.add(details_box)

        # Right panel - Inventory and movements
        inventory_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=(0, 0, 0, 20),
            flex=1
        ))

        # Current inventory
        inventory_label = toga.Label(
            'Current Inventory',
            style=Pack(
                font_size=18,
                font_weight='bold',
                padding=(0, 0, 10, 0)
            )
        )
        inventory_box.add(inventory_label)

        self.inventory_table = toga.Table(
            headings=['Location', 'Quantity', 'Last Updated'],
            style=Pack(flex=1)
        )

        inventory_data = [
            [item.location.name, str(item.quantity), self.format_date(item.last_updated)]
            for item in self.product.inventory_items
        ]
        self.inventory_table.data = inventory_data

        inventory_box.add(self.inventory_table)

        # Add/Adjust inventory buttons
        actions = toga.Box(style=Pack(
            direction=ROW,
            padding=(10, 0)
        ))

        add_btn = toga.Button(
            'Add Inventory',
            on_press=self.show_add_inventory_dialog,
            style=Pack(padding=(5, 10))
        )
        actions.add(add_btn)

        adjust_btn = toga.Button(
            'Adjust Quantity',
            on_press=self.show_adjust_dialog,
            style=Pack(padding=(5, 10))
        )
        actions.add(adjust_btn)

        transfer_btn = toga.Button(
            'Transfer',
            on_press=self.show_transfer_dialog,
            style=Pack(padding=(5, 10))
        )
        actions.add(transfer_btn)

        inventory_box.add(actions)

        # Movement history
        movements_label = toga.Label(
            'Movement History',
            style=Pack(
                font_size=18,
                font_weight='bold',
                padding=(20, 0, 10, 0)
            )
        )
        inventory_box.add(movements_label)

        self.movements_table = toga.Table(
            headings=['Date', 'From', 'To', 'Quantity', 'Reason'],
            style=Pack(flex=1)
        )

        movement_data = [
            [
                self.format_date(mov.timestamp),
                self.get_location_name(mov.from_location_id),
                self.get_location_name(mov.to_location_id),
                str(mov.quantity),
                mov.reason
            ]
            for mov in self.inventory_movements
        ]
        self.movements_table.data = movement_data

        inventory_box.add(self.movements_table)

        main_box.add(inventory_box)
        self.content.add(main_box)

    def get_location_name(self, location_id):
        # Find location name from inventory items
        for item in self.product.inventory_items:
            if item.location.id == location_id:
                return item.location.name
        return 'External'

    async def show_add_inventory_dialog(self, widget):
        """Show dialog for adding inventory"""
        form = self.create_inventory_form()
        confirm_dialog = toga.ConfirmDialog(
            title='Add Inventory',
            message='Are you sure you want to add this inventory?'
        )

        if await self.window.app.dialog(confirm_dialog):
            try:
                location_name = form.location_select.value
                quantity = int(form.quantity_input.value)

                location = next(
                    item.location for item in self.product.inventory_items
                    if item.location.name == location_name
                )

                inventory_update = InventoryUpdate(
                    product_id=self.product_id,
                    location_id=location.id,
                    quantity=quantity
                )

                await asyncio.to_thread(
                    self.inventory_api.update_inventory,
                    self.product_id,
                    inventory_update
                )

                success_dialog = toga.InfoDialog(
                    title='Success',
                    message='Inventory updated successfully'
                )
                await self.window.app.dialog(success_dialog)
                await self.setup_product_screen()

            except Exception as e:
                error_dialog = toga.ErrorDialog(
                    title='Error',
                    message=str(e)
                )
                await self.window.app.dialog(error_dialog)

    def create_inventory_form(self):
        """Create form box for inventory operations"""
        class FormBox:
            def __init__(self):
                self.box = toga.Box(style=Pack(
                    direction=COLUMN,
                    padding=10
                ))

                # Location selector
                location_box = toga.Box(style=Pack(direction=ROW))
                location_box.add(toga.Label('Location:'))
                self.location_select = toga.Selection(items=[
                    item.location.name for item in self.product.inventory_items
                ])
                location_box.add(self.location_select)
                self.box.add(location_box)

                # Quantity input
                quantity_box = toga.Box(style=Pack(direction=ROW))
                quantity_box.add(toga.Label('Quantity:'))
                self.quantity_input = toga.NumberInput(min=0)
                quantity_box.add(self.quantity_input)
                self.box.add(quantity_box)

                # Reason input
                reason_box = toga.Box(style=Pack(direction=ROW))
                reason_box.add(toga.Label('Reason:'))
                self.reason_input = toga.TextInput()
                reason_box.add(self.reason_input)
                self.box.add(reason_box)

        return FormBox()



    async def handle_add_inventory(self, dialog, result):
        """Handle add inventory dialog result"""
        if result:
            try:
                location_name = self.location_select.value
                quantity = int(self.quantity_input.value)

                location = next(
                    item.location for item in self.product.inventory_items
                    if item.location.name == location_name
                )

                inventory_update = InventoryUpdate(
                    product_id=self.product_id,
                    location_id=location.id,
                    quantity=quantity
                )

                await asyncio.to_thread(
                    self.inventory_api.update_inventory,
                    self.product_id,
                    inventory_update
                )

                self.show_success("Inventory updated successfully")
                await self.setup_product_screen()

            except Exception as e:
                self.show_error(str(e))

    async def show_adjust_dialog(self, widget):
        """Show dialog for adjusting inventory"""
        form = self.create_inventory_form()
        confirm_dialog = toga.ConfirmDialog(
            title='Adjust Inventory',
            message='Are you sure you want to adjust this inventory?'
        )

        if await self.window.app.dialog(confirm_dialog):
            try:
                location_name = form.location_select.value
                quantity_change = int(form.quantity_input.value)
                reason = form.reason_input.value

                location = next(
                    item.location for item in self.product.inventory_items
                    if item.location.name == location_name
                )

                adjustment = InventoryAdjustment(
                    product_id=self.product_id,
                    location_id=location.id,
                    quantity_change=quantity_change,
                    reason=reason,
                    timestamp=0  # Server will set this
                )

                await asyncio.to_thread(
                    self.inventory_api.adjust_inventory,
                    self.product_id,
                    adjustment
                )

                success_dialog = toga.InfoDialog(
                    title='Success',
                    message='Inventory adjusted successfully'
                )
                await self.window.app.dialog(success_dialog)
                await self.setup_product_screen()

            except Exception as e:
                error_dialog = toga.ErrorDialog(
                    title='Error',
                    message=str(e)
                )
                await self.window.app.dialog(error_dialog)

    async def handle_adjust_inventory(self, dialog, result):
        """Handle adjust inventory dialog result"""
        if result:
            try:
                location_name = self.location_select.value
                quantity_change = int(self.quantity_input.value)
                reason = self.reason_input.value

                location = next(
                    item.location for item in self.product.inventory_items
                    if item.location.name == location_name
                )

                adjustment = InventoryAdjustment(
                    product_id=self.product_id,
                    location_id=location.id,
                    quantity_change=quantity_change,
                    reason=reason,
                    timestamp=0  # Server will set this
                )

                await asyncio.to_thread(
                    self.inventory_api.adjust_inventory,
                    self.product_id,
                    adjustment
                )

                self.show_success("Inventory adjusted successfully")
                await self.setup_product_screen()

            except Exception as e:
                self.show_error(str(e))

    async def show_transfer_dialog(self, widget):
        """Show dialog for transferring inventory"""
        form = self.create_transfer_form()
        confirm_dialog = toga.ConfirmDialog(
            title='Transfer Inventory',
            message='Are you sure you want to transfer this inventory?'
        )

        if await self.window.app.dialog(confirm_dialog):
            try:
                from_location_name = form.from_location_select.value
                to_location_name = form.to_location_select.value
                quantity = int(form.transfer_quantity_input.value)

                if from_location_name == to_location_name:
                    error_dialog = toga.ErrorDialog(
                        title='Error',
                        message='Cannot transfer to the same location'
                    )
                    await self.window.app.dialog(error_dialog)
                    return

                from_location = next(
                    item.location for item in self.product.inventory_items
                    if item.location.name == from_location_name
                )
                to_location = next(
                    item.location for item in self.product.inventory_items
                    if item.location.name == to_location_name
                )

                transfer = InventoryTransfer(
                    from_location_id=from_location.id,
                    to_location_id=to_location.id,
                    quantity=quantity
                )

                await asyncio.to_thread(
                    self.inventory_api.transfer_inventory,
                    transfer
                )

                success_dialog = toga.InfoDialog(
                    title='Success',
                    message='Inventory transferred successfully'
                )
                await self.window.app.dialog(success_dialog)
                await self.setup_product_screen()

            except Exception as e:
                error_dialog = toga.ErrorDialog(
                    title='Error',
                    message=str(e)
                )
                await self.window.app.dialog(error_dialog)

    def create_transfer_form(self):
        """Create form box for transfer operations"""
        class TransferFormBox:
            def __init__(self):
                self.box = toga.Box(style=Pack(
                    direction=COLUMN,
                    padding=10
                ))

                # From location selector
                from_box = toga.Box(style=Pack(direction=ROW))
                from_box.add(toga.Label('From Location:'))
                self.from_location_select = toga.Selection(items=[
                    item.location.name for item in self.product.inventory_items
                ])
                from_box.add(self.from_location_select)
                self.box.add(from_box)

                # To location selector
                to_box = toga.Box(style=Pack(direction=ROW))
                to_box.add(toga.Label('To Location:'))
                self.to_location_select = toga.Selection(items=[
                    item.location.name for item in self.product.inventory_items
                ])
                to_box.add(self.to_location_select)
                self.box.add(to_box)

                # Quantity input
                quantity_box = toga.Box(style=Pack(direction=ROW))
                quantity_box.add(toga.Label('Quantity:'))
                self.transfer_quantity_input = toga.NumberInput(min=0)
                quantity_box.add(self.transfer_quantity_input)
                self.box.add(quantity_box)

        return TransferFormBox()

    async def handle_transfer_inventory(self, dialog, result):
        """Handle transfer inventory dialog result"""
        if result:
            try:
                from_location_name = self.from_location_select.value
                to_location_name = self.to_location_select.value
                quantity = int(self.transfer_quantity_input.value)

                from_location = next(
                    item.location for item in self.product.inventory_items
                    if item.location.name == from_location_name
                )
                to_location = next(
                    item.location for item in self.product.inventory_items
                    if item.location.name == to_location_name
                )

                transfer = InventoryTransfer(
                    from_location_id=from_location.id,
                    to_location_id=to_location.id,
                    quantity=quantity
                )

                await asyncio.to_thread(
                    self.inventory_api.transfer_inventory,
                    transfer
                )

                self.show_success("Inventory transferred successfully")
                await self.setup_product_screen()

            except Exception as e:
                self.show_error(str(e))

    def show_edit_dialog(self, widget):
        """Navigate to product edit screen"""
        self.window.app.navigate_to(
            'product_edit',
            product_id=self.product_id
        )
# src/nexusware/screens/inventory/stock_count.py
import asyncio

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from public_api.api.inventory import InventoryAPI
from public_api.shared_schemas import (
    StocktakeCreate, StocktakeItem, Location, StocktakeResult
)
from ..base import BaseScreen


class StockCountScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.inventory_api = InventoryAPI(self.window.app.api_client)
        self.location: Location | None = None
        self.counted_items: list[StocktakeItem] = []
        self.setup_stock_count_screen()

    def setup_stock_count_screen(self):
        main_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=20,
            flex=1
        ))

        # Header
        header_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 0, 20, 0)
        ))

        title = toga.Label(
            'Stock Count',
            style=Pack(
                font_size=24,
                font_weight='bold',
                flex=1
            )
        )
        header_box.add(title)

        new_count_btn = toga.Button(
            'New Count',
            on_press=self.start_new_count,
            style=Pack(
                padding=(5, 10),
                background_color=self.theme['button_background']
            )
        )
        header_box.add(new_count_btn)

        main_box.add(header_box)

        # Location selection
        location_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 0, 10, 0)
        ))

        location_label = toga.Label(
            'Location:',
            style=Pack(
                padding=(0, 10, 0, 0),
                width=100
            )
        )
        location_box.add(location_label)

        self.location_select = toga.Selection(
            on_select=self.on_location_select,
            style=Pack(flex=1)
        )
        location_box.add(self.location_select)

        main_box.add(location_box)

        # Count area
        count_box = toga.Box(style=Pack(
            direction=COLUMN,
            flex=1
        ))

        # Items table
        self.items_table = toga.Table(
            headings=['SKU', 'Product', 'Expected', 'Counted', 'Variance'],
            on_select=self.on_select_item,
            style=Pack(flex=1)
        )
        count_box.add(self.items_table)

        # Count input area
        input_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(10, 0)
        ))

        self.sku_input = toga.TextInput(
            placeholder='Scan or enter SKU',
            style=Pack(
                padding=(0, 10, 0, 0),
                flex=1
            )
        )
        input_box.add(self.sku_input)

        self.quantity_input = toga.NumberInput(
            min_value=0,
            style=Pack(
                padding=(0, 10, 0, 0),
                width=100
            )
        )
        input_box.add(self.quantity_input)

        add_btn = toga.Button(
            'Add Count',
            on_press=self.add_count,
            style=Pack(
                padding=(5, 10),
                background_color=self.theme['button_background']
            )
        )
        input_box.add(add_btn)

        count_box.add(input_box)

        # Actions
        actions_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(10, 0)
        ))

        self.scan_btn = toga.Button(
            'Scan Barcode',
            on_press=self.open_scanner,
            style=Pack(padding=(5, 10))
        )
        actions_box.add(self.scan_btn)

        self.complete_btn = toga.Button(
            'Complete Count',
            on_press=self.complete_count,
            style=Pack(
                padding=(5, 10),
                background_color=self.theme['success']
            )
        )
        actions_box.add(self.complete_btn)

        count_box.add(actions_box)
        main_box.add(count_box)

        # Results area
        self.results_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=(10, 0),
            display='none'
        ))

        results_title = toga.Label(
            'Count Results',
            style=Pack(
                font_size=18,
                font_weight='bold',
                padding=(0, 0, 10, 0)
            )
        )
        self.results_box.add(results_title)

        self.results_table = toga.Table(
            headings=['Product', 'Expected', 'Counted', 'Variance', 'Status'],
            style=Pack(flex=1)
        )
        self.results_box.add(self.results_table)

        main_box.add(self.results_box)
        self.content.add(main_box)

        # Load locations
        self.load_locations()

    async def load_locations(self):
        """Load available locations into selector"""
        try:
            locations = await asyncio.to_thread(
                self.inventory_api.get_product_locations,
                product_id=None  # Get all locations
            )
            self.location_select.items = [loc.name for loc in locations]
        except Exception as e:
            error_dialog = toga.ErrorDialog(
                title='Error',
                message=f"Failed to load locations: {str(e)}"
            )
            await self.window.app.dialog(error_dialog)

    async def on_location_select(self, widget):
        """Handle location selection change"""
        if not widget.value:
            return

        try:
            locations = await asyncio.to_thread(
                self.inventory_api.get_product_locations,
                product_id=None
            )
            self.location = next(
                loc for loc in locations
                if loc.name == widget.value
            )
            await self.load_location_inventory()
        except Exception as e:
            error_dialog = toga.ErrorDialog(
                title='Error',
                message=f"Failed to load location inventory: {str(e)}"
            )
            await self.window.app.dialog(error_dialog)

    async def load_location_inventory(self):
        """Load inventory for selected location"""
        try:
            inventory_filter = {"location_id": self.location.id}
            inventory_list = await asyncio.to_thread(
                self.inventory_api.get_inventory,
                inventory_filter=inventory_filter
            )
            self.update_items_table(inventory_list.items)
        except Exception as e:
            error_dialog = toga.ErrorDialog(
                title='Error',
                message=f"Failed to load inventory: {str(e)}"
            )
            await self.window.app.dialog(error_dialog)

    def update_items_table(self, inventory_items):
        """Update the items table with current inventory"""
        data = []
        for item in inventory_items:
            counted = next(
                (count.counted_quantity for count in self.counted_items
                 if count.product_id == item.product.id),
                None
            )

            variance = counted - item.quantity if counted is not None else None

            data.append([
                item.product.sku,
                item.product.name,
                str(item.quantity),
                str(counted) if counted is not None else '-',
                str(variance) if variance is not None else '-'
            ])

        self.items_table.data = data

    async def add_count(self, widget):
        """Add or update a count entry"""
        try:
            sku = self.sku_input.value
            quantity = int(self.quantity_input.value) if self.quantity_input.value else None

            if not sku or quantity is None or quantity < 0:
                error_dialog = toga.ErrorDialog(
                    title='Invalid Input',
                    message="Please enter valid SKU and quantity"
                )
                await self.window.app.dialog(error_dialog)
                return

            inventory_filter = {"sku": sku}
            inventory_list = await asyncio.to_thread(
                self.inventory_api.get_inventory,
                inventory_filter=inventory_filter
            )
            if not inventory_list.items:
                error_dialog = toga.ErrorDialog(
                    title='Product Not Found',
                    message=f"No product found with SKU: {sku}"
                )
                await self.window.app.dialog(error_dialog)
                return

            product = inventory_list.items[0].product

            # Update or add count
            count_item = next(
                (item for item in self.counted_items if item.product_id == product.id),
                None
            )

            if count_item:
                count_item.counted_quantity = quantity
            else:
                self.counted_items.append(StocktakeItem(
                    product_id=product.id,
                    counted_quantity=quantity
                ))

            await self.load_location_inventory()

            # Clear inputs
            self.sku_input.value = ''
            self.quantity_input.value = None

            info_dialog = toga.InfoDialog(
                title='Count Added',
                message=f"Count recorded for {product.name}"
            )
            await self.window.app.dialog(info_dialog)

        except Exception as e:
            error_dialog = toga.ErrorDialog(
                title='Error',
                message=str(e)
            )
            await self.window.app.dialog(error_dialog)

    def start_new_count(self, widget):
        """Start a new stock count"""
        confirm_dialog = toga.QuestionDialog(
            title='New Count',
            message='Start a new count? This will clear current counts.'
        )

        async def handle_response(dialog_result):
            if dialog_result:
                self.counted_items = []
                self.results_box.style.update(display='none')
                self.update_items_table([])
                self.location_select.value = None

                info_dialog = toga.InfoDialog(
                    title='New Count',
                    message='Ready to start new count'
                )
                await self.window.app.dialog(info_dialog)

        asyncio.create_task(self.window.app.dialog(confirm_dialog)).add_done_callback(
            lambda task: asyncio.create_task(handle_response(task.result()))
        )

    def open_scanner(self, widget):
        """Navigate to barcode scanner"""
        self.window.app.navigate_to(
            'barcode_scanner',
            on_scan=lambda barcode: setattr(self.sku_input, 'value', barcode)
        )

    async def complete_count(self, widget):
        """Complete and submit the stock count"""
        if not self.location or not self.counted_items:
            error_dialog = toga.ErrorDialog(
                title='Invalid Count',
                message="Please select a location and count items"
            )
            await self.window.app.dialog(error_dialog)
            return

        confirm_dialog = toga.ConfirmDialog(
            title='Complete Count',
            message='Submit this stock count? This cannot be undone.'
        )

        if await self.window.app.dialog(confirm_dialog):
            try:
                stocktake = StocktakeCreate(
                    location_id=self.location.id,
                    items=self.counted_items
                )

                result = await asyncio.to_thread(
                    self.inventory_api.perform_stocktake,
                    stocktake_data=stocktake
                )

                self.show_results(result)

                success_dialog = toga.InfoDialog(
                    title='Count Complete',
                    message=f'Stock count completed with {result.accuracy_percentage:.1f}% accuracy'
                )
                await self.window.app.dialog(success_dialog)

            except Exception as e:
                error_dialog = toga.ErrorDialog(
                    title='Error',
                    message=str(e)
                )
                await self.window.app.dialog(error_dialog)

    def show_results(self, result: StocktakeResult):
        """Display stock count results"""
        self.results_box.style.update(display='flex')

        data = []
        for disc in result.discrepancies:
            status = 'Match' if disc.discrepancy == 0 else 'Variance'
            data.append([
                disc.product.name,
                str(disc.expected_quantity),
                str(disc.counted_quantity),
                str(disc.discrepancy),
                status
            ])

        self.results_table.data = data

        # Show summary
        summary = toga.Label(
            f'Accuracy: {result.accuracy_percentage:.1f}% | '
            f'Total Items: {result.total_items} | '
            f'Discrepancies: {len(result.discrepancies)}',
            style=Pack(padding=(10, 0))
        )
        self.results_box.add(summary)

    def on_select_item(self, widget, row):
        """Handle item selection in table"""
        if row is None:
            return

        sku = self.items_table.data[row][0]
        self.sku_input.value = sku
        self.quantity_input.focus()

    async def cleanup(self):
        """Cleanup before screen exit"""
        if self.counted_items:
            confirm_dialog = toga.QuestionDialog(
                title='Unsaved Count',
                message='Discard current count?'
            )
            if await self.window.app.dialog(confirm_dialog):
                self.counted_items = []
                self.location = None

# src/nexusware/screens/inventory/inventory_list.py
import asyncio

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from public_api.api.inventory import InventoryAPI
from public_api.shared_schemas import InventoryFilter
from ..base import BaseScreen


class InventoryListScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.inventory_api = InventoryAPI(self.window.app.api_client)
        self.inventory_items = []
        self.filter = InventoryFilter()
        self.setup_inventory_screen()

    def setup_inventory_screen(self):
        main_box = toga.Box(style=Pack(
            direction=ROW,
            padding=20,
            flex=1
        ))

        # Left panel - Filters
        filter_box = self.create_filter_box()
        main_box.add(filter_box)

        # Right panel - Inventory list and details
        content_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=(0, 0, 0, 20),
            flex=1
        ))

        # Action buttons
        actions_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 0, 10, 0)
        ))

        scan_btn = toga.Button(
            'Scan Barcode',
            on_press=self.open_scanner,
            style=Pack(padding=(5, 10))
        )
        actions_box.add(scan_btn)

        stock_count_btn = toga.Button(
            'Stock Count',
            on_press=self.open_stock_count,
            style=Pack(padding=(5, 10))
        )
        actions_box.add(stock_count_btn)

        refresh_btn = toga.Button(
            'Refresh',
            on_press=self.refresh_inventory,
            style=Pack(padding=(5, 10))
        )
        actions_box.add(refresh_btn)

        content_box.add(actions_box)

        # Inventory table
        self.inventory_table = toga.Table(
            headings=['SKU', 'Name', 'Location', 'Quantity', 'Last Updated'],
            on_select=self.on_select_item,
            style=Pack(flex=1)
        )
        content_box.add(self.inventory_table)

        # Summary stats
        self.stats_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(10, 0)
        ))
        content_box.add(self.stats_box)

        main_box.add(content_box)
        self.content.add(main_box)

        # Initial load
        self.refresh_inventory()
        self.load_summary()

    def create_filter_box(self):
        filter_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=(0, 20, 0, 0),
            width=250
        ))

        # Filter title
        title = toga.Label(
            'Filters',
            style=Pack(
                font_size=16,
                font_weight='bold',
                padding=(0, 0, 10, 0)
            )
        )
        filter_box.add(title)

        # SKU filter
        sku_label = toga.Label('SKU')
        filter_box.add(sku_label)

        self.sku_input = toga.TextInput(
            on_change=self.apply_filters,
            style=Pack(padding=(0, 0, 10, 0))
        )
        filter_box.add(self.sku_input)

        # Name filter
        name_label = toga.Label('Product Name')
        filter_box.add(name_label)

        self.name_input = toga.TextInput(
            on_change=self.apply_filters,
            style=Pack(padding=(0, 0, 10, 0))
        )
        filter_box.add(self.name_input)

        # Quantity range
        quantity_label = toga.Label('Quantity Range')
        filter_box.add(quantity_label)

        quantity_box = toga.Box(style=Pack(direction=ROW))
        self.min_quantity = toga.NumberInput(
            min_value=0,
            on_change=self.apply_filters,
            style=Pack(padding=(0, 5, 0, 0), width=100)
        )
        quantity_box.add(self.min_quantity)

        to_label = toga.Label(' to ')
        quantity_box.add(to_label)

        self.max_quantity = toga.NumberInput(
            min_value=0,
            on_change=self.apply_filters,
            style=Pack(padding=(0, 0, 0, 5), width=100)
        )
        quantity_box.add(self.max_quantity)

        filter_box.add(quantity_box)

        # Reset filters button
        reset_btn = toga.Button(
            'Reset Filters',
            on_press=self.reset_filters,
            style=Pack(padding=(10, 0))
        )
        filter_box.add(reset_btn)

        return filter_box

    async def refresh_inventory(self, widget=None):
        """Refresh inventory list with current filters"""
        try:
            # Convert filter to API format
            inventory_list = await asyncio.to_thread(
                self.inventory_api.get_inventory,
                inventory_filter=self.filter
            )
            self.inventory_items = inventory_list.items
            self.update_inventory_table()
        except Exception as e:
            self.show_error(str(e))

    def update_inventory_table(self):
        """Update table with current inventory items"""
        data = []
        for item in self.inventory_items:
            data.append([
                item.product.sku,
                item.product.name,
                item.location.name,
                str(item.quantity),
                self.format_date(item.last_updated)
            ])
        self.inventory_table.data = data

    async def load_summary(self):
        """Load and display inventory summary statistics"""
        try:
            summary = await asyncio.to_thread(
                self.inventory_api.get_inventory_summary
            )
            self.stats_box.clear()

            stats = [
                ('Total Items', summary.total_items),
                ('Categories', summary.total_categories)
            ]

            for label, value in stats:
                stat_box = toga.Box(style=Pack(
                    direction=COLUMN,
                    padding=(0, 20)
                ))

                stat_box.add(toga.Label(
                    str(value),
                    style=Pack(
                        font_size=20,
                        font_weight='bold'
                    )
                ))
                stat_box.add(toga.Label(label))

                self.stats_box.add(stat_box)

        except Exception as e:
            self.show_error(str(e))

    def apply_filters(self, widget):
        """Apply current filter values"""
        self.filter = InventoryFilter(
            sku=self.sku_input.value if self.sku_input.value else None,
            name=self.name_input.value if self.name_input.value else None,
            quantity_min=int(self.min_quantity.value) if self.min_quantity.value else None,
            quantity_max=int(self.max_quantity.value) if self.max_quantity.value else None
        )
        self.refresh_inventory()

    def reset_filters(self, widget):
        """Reset all filters to default values"""
        self.sku_input.value = ''
        self.name_input.value = ''
        self.min_quantity.value = None
        self.max_quantity.value = None
        self.filter = InventoryFilter()
        self.refresh_inventory()

    def open_scanner(self, widget):
        """Navigate to barcode scanner screen"""
        self.window.app.navigate_to('barcode_scanner')

    def open_stock_count(self, widget):
        """Navigate to stock count screen"""
        self.window.app.navigate_to('stock_count')

    def on_select_item(self, widget, row):
        """Handle inventory item selection"""
        if row is not None:
            product_sku = self.inventory_table.data[row][0]
            product = next(item.product for item in self.inventory_items
                           if item.product.sku == product_sku)
            self.window.app.navigate_to('product_details', product_id=product.id)

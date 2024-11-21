# src/nexusware/screens/picking/picking.py
import asyncio
from datetime import datetime, timezone
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from ..base import BaseScreen
from public_api.api.pick_lists import PickListsAPI
from public_api.api.orders import OrdersAPI
from public_api.shared_schemas import (
    PickList, PickListUpdate, PickListItem, OptimizedPickingRoute,
    OrderWithDetails
)


class PickingScreen(BaseScreen):
    def __init__(self, pick_list_id: int, optimized_route: OptimizedPickingRoute | None = None):
        super().__init__()
        self.pick_lists_api = PickListsAPI(self.window.app.api_client)
        self.orders_api = OrdersAPI(self.window.app.api_client)
        self.pick_list_id = pick_list_id
        self.pick_list: PickList | None = None
        self.order: OrderWithDetails | None = None
        self.current_item_index = 0
        self.route = optimized_route
        self.setup_picking_screen()

    async def setup_picking_screen(self):
        """Initialize picking screen with data"""
        try:
            # Show loading dialog
            loading_dialog = toga.Dialog(
                title='Loading',
                content=toga.Label('Loading pick list details...'),
                on_result=None
            )
            await self.window.app.dialog(loading_dialog)

            # Load pick list and order data
            self.pick_list = await asyncio.to_thread(
                self.pick_lists_api.get_pick_list,
                self.pick_list_id
            )

            self.order = await asyncio.to_thread(
                self.orders_api.get_order,
                self.pick_list.order_id
            )

            # Get optimized route if not provided
            if not self.route:
                self.route = await asyncio.to_thread(
                    self.pick_lists_api.optimize_picking_route,
                    self.pick_list_id
                )

            # Close loading dialog
            loading_dialog.close()

            # Render screen
            self.render_picking_screen()

        except Exception as e:
            error_dialog = toga.ErrorDialog(
                title='Error',
                message=f"Failed to load picking details: {str(e)}"
            )
            await self.window.app.dialog(error_dialog)
            # Navigate back to pick lists
            self.window.app.navigate_to('pick_lists')

    def render_picking_screen(self):
        """Render the picking screen UI"""
        # Clear existing content
        if hasattr(self, 'content'):
            self.content.clear()

        main_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=20
        ))

        # Header
        header = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 0, 20, 0)
        ))

        title = toga.Label(
            f'Picking List #{self.pick_list_id}',
            style=Pack(
                font_size=24,
                font_weight='bold',
                flex=1
            )
        )
        header.add(title)

        progress = toga.Label(
            f'Item {self.current_item_index + 1} of {len(self.route.optimized_route)}',
            style=Pack(font_size=16)
        )
        header.add(progress)

        main_box.add(header)

        # Order details
        order_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=(0, 0, 20, 0),
            background_color=self.theme['secondary_background']
        ))

        order_title = toga.Label(
            f'Order #{self.order.id}',
            style=Pack(
                font_size=16,
                font_weight='bold',
                padding=(0, 0, 10, 0)
            )
        )
        order_box.add(order_title)

        customer_details = toga.Label(
            f'Customer: {self.order.shipping_name}',
            style=Pack(padding=(0, 0, 5, 0))
        )
        order_box.add(customer_details)

        main_box.add(order_box)

        # Current item details
        if self.current_item_index < len(self.route.optimized_route):
            item = self.route.optimized_route[self.current_item_index]
            product = next(
                (i.product for i in self.order.order_items if i.product.id == item.product_id),
                None
            )

            item_box = toga.Box(style=Pack(
                direction=COLUMN,
                padding=20,
                background_color=self.theme['content_background']
            ))

            # Product details
            details = [
                ('Product', product.name if product else str(item.product_id)),
                ('SKU', product.sku if product else 'N/A'),
                ('Location', str(item.location_id)),
                ('Quantity Required', str(item.quantity)),
                ('Quantity Picked', str(item.picked_quantity)),
                ('Remaining', str(item.quantity - item.picked_quantity))
            ]

            for label, value in details:
                detail_box = toga.Box(style=Pack(
                    direction=ROW,
                    padding=(0, 0, 10, 0)
                ))

                detail_box.add(toga.Label(
                    f'{label}:',
                    style=Pack(width=150, font_weight='bold')
                ))
                detail_box.add(toga.Label(value))

                item_box.add(detail_box)

            # Picking controls
            controls = toga.Box(style=Pack(
                direction=ROW,
                padding=(20, 0)
            ))

            self.quantity_input = toga.NumberInput(
                min_value=0,
                max_value=item.quantity - item.picked_quantity,
                value=0,
                style=Pack(width=100)
            )
            controls.add(self.quantity_input)

            confirm_btn = toga.Button(
                'Confirm Pick',
                on_press=self.confirm_pick,
                style=Pack(
                    padding=(5, 10),
                    background_color=self.theme['success']
                )
            )
            controls.add(confirm_btn)

            skip_btn = toga.Button(
                'Skip Item',
                on_press=self.skip_item,
                style=Pack(
                    padding=(5, 10),
                    background_color=self.theme['warning']
                )
            )
            controls.add(skip_btn)

            item_box.add(controls)
            main_box.add(item_box)

            # Scanner button
            scanner_btn = toga.Button(
                'Open Scanner',
                on_press=self.open_scanner,
                style=Pack(padding=(10, 0))
            )
            main_box.add(scanner_btn)

        # Complete button
        if self.current_item_index >= len(self.route.optimized_route):
            complete_box = toga.Box(style=Pack(
                direction=COLUMN,
                padding=(20, 0),
                alignment='center'
            ))

            complete_label = toga.Label(
                'All items have been picked!',
                style=Pack(
                    font_size=18,
                    font_weight='bold',
                    padding=(0, 0, 10, 0)
                )
            )
            complete_box.add(complete_label)

            complete_btn = toga.Button(
                'Complete Pick List',
                on_press=self.complete_pick_list,
                style=Pack(
                    padding=10,
                    background_color=self.theme['success']
                )
            )
            complete_box.add(complete_btn)

            main_box.add(complete_box)

        self.content.add(main_box)

    async def confirm_pick(self, widget):
        """Handle pick confirmation"""
        try:
            quantity = self.quantity_input.value
            if quantity <= 0:
                error_dialog = toga.ErrorDialog(
                    title='Invalid Quantity',
                    message="Please enter a valid quantity"
                )
                await self.window.app.dialog(error_dialog)
                return

            current_item = self.route.optimized_route[self.current_item_index]

            # Update picked quantity
            update_data = PickListUpdate(
                items=[{
                    'product_id': current_item.product_id,
                    'picked_quantity': current_item.picked_quantity + quantity
                }]
            )

            await asyncio.to_thread(
                self.pick_lists_api.update_pick_list,
                self.pick_list_id,
                update_data
            )

            self.current_item_index += 1

            # Show success message
            info_dialog = toga.InfoDialog(
                title='Success',
                message=f'Picked {quantity} items'
            )
            await self.window.app.dialog(info_dialog)

            self.render_picking_screen()

        except Exception as e:
            error_dialog = toga.ErrorDialog(
                title='Error',
                message=str(e)
            )
            await self.window.app.dialog(error_dialog)

    async def skip_item(self, widget):
        """Handle item skip"""
        confirm_dialog = toga.ConfirmDialog(
            title='Skip Item',
            message='Are you sure you want to skip this item?'
        )

        if await self.window.app.dialog(confirm_dialog):
            self.current_item_index += 1
            self.render_picking_screen()

    def open_scanner(self, widget):
        """Navigate to barcode scanner"""
        current_item = self.route.optimized_route[self.current_item_index]
        product = next(
            i.product for i in self.order.order_items if i.product.id == current_item.product_id
        )

        def handle_scan(barcode):
            if barcode == product.barcode:
                self.quantity_input.value = 1
                asyncio.create_task(self.confirm_pick(None))
            else:
                asyncio.create_task(self.show_error("Incorrect product scanned"))

        self.window.app.navigate_to(
            'barcode_scanner',
            on_scan=handle_scan
        )

    async def complete_pick_list(self, widget):
        """Complete the pick list"""
        confirm_dialog = toga.ConfirmDialog(
            title='Complete Pick List',
            message='Are you sure you want to complete this pick list?'
        )

        if await self.window.app.dialog(confirm_dialog):
            try:
                await asyncio.to_thread(
                    self.pick_lists_api.complete_pick_list,
                    self.pick_list_id
                )

                success_dialog = toga.InfoDialog(
                    title='Success',
                    message='Pick list completed successfully'
                )
                await self.window.app.dialog(success_dialog)
                self.window.app.navigate_to('pick_lists')

            except Exception as e:
                error_dialog = toga.ErrorDialog(
                    title='Error',
                    message=str(e)
                )
                await self.window.app.dialog(error_dialog)

    def format_date(self, timestamp: int) -> str:
        """Format timestamp for display"""
        if not timestamp:
            return '-'
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M')

    async def cleanup(self):
        """Cleanup when leaving screen"""
        if self.current_item_index > 0 and self.current_item_index < len(self.route.optimized_route):
            confirm_dialog = toga.ConfirmDialog(
                title='Exit Picking',
                message='Are you sure you want to exit? Progress will be saved.'
            )
            if not await self.window.app.dialog(confirm_dialog):
                return False
        return True
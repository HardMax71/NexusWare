# src/nexusware/screens/picking/pick_list.py
import asyncio
from datetime import datetime, timezone
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from ..base import BaseScreen
from public_api.api.pick_lists import PickListsAPI
from public_api.api.orders import OrdersAPI
from public_api.shared_schemas import (
    PickList, PickListCreate, PickListFilter,
    PickListItemCreate, OptimizedPickingRoute,
    Order, OrderStatus, OrderWithDetails
)


class PickListScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.pick_lists_api = PickListsAPI(self.window.app.api_client)
        self.orders_api = OrdersAPI(self.window.app.api_client)
        self.pick_lists: list[PickList] = []
        self.selected_pick_list: PickList | None = None
        self.setup_pick_list_screen()

    def setup_pick_list_screen(self):
        main_box = toga.Box(style=Pack(
            direction=ROW,
            padding=20,
            flex=1
        ))

        # Left panel - Pick lists
        lists_box = toga.Box(style=Pack(
            direction=COLUMN,
            flex=1,
            padding=(0, 10, 0, 0)
        ))

        # Actions header
        actions = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 0, 10, 0)
        ))

        create_btn = toga.Button(
            'Create Pick List',
            on_press=self.show_create_dialog,
            style=Pack(
                padding=(5, 10),
                background_color=self.theme['button_background']
            )
        )
        actions.add(create_btn)

        refresh_btn = toga.Button(
            'Refresh',
            on_press=self.refresh_pick_lists,
            style=Pack(padding=(5, 10))
        )
        actions.add(refresh_btn)

        lists_box.add(actions)

        # Pick lists table
        self.pick_lists_table = toga.Table(
            headings=['ID', 'Order', 'Status', 'Items', 'Created'],
            on_select=self.on_select_pick_list,
            style=Pack(flex=1)
        )
        lists_box.add(self.pick_lists_table)

        main_box.add(lists_box)

        # Right panel - Details
        self.details_box = toga.Box(style=Pack(
            direction=COLUMN,
            flex=1,
            padding=(0, 0, 0, 20)
        ))
        self.details_box.add(toga.Label('Select a pick list to view details'))
        main_box.add(self.details_box)

        self.content.add(main_box)
        asyncio.create_task(self.refresh_pick_lists())

    async def refresh_pick_lists(self, widget=None):
        """Refresh the list of pick lists"""
        try:
            self.pick_lists = await asyncio.to_thread(
                self.pick_lists_api.get_pick_lists
            )
            self.update_pick_lists_table()
        except Exception as e:
            error_dialog = toga.ErrorDialog(
                title='Error',
                message=f"Failed to load pick lists: {str(e)}"
            )
            await self.window.app.dialog(error_dialog)

    def update_pick_lists_table(self):
        """Update pick lists table with current data"""
        data = []
        for pick_list in self.pick_lists:
            data.append([
                str(pick_list.pick_list_id),
                f'Order #{pick_list.order_id}',
                pick_list.status,
                str(len(pick_list.items)),
                self.format_date(pick_list.created_at)
            ])
        self.pick_lists_table.data = data

    async def show_create_dialog(self, widget):
        """Show dialog to create new pick list"""
        try:
            # Get pending orders that don't have pick lists
            orders = await asyncio.to_thread(
                self.orders_api.get_orders,
                filter_params={"status": OrderStatus.PROCESSING}
            )

            if not orders:
                info_dialog = toga.InfoDialog(
                    title='No Orders',
                    message='No orders available for picking'
                )
                await self.window.app.dialog(info_dialog)
                return

            # Create order selection form
            form_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

            # Order selection
            order_box = toga.Box(style=Pack(direction=ROW, padding=(0, 0, 10, 0)))
            order_box.add(toga.Label('Select Order:'))

            self.order_select = toga.Selection(
                items=[f'Order #{order.id} - {len(order.order_items)} items'
                       for order in orders]
            )
            order_box.add(self.order_select)
            form_box.add(order_box)

            # Store orders for reference
            self.pending_orders = orders

            create_dialog = toga.Dialog(
                title='Create Pick List',
                content=form_box,
                on_result=self.handle_create_dialog
            )
            await self.window.app.dialog(create_dialog)

        except Exception as e:
            error_dialog = toga.ErrorDialog(
                title='Error',
                message=str(e)
            )
            await self.window.app.dialog(error_dialog)

    async def handle_create_dialog(self, dialog, result):
        """Handle create dialog result"""
        if result and self.order_select.value:
            try:
                # Get selected order
                order_index = self.order_select.items.index(self.order_select.value)
                order = self.pending_orders[order_index]

                # Create pick list items from order items
                pick_list_items = [
                    PickListItemCreate(
                        product_id=item.product.id,
                        location_id=0,  # Will be assigned by backend
                        quantity=item.quantity,
                        picked_quantity=0
                    )
                    for item in order.order_items
                ]

                # Create pick list
                pick_list_data = PickListCreate(
                    order_id=order.id,
                    status="Pending",
                    items=pick_list_items
                )

                await asyncio.to_thread(
                    self.pick_lists_api.create_pick_list,
                    pick_list_data
                )

                success_dialog = toga.InfoDialog(
                    title='Success',
                    message='Pick list created successfully'
                )
                await self.window.app.dialog(success_dialog)
                await self.refresh_pick_lists()

            except Exception as e:
                error_dialog = toga.ErrorDialog(
                    title='Error',
                    message=str(e)
                )
                await self.window.app.dialog(error_dialog)

    async def on_select_pick_list(self, widget, row):
        """Handle pick list selection"""
        if row is None:
            return

        try:
            pick_list_id = int(self.pick_lists_table.data[row][0])
            self.selected_pick_list = await asyncio.to_thread(
                self.pick_lists_api.get_pick_list,
                pick_list_id
            )
            # Also get order details
            order = await asyncio.to_thread(
                self.orders_api.get_order,
                self.selected_pick_list.order_id
            )
            await self.show_pick_list_details(order)
        except Exception as e:
            error_dialog = toga.ErrorDialog(
                title='Error',
                message=f"Failed to load pick list details: {str(e)}"
            )
            await self.window.app.dialog(error_dialog)

    async def show_pick_list_details(self, order: OrderWithDetails):
        """Display pick list details with order information"""
        self.details_box.clear()

        # Header
        header = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 0, 10, 0)
        ))

        title = toga.Label(
            f'Pick List #{self.selected_pick_list.pick_list_id}',
            style=Pack(
                font_size=18,
                font_weight='bold',
                flex=1
            )
        )
        header.add(title)

        if self.selected_pick_list.status == 'Pending':
            start_btn = toga.Button(
                'Start Picking',
                on_press=self.start_picking,
                style=Pack(
                    padding=(5, 10),
                    background_color=self.theme['success']
                )
            )
            header.add(start_btn)

        self.details_box.add(header)

        # Order details
        order_box = toga.Box(style=Pack(direction=COLUMN, padding=(0, 0, 10, 0)))

        order_title = toga.Label(
            'Order Details',
            style=Pack(font_weight='bold', padding=(0, 0, 5, 0))
        )
        order_box.add(order_title)

        details = [
            ('Order ID', str(order.id)),
            ('Customer', order.shipping_name or 'N/A'),
            ('Status', order.status),
            ('Order Date', self.format_date(order.order_date)),
            ('Total Amount', f'${order.total_amount:.2f}'),
        ]

        for label, value in details:
            detail_box = toga.Box(style=Pack(direction=ROW, padding=(0, 0, 5, 0)))
            detail_box.add(toga.Label(f'{label}:', style=Pack(width=100)))
            detail_box.add(toga.Label(value))
            order_box.add(detail_box)

        self.details_box.add(order_box)

        # Items table
        items_label = toga.Label(
            'Items to Pick',
            style=Pack(
                font_size=16,
                font_weight='bold',
                padding=(10, 0)
            )
        )
        self.details_box.add(items_label)

        items_table = toga.Table(
            headings=['Product', 'Location', 'Qty Needed', 'Qty Picked', 'Status'],
            style=Pack(flex=1)
        )

        items_data = [
            [
                next(i.product.name for i in order.order_items if i.product.id == item.product_id),
                str(item.location_id),
                str(item.quantity),
                str(item.picked_quantity),
                'Complete' if item.picked_quantity >= item.quantity else 'Pending'
            ]
            for item in self.selected_pick_list.items
        ]
        items_table.data = items_data

        self.details_box.add(items_table)

    async def start_picking(self, widget):
        """Start picking process for selected pick list"""
        if not self.selected_pick_list:
            return

        confirm_dialog = toga.ConfirmDialog(
            title='Start Picking',
            message=f'Start picking for Pick List #{self.selected_pick_list.pick_list_id}?'
        )

        if await self.window.app.dialog(confirm_dialog):
            try:
                # Get optimized route
                route = await asyncio.to_thread(
                    self.pick_lists_api.optimize_picking_route,
                    self.selected_pick_list.pick_list_id
                )

                # Start pick list
                await asyncio.to_thread(
                    self.pick_lists_api.start_pick_list,
                    self.selected_pick_list.pick_list_id
                )

                # Navigate to picking screen with optimized route
                self.window.app.navigate_to(
                    'picking',
                    pick_list_id=self.selected_pick_list.pick_list_id,
                    optimized_route=route
                )

            except Exception as e:
                error_dialog = toga.ErrorDialog(
                    title='Error',
                    message=f"Failed to start picking: {str(e)}"
                )
                await self.window.app.dialog(error_dialog)

    def format_date(self, timestamp: int) -> str:
        """Format timestamp for display"""
        if not timestamp:
            return '-'
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M')

    async def cleanup(self):
        """Cleanup when leaving screen"""
        self.selected_pick_list = None
        self.pick_lists = []
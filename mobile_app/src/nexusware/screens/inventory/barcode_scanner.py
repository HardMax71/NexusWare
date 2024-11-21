# src/nexusware/screens/inventory/barcode_scanner.py
import asyncio

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from public_api.api.inventory import InventoryAPI
from ..base import BaseScreen


class BarcodeScanner(BaseScreen):
    def __init__(self):
        super().__init__()
        self.inventory_api = InventoryAPI(self.window.app.api_client)
        self.camera_active = False
        self.setup_scanner_screen()

    def setup_scanner_screen(self):
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
            'Barcode Scanner',
            style=Pack(
                font_size=24,
                font_weight='bold',
                flex=1
            )
        )
        header_box.add(title)

        # Camera toggle button
        self.camera_btn = toga.Button(
            'Start Camera',
            on_press=self.toggle_camera,
            style=Pack(
                padding=(5, 10),
                background_color=self.theme['button_background']
            )
        )
        header_box.add(self.camera_btn)

        main_box.add(header_box)

        # Camera preview
        self.camera_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=10,
            flex=1,
            background_color='#000000'
        ))
        main_box.add(self.camera_box)

        # Manual entry
        manual_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=10
        ))

        manual_label = toga.Label(
            'Manual Entry',
            style=Pack(
                font_size=16,
                font_weight='bold',
                padding=(0, 0, 10, 0)
            )
        )
        manual_box.add(manual_label)

        input_box = toga.Box(style=Pack(direction=ROW))

        self.barcode_input = toga.TextInput(
            placeholder='Enter barcode...',
            style=Pack(
                padding=(0, 10, 0, 0),
                flex=1
            )
        )
        input_box.add(self.barcode_input)

        submit_btn = toga.Button(
            'Submit',
            on_press=self.handle_manual_entry,
            style=Pack(
                padding=(5, 10),
                background_color=self.theme['button_background']
            )
        )
        input_box.add(submit_btn)

        manual_box.add(input_box)
        main_box.add(manual_box)

        # Recent scans
        scans_label = toga.Label(
            'Recent Scans',
            style=Pack(
                font_size=16,
                font_weight='bold',
                padding=(20, 0, 10, 0)
            )
        )
        main_box.add(scans_label)

        self.scans_table = toga.Table(
            headings=['Time', 'Barcode', 'Product', 'Status'],
            style=Pack(flex=1)
        )
        main_box.add(self.scans_table)

        self.content.add(main_box)

    async def toggle_camera(self, widget):
        """Handle camera toggle"""
        try:
            if not self.camera_active:
                await self.start_camera()
                self.camera_btn.text = 'Stop Camera'
                self.camera_active = True
            else:
                await self.stop_camera()
                self.camera_btn.text = 'Start Camera'
                self.camera_active = False
        except Exception as e:
            self.show_error(str(e))

    async def start_camera(self):
        """Initialize and start camera"""
        try:
            # Initialize camera
            self.camera = toga.Camera(self.on_frame)
            await self.camera.start()

            # Create camera preview
            self.preview = toga.ImageView(
                style=Pack(
                    width=400,
                    height=300
                )
            )
            self.camera_box.add(self.preview)

        except Exception as e:
            self.show_error(f"Failed to start camera: {str(e)}")

    async def stop_camera(self):
        """Stop camera and cleanup"""
        if hasattr(self, 'camera'):
            await self.camera.stop()
            self.camera_box.remove(self.preview)

    async def on_frame(self, frame):
        """Process camera frame"""
        try:
            if frame and self.camera_active:
                # Update preview
                self.preview.image = frame

                # Scan for barcode using image processing
                barcode = await self.scan_frame_for_barcode(frame)
                if barcode:
                    await self.process_barcode(barcode)

        except Exception as e:
            self.show_error(f"Frame processing error: {str(e)}")

    async def scan_frame_for_barcode(self, frame):
        """
        Scan frame for barcode using image processing
        Returns barcode string if found, None otherwise
        """
        # TODO: Implement actual barcode detection using CV
        return None

    async def handle_manual_entry(self, widget):
        """Handle manual barcode entry"""
        barcode = self.barcode_input.value
        if not barcode:
            self.show_error("Please enter a barcode")
            return

        await self.process_barcode(barcode)
        self.barcode_input.value = ''

    async def process_barcode(self, barcode):
        """Process scanned/entered barcode"""
        try:
            # Get inventory filter by barcode
            inventory_filter = {
                "sku": barcode  # Assuming barcode matches SKU
            }

            # Look up product by barcode
            inventory_result = await asyncio.to_thread(
                self.inventory_api.get_inventory,
                inventory_filter=inventory_filter
            )

            if inventory_result.items:
                inventory_item = inventory_result.items[0]
                self.add_scan_record(barcode, inventory_item.product)
                self.show_product_details(inventory_item.product)
            else:
                self.add_scan_record(barcode, None, error="Product not found")
                self.show_error("Product not found")

        except Exception as e:
            self.add_scan_record(barcode, None, error=str(e))
            self.show_error(f"Error processing barcode: {str(e)}")

    def add_scan_record(self, barcode, product, error=None):
        """Add scan record to recent scans table"""
        scan_time = self.format_time(None)
        status = 'Success' if product else f'Error: {error}'
        product_name = product.name if product else '-'

        current_data = list(self.scans_table.data)
        current_data.insert(0, [scan_time, barcode, product_name, status])

        # Keep only last 10 scans
        self.scans_table.data = current_data[:10]

    def show_product_details(self, product):
        """Navigate to product details screen"""
        self.window.app.navigate_to(
            'product_details',
            product_id=product.id
        )

    def format_time(self, timestamp):
        """Format timestamp for display"""
        from datetime import datetime
        return datetime.now().strftime('%H:%M:%S')

    async def cleanup(self):
        """Cleanup when leaving the screen"""
        if self.camera_active:
            await self.stop_camera()

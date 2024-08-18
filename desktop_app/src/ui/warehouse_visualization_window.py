from collections import defaultdict

import matplotlib

matplotlib.use('Qt5Agg')
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from public_api.api import WarehouseAPI, APIClient
from public_api.shared_schemas import WarehouseLayout


class WarehouseVisualizationWidget(QWidget):
    def __init__(self, warehouse_api: WarehouseAPI):
        super().__init__()
        self.warehouse_api = warehouse_api
        self.warehouse_layout: WarehouseLayout = None
        self.inventory_data = {}
        self.unique_aisles = []
        self.unique_racks = []
        self.location_grid = defaultdict(list)
        self.max_inventory_level = 100  # Default value, will be updated dynamically

        layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.ax = self.figure.add_subplot(111, projection='3d')
        self.load_warehouse_data()

    def load_warehouse_data(self):
        self.warehouse_layout = self.warehouse_api.get_warehouse_layout()
        self.load_inventory_data()
        self.update_visualization()

    def load_inventory_data(self):
        self.inventory_data.clear()
        self.unique_aisles.clear()
        self.unique_racks.clear()
        self.location_grid.clear()
        max_level = 0
        for zone in self.warehouse_layout.zones:
            for location in zone.locations:
                inventory = self.warehouse_api.get_location_inventory(location.id)
                self.inventory_data[location.id] = inventory
                inventory_level = sum(item.quantity for item in inventory)
                max_level = max(max_level, inventory_level)
                if location.aisle and location.aisle not in self.unique_aisles:
                    self.unique_aisles.append(location.aisle)
                if location.rack and location.rack not in self.unique_racks:
                    self.unique_racks.append(location.rack)
                self.location_grid[(location.aisle, location.rack)].append(location)

        self.max_inventory_level = max(100, max_level)  # Ensure it's at least 100
        self.unique_aisles.sort()
        self.unique_racks.sort(key=lambda x: int(x) if x.isdigit() else x)

    def update_visualization(self):
        if not self.warehouse_layout:
            return

        self.ax.clear()

        for (aisle, rack), locations in self.location_grid.items():
            self.draw_cell(aisle, rack, locations)

        self.ax.set_xlabel('Aisles')
        self.ax.set_ylabel('Racks')
        self.ax.set_zlabel('Inventory Level')
        self.ax.set_title('3D Warehouse Layout')

        max_aisle = len(self.unique_aisles)
        max_rack = len(self.unique_racks)
        self.ax.set_xlim(0, max_aisle)
        self.ax.set_ylim(0, max_rack)
        self.ax.set_zlim(0, self.max_inventory_level)

        self.ax.set_xticks(range(max_aisle))
        self.ax.set_xticklabels(self.unique_aisles)
        self.ax.set_yticks(range(max_rack))
        self.ax.set_yticklabels(self.unique_racks)

        self.figure.tight_layout()
        self.canvas.draw()

    def draw_cell(self, aisle, rack, locations):
        x = self.unique_aisles.index(aisle)
        y = self.unique_racks.index(rack)

        for i, location in enumerate(locations):
            offset_x = i % 2 * 0.4
            offset_y = i // 2 * 0.4
            self.draw_location(x + offset_x, y + offset_y, location)

    def draw_location(self, x, y, location):
        inventory_items = self.inventory_data.get(location.id, [])
        inventory_level = sum(item.quantity for item in inventory_items)
        fill_level = inventory_level / self.max_inventory_level

        color = self.get_color_by_fill_level(fill_level)

        # Draw a 3D bar for each location
        self.ax.bar3d(x, y, 0, 0.3, 0.3, inventory_level, shade=True, color=color, alpha=0.8)

        # Add text labels
        location_text = f"{location.shelf}-{location.bin or 'bin'}"
        self.ax.text(x + 0.15, y + 0.15, inventory_level + self.max_inventory_level * 0.05,
                     f"{location_text}\n{inventory_level}",
                     ha='center', va='center', fontsize=8)

    def get_color_by_fill_level(self, fill_level):
        if fill_level < 0.3:
            return '#90EE90'  # Light green
        elif fill_level < 0.7:
            return '#FFFFE0'  # Light yellow
        else:
            return '#FFA07A'  # Light salmon


class WarehouseVisualizationWindow(QMainWindow):
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.warehouse_api = WarehouseAPI(api_client)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("3D Warehouse Visualization")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        self.visualization_widget = WarehouseVisualizationWidget(self.warehouse_api)
        main_layout.addWidget(self.visualization_widget)

        button_layout = QHBoxLayout()
        refresh_button = QPushButton("Refresh Data")
        refresh_button.clicked.connect(self.refresh_data)
        button_layout.addWidget(refresh_button)

        main_layout.addLayout(button_layout)

        self.setCentralWidget(central_widget)

    def refresh_data(self):
        self.visualization_widget.load_warehouse_data()

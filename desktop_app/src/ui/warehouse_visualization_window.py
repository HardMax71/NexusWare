from collections import defaultdict

import matplotlib

matplotlib.use('Qt5Agg')

from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as patches

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

        layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.ax = self.figure.add_subplot(111)
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
        for zone in self.warehouse_layout.zones:
            for location in zone.locations:
                self.inventory_data[location.id] = self.warehouse_api.get_location_inventory(location.id)
                if location.aisle and location.aisle not in self.unique_aisles:
                    self.unique_aisles.append(location.aisle)
                if location.rack and location.rack not in self.unique_racks:
                    self.unique_racks.append(location.rack)
                self.location_grid[(location.aisle, location.rack)].append(location)

        self.unique_aisles.sort()
        self.unique_racks.sort(key=lambda x: int(x) if x.isdigit() else x)

    def update_visualization(self):
        if not self.warehouse_layout:
            return

        self.ax.clear()
        self.ax.set_xlim(0, len(self.unique_aisles))
        self.ax.set_ylim(0, len(self.unique_racks))

        for (aisle, rack), locations in self.location_grid.items():
            self.draw_cell(aisle, rack, locations)

        self.ax.set_xlabel('Aisles')
        self.ax.set_ylabel('Racks')
        self.ax.set_title('Warehouse Layout')
        self.ax.set_xticks([i + 0.5 for i in range(len(self.unique_aisles))])
        self.ax.set_xticklabels(self.unique_aisles)
        self.ax.set_yticks([i + 0.5 for i in range(len(self.unique_racks))])
        self.ax.set_yticklabels(self.unique_racks)
        self.ax.invert_yaxis()
        self.figure.tight_layout()
        self.canvas.draw()

    def draw_cell(self, aisle, rack, locations):
        x = self.unique_aisles.index(aisle)
        y = self.unique_racks.index(rack)

        num_locations = len(locations)
        if num_locations == 1:
            self.draw_single_location(x, y, locations[0])
        else:
            self.draw_multiple_locations(x, y, locations)

    def draw_single_location(self, x, y, location):
        inventory_items = self.inventory_data.get(location.id, [])
        inventory_level = sum(item.quantity for item in inventory_items)
        max_capacity = 100
        fill_level = min(inventory_level / max_capacity, 1.0)

        color = self.get_color_by_fill_level(fill_level)
        rect = patches.Rectangle((x, y), 1, 1, fill=True, facecolor=color, edgecolor='black', linewidth=0.5)
        self.ax.add_patch(rect)

        location_text = f"{location.shelf}-{location.bin or 'bin'}"
        inventory_text = f"{inventory_level}/{max_capacity}"
        self.ax.text(x + 0.5, y + 0.6, location_text, fontsize=8, ha='center', va='center')
        self.ax.text(x + 0.5, y + 0.4, inventory_text, fontsize=8, ha='center', va='center')

    def draw_multiple_locations(self, x, y, locations):
        num_locations = len(locations)
        cols = min(2, num_locations)
        rows = (num_locations + 1) // 2

        for i, location in enumerate(locations):
            sub_x = x + (i % cols) * 0.5
            sub_y = y + (i // cols) * (1 / rows)

            inventory_items = self.inventory_data.get(location.id, [])
            inventory_level = sum(item.quantity for item in inventory_items)
            max_capacity = 100
            fill_level = min(inventory_level / max_capacity, 1.0)

            color = self.get_color_by_fill_level(fill_level)
            rect = patches.Rectangle((sub_x, sub_y), 0.5, 1 / rows, fill=True, facecolor=color, edgecolor='black',
                                     linewidth=0.5)
            self.ax.add_patch(rect)

            location_text = f"{location.shelf}-{location.bin or 'bin'}"
            inventory_text = f"{inventory_level}/{max_capacity}"
            self.ax.text(sub_x + 0.25, sub_y + 0.6 / rows, location_text, fontsize=6, ha='center', va='center')
            self.ax.text(sub_x + 0.25, sub_y + 0.3 / rows, inventory_text, fontsize=6, ha='center', va='center')

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
        self.setWindowTitle("Warehouse Visualization")
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

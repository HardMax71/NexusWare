from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene

from desktop_app.src.api import WarehouseAPI, APIClient


class WarehouseVisualizerWidget(QWidget):
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.warehouse_api = WarehouseAPI(api_client)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        layout.addWidget(self.view)

        self.load_warehouse_layout()

    def load_warehouse_layout(self):
        layout_data = self.warehouse_api.get_warehouse_layout()
        self.draw_warehouse(layout_data)

    def draw_warehouse(self, layout_data):
        self.scene.clear()

        for zone in layout_data['zones']:
            zone_item = self.scene.addRect(zone['x'], zone['y'], zone['width'], zone['height'],
                                           QPen(Qt.black), QBrush(QColor(200, 200, 200, 100)))
            zone_item.setToolTip(f"Zone: {zone['name']}")

            for location in zone['locations']:
                location_item = self.scene.addRect(location['x'], location['y'], location['width'], location['height'],
                                                   QPen(Qt.black), QBrush(QColor(150, 150, 150, 100)))
                location_item.setToolTip(f"Location: {location['name']}\nOccupancy: {location['occupancy']}%")

        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

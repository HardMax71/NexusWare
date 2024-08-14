from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QComboBox, QSpinBox

from public_api.api import APIClient
from .components import StyledButton


# TODO: Implement simulation stuff

class SimulationView(QWidget):
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()
        self.simulation_type = QComboBox()
        self.simulation_type.addItems(["Order Processing", "Inventory Management", "Shipment Routing"])
        self.duration = QSpinBox()
        self.duration.setRange(1, 30)
        self.duration.setSuffix(" days")
        self.start_button = StyledButton("Start Simulation")
        self.start_button.clicked.connect(self.start_simulation)
        controls_layout.addWidget(self.simulation_type)
        controls_layout.addWidget(self.duration)
        controls_layout.addWidget(self.start_button)
        layout.addLayout(controls_layout)

        # Simulation display
        self.simulation_display = QTextEdit()
        self.simulation_display.setReadOnly(True)
        layout.addWidget(self.simulation_display)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_simulation)
        self.current_day = 0

    def start_simulation(self):
        self.simulation_display.clear()
        self.current_day = 0
        self.timer.start(1000)  # Update every second

    def update_simulation(self):
        self.current_day += 1
        if self.current_day <= self.duration.value():
            sim_type = self.simulation_type.currentText()
            result = self.api_client.run_simulation(sim_type, self.current_day)
            self.simulation_display.append(f"Day {self.current_day}: {result}")
        else:
            self.timer.stop()
            self.simulation_display.append("Simulation complete.")

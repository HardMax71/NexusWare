from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox

from public_api.api import OrdersAPI, APIClient
from desktop_app.src.ui.components import StyledButton
from public_api.shared_schemas import OrderFilter


# TODO: Implement missing functions

class OrderView(QWidget):
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.orders_api = OrdersAPI(api_client)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Pending", "Processing", "Shipped", "Delivered", "Cancelled"])
        self.refresh_button = StyledButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_orders)
        self.new_order_button = StyledButton("New Order")
        self.new_order_button.clicked.connect(self.create_new_order)
        controls_layout.addWidget(self.status_combo)
        controls_layout.addWidget(self.refresh_button)
        controls_layout.addWidget(self.new_order_button)
        layout.addLayout(controls_layout)

        # Orders table
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(6)
        self.orders_table.setHorizontalHeaderLabels(["Order ID", "Customer", "Date", "Total", "Status", "Actions"])
        layout.addWidget(self.orders_table)

        self.refresh_orders()

    def refresh_orders(self):
        status_filter = self.status_combo.currentText()
        if status_filter == "All":
            status_filter = None

        filter = OrderFilter(status=status_filter)
        orders = self.orders_api.get_orders(filter_params=filter)
        self.orders_table.setRowCount(len(orders))
        for row, order in enumerate(orders):
            self.orders_table.setItem(row, 0, QTableWidgetItem(str(order.order_id)))
            self.orders_table.setItem(row, 1, QTableWidgetItem(order.customer.name))
            self.orders_table.setItem(row, 2, QTableWidgetItem(order.order_date.strftime("%Y-%m-%d")))
            self.orders_table.setItem(row, 3, QTableWidgetItem(f"${order.total_amount:.2f}"))
            self.orders_table.setItem(row, 4, QTableWidgetItem(order.status))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            view_button = StyledButton("View")
            view_button.clicked.connect(lambda _, oid=order.order_id: self.view_order(oid))
            actions_layout.addWidget(view_button)
            self.orders_table.setCellWidget(row, 5, actions_widget)

    def create_new_order(self):
        # Implement new order creation dialog
        pass

    def view_order(self, order_id):
        # Implement order details view
        pass

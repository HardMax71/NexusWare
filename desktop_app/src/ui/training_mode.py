from PySide6.QtCore import Qt, QRect, QPoint, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsOpacityEffect, \
    QApplication


class GlowingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.highlight_rect = QRect()
        if parent:
            self.resize(parent.size())
            parent.resizeEvent = self.parent_resize_event

    def parent_resize_event(self, event):
        self.resize(event.size())

    def set_highlight(self, rect):
        self.highlight_rect = rect
        self.update()


class TrainingModeManager:
    def __init__(self, main_window, config_manager):
        self.main_window = main_window
        self.config_manager = config_manager
        self.current_step = 0
        self.overlay = GlowingOverlay(main_window)
        self.tooltip = QLabel(main_window)
        self.tooltip.setStyleSheet("""
            QLabel {
                background-color: #F0F0F0;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        self.tooltip.hide()

        self.skip_button = QPushButton("Skip Training", self.tooltip)
        self.skip_button.clicked.connect(self.skip_training)

        self.next_button = QPushButton("Next", self.tooltip)
        self.next_button.clicked.connect(self.next_step)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.skip_button)
        button_layout.addWidget(self.next_button)

        tooltip_layout = QVBoxLayout(self.tooltip)
        self.tooltip_text = QLabel()
        self.tooltip_text.setWordWrap(True)
        tooltip_layout.addWidget(self.tooltip_text)
        tooltip_layout.addLayout(button_layout)

        self.training_steps = [
            {
                "target": "menu_bar",
                "text": "This is the menu bar. You can access various functions from here.",
                "rect": lambda: self.main_window.menuBar().geometry()
            },
            {
                "target": "dashboard_tab",
                "text": "The Dashboard tab provides an overview of key metrics and information.",
                "rect": lambda: self.get_tab_rect("Dashboard")
            },
            {
                "target": "inventory_tab",
                "text": "The Inventory tab allows you to manage and view your stock levels.",
                "rect": lambda: self.get_tab_rect("Inventory")
            },
            {
                "target": "orders_tab",
                "text": "The Orders tab is where you can process and manage customer orders.",
                "rect": lambda: self.get_tab_rect("Orders")
            },
            {
                "target": "products_tab",
                "text": "The Products tab lets you manage your product catalog.",
                "rect": lambda: self.get_tab_rect("Products")
            },
            {
                "target": "suppliers_tab",
                "text": "The Suppliers tab is for managing your supplier information.",
                "rect": lambda: self.get_tab_rect("Suppliers")
            },
            {
                "target": "customers_tab",
                "text": "The Customers tab allows you to manage customer information.",
                "rect": lambda: self.get_tab_rect("Customers")
            },
            {
                "target": "shipments_tab",
                "text": "The Shipments tab is where you can track and manage outgoing shipments.",
                "rect": lambda: self.get_tab_rect("Shipments")
            },
            {
                "target": "status_bar",
                "text": "The status bar at the bottom provides additional information and notifications.",
                "rect": lambda: self.main_window.statusBar().geometry()
            }
        ]

    def get_tab_rect(self, tab_name):
        index = self.main_window.tab_widget.findText(tab_name)
        if index != -1:
            return self.main_window.tab_widget.tabBar().tabRect(index)
        return QRect()

    def start_training(self):
        if not self.config_manager.get("skip_training", False):
            self.overlay.show()
            self.show_current_step()

    def show_current_step(self):
        if self.current_step >= len(self.training_steps):
            self.end_training()
            return

        step = self.training_steps[self.current_step]
        target_rect = step["rect"]()
        self.overlay.set_highlight(target_rect)

        global_pos = self.main_window.mapToGlobal(target_rect.bottomLeft())
        tooltip_pos = global_pos + QPoint(0, target_rect.height() + 5)
        screen_rect = QApplication.primaryScreen().geometry()
        if tooltip_pos.y() + self.tooltip.height() > screen_rect.height():
            tooltip_pos = global_pos - QPoint(0, self.tooltip.height() + 5)
        self.tooltip.move(tooltip_pos)

        self.overlay.raise_()
        self.tooltip.raise_()
        self.tooltip.show()

        # Animate the glow effect
        effect = QGraphicsOpacityEffect(self.overlay)
        self.overlay.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(1000)
        animation.setStartValue(0.5)
        animation.setEndValue(1)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start()

    def next_step(self):
        self.current_step += 1
        self.show_current_step()

    def skip_training(self):
        self.config_manager.set("skip_training", True)
        self.config_manager.apply_changes()
        self.end_training()

    def end_training(self):
        self.overlay.hide()
        self.tooltip.hide()

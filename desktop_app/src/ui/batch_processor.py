from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QProgressBar

from .components import StyledButton

# TODO: TEsting

class BatchProcessorThread(QThread):
    progress_update = Signal(int)
    log_update = Signal(str)

    def __init__(self, api_client, batch_data):
        super().__init__()
        self.api_client = api_client
        self.batch_data = batch_data

    def run(self):
        total_items = len(self.batch_data)
        for i, item in enumerate(self.batch_data, 1):
            # Process the item (e.g., create order, update inventory, etc.)
            result = self.api_client.process_batch_item(item)
            self.log_update.emit(f"Processed item {i}: {result}")
            self.progress_update.emit(int(i / total_items * 100))


class BatchProcessorWidget(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()
        self.load_button = StyledButton("Load Batch")
        self.load_button.clicked.connect(self.load_batch)
        self.process_button = StyledButton("Process Batch")
        self.process_button.clicked.connect(self.process_batch)
        controls_layout.addWidget(self.load_button)
        controls_layout.addWidget(self.process_button)
        layout.addLayout(controls_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)

        self.batch_data = None

    def load_batch(self):
        # Implement batch loading logic (e.g., file selection)
        self.batch_data = self.api_client.load_batch_data()
        self.log_display.append(f"Loaded batch with {len(self.batch_data)} items")

    def process_batch(self):
        if not self.batch_data:
            self.log_display.append("No batch data loaded")
            return

        self.process_thread = BatchProcessorThread(self.api_client, self.batch_data)
        self.process_thread.progress_update.connect(self.update_progress)
        self.process_thread.log_update.connect(self.update_log)
        self.process_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_log(self, message):
        self.log_display.append(message)

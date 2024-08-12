from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel

from .components import StyledButton

# TODO: IMplement in full
class TrainingModeWidget(QWidget):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.current_step = 0
        self.training_steps = [
            "Welcome to the training mode! Let's start with creating a new order.",
            "Great! Now let's process the order and update inventory.",
            "Next, we'll generate a shipping label for the order.",
            "Finally, let's mark the order as shipped and complete the process."
        ]
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Instructions display
        self.instructions = QLabel()
        self.instructions.setWordWrap(True)
        self.instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.instructions)

        # Action buttons
        action_layout = QHBoxLayout()
        self.prev_button = StyledButton("Previous")
        self.prev_button.clicked.connect(self.previous_step)
        self.next_button = StyledButton("Next")
        self.next_button.clicked.connect(self.next_step)
        action_layout.addWidget(self.prev_button)
        action_layout.addWidget(self.next_button)
        layout.addLayout(action_layout)

        # Training area
        self.training_area = QTextEdit()
        self.training_area.setReadOnly(True)
        layout.addWidget(self.training_area)

        self.update_training_step()

    def update_training_step(self):
        self.instructions.setText(self.training_steps[self.current_step])
        self.prev_button.setEnabled(self.current_step > 0)
        self.next_button.setEnabled(self.current_step < len(self.training_steps) - 1)
        self.training_area.clear()
        self.training_area.append(f"Step {self.current_step + 1} of {len(self.training_steps)}")

    def previous_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.update_training_step()

    def next_step(self):
        if self.current_step < len(self.training_steps) - 1:
            self.current_step += 1
            self.update_training_step()

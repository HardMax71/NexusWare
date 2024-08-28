from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QColor, QPainter, QIcon
from PySide6.QtWidgets import (QApplication, QLabel, QPushButton,
                               QVBoxLayout, QHBoxLayout,
                               QFrame)

from .utils import load_stylesheet


class QTutorialHint(QFrame):
    def __init__(self, text, current_step, total_steps, show_step_number=True, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(load_stylesheet('styles:tutorial_mode/tutorial_hint.qss'))
        self.setFocusPolicy(Qt.StrongFocus)

        layout = QVBoxLayout(self)

        if show_step_number:
            self.progress_label = QLabel(f"Step {current_step + 1} of {total_steps}")
            self.progress_label.setAlignment(Qt.AlignCenter)
            self.progress_label.setObjectName("progress_label")
            layout.addWidget(self.progress_label)

        hint_text = QLabel(text)
        hint_text.setWordWrap(True)
        layout.addWidget(hint_text)

        button_layout = QHBoxLayout()

        # Function to set button size and icon size dynamically
        def create_icon_button(icon_path):
            button = QPushButton()
            button.setIcon(QIcon(icon_path))
            button.setIconSize(button.sizeHint())
            button.setFixedSize(button.iconSize())
            return button

        self.prev_button = create_icon_button("icons:tutorial_mode/back-button.png")
        self.prev_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.next_button = create_icon_button("icons:tutorial_mode/fast-forward.png")
        self.next_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.stop_button = create_icon_button("icons:tutorial_mode/close.png")
        self.stop_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.next_button)
        layout.addLayout(button_layout)

        self.target_element = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(255, 255, 240))  # Lighter yellow for a modern look
        painter.setPen(QColor(255, 140, 0))  # Dark orange border color
        painter.drawRoundedRect(self.rect(), 15, 15)

    def set_target_element(self, element):
        self.target_element = element
        self.update_position()

    def update_position(self):
        if self.target_element and self.parent():
            element_rect = self.target_element.geometry()
            element_global_rect = QRect(self.parent().mapToGlobal(element_rect.topLeft()), element_rect.size())

            hint_pos = element_global_rect.topRight() + QPoint(20, 0)
            screen_rect = self.parent().geometry()  # Use parent window's geometry

            if hint_pos.x() + self.width() > screen_rect.right():
                hint_pos = element_global_rect.topLeft() - QPoint(self.width() + 20, 0)

            if hint_pos.y() + self.height() > screen_rect.bottom():
                hint_pos = element_global_rect.bottomRight() - QPoint(self.width(), self.height() + 20)

            if hint_pos.x() < screen_rect.left():
                hint_pos.setX(screen_rect.left() + 20)
            if hint_pos.y() < screen_rect.top():
                hint_pos.setY(screen_rect.top() + 20)

            self.move(hint_pos)

    def show(self):
        self.adjustSize()
        self.update_position()
        super().show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Right or event.key() == Qt.Key.Key_Enter:
            self.next_button.click()
        elif event.key() == Qt.Key.Key_Left:
            self.prev_button.click()
        elif event.key() == Qt.Key.Key_Escape:
            self.stop_button.click()

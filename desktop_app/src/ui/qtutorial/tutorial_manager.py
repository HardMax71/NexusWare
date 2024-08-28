from PySide6.QtCore import QTimer, QDir
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QProgressBar

from .hint import QTutorialHint
from .utils import load_stylesheet

class QTutorialManager:
    def __init__(self, parent, tutorial_steps, show_step_number=True):
        self.parent = parent
        self.tutorial_steps = tutorial_steps
        self.current_step = 0
        self.current_hint = None
        self.original_stylesheet = self.parent.styleSheet()
        self.paused = False
        self.show_step_number = show_step_number


    def start_tutorial(self):
        QTimer.singleShot(500, self.show_tutorial_step)

    def show_tutorial_step(self):
        if self.paused:
            return

        if self.current_step < len(self.tutorial_steps):
            element, text = self.tutorial_steps[self.current_step]

            # Reset the style of the previously highlighted element
            if self.current_step > 0:
                prev_element = self.tutorial_steps[self.current_step - 1][0]
                prev_element.setGraphicsEffect(None)
                prev_element.setStyleSheet("")

            highlight_effect = QGraphicsDropShadowEffect()
            highlight_effect.setColor(QColor(255, 165, 0))  # Solid orange
            highlight_effect.setOffset(0, 0)
            highlight_effect.setBlurRadius(20)
            element.setGraphicsEffect(highlight_effect)
            element.setStyleSheet(load_stylesheet('styles:tutorial_mode/highlight.qss'))

            if self.current_hint:
                self.current_hint.close()

            self.current_hint = QTutorialHint(text, self.current_step, len(self.tutorial_steps), self.show_step_number,
                                              self.parent)
            self.current_hint.next_button.clicked.connect(self.next_tutorial_step)
            self.current_hint.prev_button.clicked.connect(self.prev_tutorial_step)
            self.current_hint.stop_button.clicked.connect(self.end_tutorial)
            self.current_hint.set_target_element(element)
            self.current_hint.show()

    def next_tutorial_step(self):
        if self.current_step < len(self.tutorial_steps) - 1:
            self.current_step += 1
            self.show_tutorial_step()
        else:
            self.end_tutorial()

    def prev_tutorial_step(self):
        if self.current_step > 0:
            # Reset the style of the currently highlighted element
            current_element = self.tutorial_steps[self.current_step][0]
            current_element.setGraphicsEffect(None)
            current_element.setStyleSheet("")

            self.current_step -= 1

            # Highlight the previous element
            self.show_tutorial_step()

    def end_tutorial(self):
        for element, _ in self.tutorial_steps:
            element.setGraphicsEffect(None)
            element.setStyleSheet("")

        if self.current_hint:
            self.current_hint.close()
            self.current_hint = None

        self.current_step = 0
        self.parent.setStyleSheet(self.original_stylesheet)
        self.parent.update()

    def update_hint_position(self):
        if self.current_hint:
            self.current_hint.update_position()

    def pause_tutorial(self):
        self.paused = True
        if self.current_hint:
            self.current_hint.hide()

    def resume_tutorial(self):
        self.paused = False
        self.show_tutorial_step()

    def skip_to_step(self, step_index):
        if 0 <= step_index < len(self.tutorial_steps):
            self.current_step = step_index
            self.show_tutorial_step()

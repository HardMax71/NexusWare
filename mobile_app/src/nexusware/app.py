import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

class NexusWareMobile(toga.App):
    def __init__(self):
        super().__init__()

    def startup(self):
        # Create a main window with a title
        self.main_window = toga.MainWindow(title="NexusWare Mobile")

        # Create a main box with vertical layout
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        # Add a header label
        header_label = toga.Label(
            "NexusWare Mobile",
            style=Pack(padding=(0, 0, 20, 0), font_size=20, font_weight='bold')
        )

        # Create a button that will show a message
        self.button = toga.Button(
            'Test Connection',
            on_press=self.show_message,
            style=Pack(padding=5)
        )

        # Create a text input
        self.input = toga.TextInput(
            placeholder='Scan barcode...',
            style=Pack(padding=5)
        )

        # Add all widgets to the main box
        main_box.add(header_label)
        main_box.add(self.input)
        main_box.add(self.button)

        # Add the main box to the main window
        self.main_window.content = main_box
        self.main_window.show()

    def show_message(self, widget):
        self.main_window.info_dialog(
            'Connection Test',
            'Successfully connected to NexusWare!'
        )

def main():
    return NexusWareMobile()
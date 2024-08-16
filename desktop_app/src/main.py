import sys

from PySide6.QtCore import QFile, QTextStream, QTranslator
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import QApplication

from public_api.api import APIClient
from public_api.api import UsersAPI
from services.authentication import AuthenticationService
from services.offline_manager import OfflineManager
from services.update_manager import UpdateManager
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow
from utils.config_manager import ConfigManager
from utils.logger import setup_logger


def load_stylesheet(filename):
    file = QFile(filename)
    if file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(file)
        return stream.readAll()
    return ""


def apply_appearance_settings(app, config_manager):
    # Apply theme
    theme = config_manager.get("theme", "light")
    stylesheet = load_stylesheet(f"resources/styles/{theme}_theme.qss")
    app.setStyleSheet(stylesheet)

    # Apply font
    font_family = config_manager.get("font", "Arial")
    font_size_name = config_manager.get("font_size", "Medium")
    font = QFont(font_family)

    if font_size_name == "Small":
        font.setPointSize(8)
    elif font_size_name == "Medium":
        font.setPointSize(10)
    elif font_size_name == "Large":
        font.setPointSize(12)

    app.setFont(font)


def main():
    # Set up logging
    logger = setup_logger("nexusware")

    # Initialize the application
    app = QApplication(sys.argv)
    app.setApplicationName("NexusWare WMS")
    app.setOrganizationName("NexusWare")
    app.setOrganizationDomain("nexusware.com")

    # Set application icon
    app_icon = QIcon("resources/icons/app_icon.png")
    app.setWindowIcon(app_icon)

    # Load configuration
    config_manager = ConfigManager()

    # Apply appearance settings
    apply_appearance_settings(app, config_manager)

    # Load language
    language = config_manager.get("language", "English")
    translator = QTranslator()
    if language != "English":
        if translator.load(f"resources/translations/{language.lower()}.qm"):
            app.installTranslator(translator)

    # Initialize API client
    api_client = APIClient(base_url=config_manager.get("api_base_url", "http://127.0.0.1:8000/api/v1"))

    # Initialize services
    users_api = UsersAPI(api_client)
    auth_service = AuthenticationService(users_api)
    offline_manager = OfflineManager("offline_data.db")
    update_manager = UpdateManager(config_manager)

    # Check for updates
    if config_manager.get("auto_update", True) and update_manager.check_for_updates():
        update_manager.perform_update()

    # Show login dialog
    login_dialog = LoginDialog(auth_service)
    if login_dialog.exec() != LoginDialog.Accepted:
        sys.exit(0)

    # Set up main window
    main_window = MainWindow(api_client=api_client,
                             config_manager=config_manager)

    # Show main window
    main_window.show()

    # Start the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
import sys

from PySide6.QtCore import QFile, QTextStream
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from api.client import APIClient
from api.users import UsersAPI
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


def main():
    # Set up logging
    logger = setup_logger("nexusware")

    # Initialize the application
    app = QApplication(sys.argv)
    app.setApplicationName("NexusWare WMS")
    app.setOrganizationName("YourCompany")
    app.setOrganizationDomain("yourcompany.com")

    # Set application icon
    app_icon = QIcon("resources/icons/app_icon.png")
    app.setWindowIcon(app_icon)

    # Load configuration
    config_manager = ConfigManager()

    # Initialize API client
    api_client = APIClient()

    # Initialize services
    users_api = UsersAPI(api_client)
    auth_service = AuthenticationService(users_api)
    offline_manager = OfflineManager("offline_data.db")
    update_manager = UpdateManager(config_manager)

    # Check for updates
    if update_manager.check_for_updates():
        # Handle update process (e.g., show update dialog)
        pass

    # Show login dialog
    login_dialog = LoginDialog(auth_service)
    if login_dialog.exec() != LoginDialog.Accepted:
        sys.exit(0)

    # Set up main window
    main_window = MainWindow(api_client)

    # Load stylesheet
    theme = config_manager.get("theme", "light")
    stylesheet = load_stylesheet(f"resources/styles/{theme}_theme.qss")
    app.setStyleSheet(stylesheet)

    # Show main window
    main_window.show()

    # Start the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
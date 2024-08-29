import sys

from PySide6.QtCore import QFile, QTextStream, QTranslator, QDir
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import QApplication, QMessageBox
from requests import HTTPError

from desktop_app.src.ui.components import IconPath
from public_api.api import APIClient, UsersAPI
from services import OfflineManager, UpdateManager
from ui.components.dialogs.error_dialog import global_exception_handler
from ui.main_window import MainWindow
from ui.views.auth import LoginDialog
from utils import ConfigManager, setup_logger


class AppContext:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.logger = setup_logger("nexusware")
        self.api_client = APIClient(base_url=self.config_manager.get("api_base_url",
                                                                     "http://127.0.0.1:8000/api/v1"))
        self.users_api = UsersAPI(self.api_client)
        self.offline_manager = OfflineManager("offline_data.db")
        self.update_manager = UpdateManager(self.config_manager)

    def initialize_app(self):
        app = QApplication(sys.argv)
        app.setApplicationName("NexusWare WMS")
        app.setOrganizationName("NexusWare")
        app.setOrganizationDomain(self.config_manager.get("organization_domain", "nexusware.com"))

        QDir.addSearchPath("icons", self.config_manager.get("icons_path", "resources/icons"))
        QDir.addSearchPath("styles", self.config_manager.get("styles_path", "resources/styles"))
        QDir.addSearchPath("templates", self.config_manager.get("templates_path",
                                                                "resources/templates"))
        QDir.addSearchPath("translations", self.config_manager.get("translations_path",
                                                                   "resources/translations"))

        app_icon = QIcon(IconPath.APP_ICON)
        app.setWindowIcon(app_icon)
        self.apply_appearance_settings(app)

        language = self.config_manager.get("language", "English")
        translator = QTranslator()
        if language != "English":
            if translator.load(f"translations:{language.lower()}.qm"):
                app.installTranslator(translator)

        return app

    def apply_appearance_settings(self, app):
        theme = self.config_manager.get("theme", "light")
        stylesheet = self.load_stylesheet(f"styles:{theme}_theme.qss")
        app.setStyleSheet(stylesheet)

        font_family = self.config_manager.get("font", "Arial")
        font_size_name = self.config_manager.get("font_size", "Medium")
        font = QFont(font_family)

        if font_size_name == "Small":
            font.setPointSize(8)
        elif font_size_name == "Medium":
            font.setPointSize(10)
        elif font_size_name == "Large":
            font.setPointSize(12)

        app.setFont(font)

    def load_stylesheet(self, filename):
        file = QFile(filename)
        if file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(file)
            return stream.readAll()
        return ""

    def create_and_show_main_window(self):
        user_permissions = self.users_api.get_current_user_permissions()
        main_window = MainWindow(api_client=self.api_client,
                                 config_manager=self.config_manager,
                                 permission_manager=user_permissions)
        main_window.show()
        return main_window


def main():
    app_context = AppContext()
    app_context.logger.info("Starting NexusWare WMS")

    app = app_context.initialize_app()

    sys.excepthook = global_exception_handler(app_context)

    app_context.offline_manager.clear_all_actions()

    if app_context.config_manager.get("auto_update", True) and app_context.update_manager.check_for_updates():
        app_context.update_manager.perform_update()

    login_dialog = LoginDialog(app_context.users_api)
    if login_dialog.exec() != LoginDialog.Accepted:
        sys.exit(0)

    try:
        main_window = app_context.create_and_show_main_window()  # noqa

        show_manual = app_context.config_manager.get("show_manual_after_login", True)
        if show_manual:
            main_window.open_user_manual()

    except HTTPError as e:
        print(e)
        QMessageBox.critical(None, "Error", str(e))

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

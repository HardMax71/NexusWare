import psutil
import requests
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QProgressBar, QHBoxLayout
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from src.ui.components import StyledButton, StyledLabel
from public_api.api import APIClient


class SystemDiagnosticsWidget(QWidget):
    def __init__(self, config_manager, api_client: APIClient, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.api_client = api_client
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()
        self.run_diagnostics_button = StyledButton("Run Diagnostics")
        self.run_diagnostics_button.clicked.connect(self.run_diagnostics)
        controls_layout.addWidget(self.run_diagnostics_button)

        self.clear_button = StyledButton("Clear")
        self.clear_button.clicked.connect(self.clear_diagnostics)
        controls_layout.addWidget(self.clear_button)

        layout.addLayout(controls_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Diagnostics display
        self.diagnostics_display = QTextEdit()
        self.diagnostics_display.setReadOnly(True)
        layout.addWidget(self.diagnostics_display)

        # System info
        self.cpu_label = StyledLabel("CPU Usage: N/A")
        self.memory_label = StyledLabel("Memory Usage: N/A")
        self.disk_label = StyledLabel("Disk Usage: N/A")
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.memory_label)
        layout.addWidget(self.disk_label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_diagnostics)

    def run_diagnostics(self):
        self.diagnostics_display.clear()
        self.progress_bar.setValue(0)
        self.timer.start(1000)  # Update every second
        self.run_diagnostics_button.setEnabled(False)

    def clear_diagnostics(self):
        self.diagnostics_display.clear()
        self.progress_bar.setValue(0)
        self.cpu_label.setText("CPU Usage: N/A")
        self.memory_label.setText("Memory Usage: N/A")
        self.disk_label.setText("Disk Usage: N/A")

    def update_diagnostics(self):
        progress = self.progress_bar.value()
        if progress < 100:
            progress += 10
            self.progress_bar.setValue(progress)

            if progress == 10:
                self.add_diagnostic("Checking database connection...")
                self.check_database_connection()
            elif progress == 30:
                self.add_diagnostic("Verifying API endpoints...")
                self.verify_api_endpoints()
            elif progress == 70:
                self.add_diagnostic("Analyzing system performance...")
                self.analyze_system_performance()
            elif progress == 90:
                self.add_diagnostic("Generating final report...")
                self.generate_final_report()
        else:
            self.timer.stop()
            self.add_diagnostic("Diagnostics complete.")
            self.run_diagnostics_button.setEnabled(True)

    def add_diagnostic(self, message):
        self.diagnostics_display.append(message)

    def check_database_connection(self):
        try:
            # Assuming the database URL is stored in the config
            db_url = self.config_manager.get("database_url", "sqlite:///./test.db")
            engine = create_engine(db_url)
            with engine.connect() as connection:
                result = connection.execute("SELECT 1")
                if result.scalar() == 1:
                    self.add_diagnostic("Database connection: OK")
                else:
                    self.add_diagnostic("Database connection: Failed")
        except SQLAlchemyError as e:
            self.add_diagnostic(f"Database connection error: {str(e)}")

    def verify_api_endpoints(self):
        test_url = self.config_manager.get("api_test_url", "http://127.0.0.1:8000/")
        timeout = self.config_manager.get("request_timeout", 10)

        try:
            response = requests.get(test_url, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                if data.get('message') == "Welcome to NexusWare WMS API":
                    self.add_diagnostic("API endpoints: Verified")
                else:
                    self.add_diagnostic("API endpoints: Connected, but unexpected response")
            else:
                self.add_diagnostic(f"API endpoints: Failed. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.add_diagnostic(f"API endpoints: Error - {str(e)}")

    def analyze_system_performance(self):
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        self.cpu_label.setText(f"CPU Usage: {cpu_percent}%")
        self.memory_label.setText(f"Memory Usage: {memory.percent}%")
        self.disk_label.setText(f"Disk Usage: {disk.percent}%")

        self.add_diagnostic(f"CPU Usage: {cpu_percent}%")
        self.add_diagnostic(f"Memory Usage: {memory.percent}%")
        self.add_diagnostic(f"Disk Usage: {disk.percent}%")

    def generate_final_report(self):
        self.add_diagnostic("System Configuration:")
        self.add_diagnostic(f"- Theme: {self.config_manager.get('theme', 'light').capitalize()}")
        self.add_diagnostic(f"- Font: {self.config_manager.get('font', 'Arial')}")
        self.add_diagnostic(f"- Font Size: {self.config_manager.get('font_size', 'Medium')}")
        self.add_diagnostic(f"- Language: {self.config_manager.get('language', 'English')}")
        self.add_diagnostic(
            f"- Auto Update: {'Enabled' if self.config_manager.get('auto_update', True) else 'Disabled'}")
        self.add_diagnostic(
            f"- Start on Startup: {'Enabled' if self.config_manager.get('start_on_startup', False) else 'Disabled'}")
        self.add_diagnostic(
            f"- API Base URL: {self.config_manager.get('api_base_url', 'http://127.0.0.1:8000/api/v1')}")
        self.add_diagnostic(f"- Request Timeout: {self.config_manager.get('request_timeout', 10)} seconds")
        self.add_diagnostic(f"- Log Level: {self.config_manager.get('log_level', 'INFO')}")
        self.add_diagnostic(f"- Cache Size: {self.config_manager.get('cache_size', 200)} MB")
        self.add_diagnostic(
            f"- Two-Factor Auth: {'Enabled' if self.config_manager.get('two_factor_auth', False) else 'Disabled'}")
        self.add_diagnostic(
            f"- Data Encryption: {'Enabled' if self.config_manager.get('data_encryption', True) else 'Disabled'}")
        self.add_diagnostic(f"- Min Password Strength: {self.config_manager.get('min_password_strength', 'Medium')}")

    def showEvent(self, event):
        super().showEvent(event)
        self.analyze_system_performance()

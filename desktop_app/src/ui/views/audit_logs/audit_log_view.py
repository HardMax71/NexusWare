from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QDateEdit, QLabel, QSplitter
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QValueAxis, QBarCategoryAxis

from src.ui.components import StyledButton
from src.ui.components.icon_path import IconPath
from public_api.api import APIClient, AuditAPI

class AuditLogView(QWidget):
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.audit_log_api = AuditAPI(api_client)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()
        self.start_date = QDateEdit(QDate.currentDate().addDays(-7))
        self.end_date = QDateEdit(QDate.currentDate())
        self.refresh_button = StyledButton("Refresh", icon_path=IconPath.REFRESH)
        self.refresh_button.clicked.connect(self.refresh_data)
        controls_layout.addWidget(QLabel("Start Date:"))
        controls_layout.addWidget(self.start_date)
        controls_layout.addWidget(QLabel("End Date:"))
        controls_layout.addWidget(self.end_date)
        controls_layout.addWidget(self.refresh_button)
        layout.addLayout(controls_layout)

        # Charts
        splitter = QSplitter()
        layout.addWidget(splitter)

        self.action_chart_view = QChartView()
        self.table_chart_view = QChartView()
        self.user_chart_view = QChartView()

        splitter.addWidget(self.action_chart_view)
        splitter.addWidget(self.table_chart_view)
        splitter.addWidget(self.user_chart_view)

        # Total logs label
        self.total_logs_label = QLabel()
        layout.addWidget(self.total_logs_label)

        self.refresh_data()

    def refresh_data(self):
        start_date_timestamp = int(self.start_date.dateTime().toSecsSinceEpoch())
        end_date_timestamp = int(self.end_date.dateTime().toSecsSinceEpoch())

        audit_summary = self.audit_log_api.get_audit_summary(start_date_timestamp, end_date_timestamp)

        self.update_total_logs(audit_summary.total_logs)
        self.update_action_chart(audit_summary.logs_by_action)
        self.update_table_chart(audit_summary.logs_by_table)
        self.update_user_chart(audit_summary.most_active_users)

    def update_total_logs(self, total_logs):
        self.total_logs_label.setText(f"Total Logs: {total_logs}")

    def update_action_chart(self, logs_by_action):
        series = QPieSeries()
        for action, count in logs_by_action.items():
            series.append(action, count)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Logs by Action")
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignRight)

        self.action_chart_view.setChart(chart)

    def update_table_chart(self, logs_by_table):
        series = QBarSeries()
        bar_set = QBarSet("Logs")

        categories = []
        for table, count in logs_by_table.items():
            bar_set.append(count)
            categories.append(table)

        series.append(bar_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Logs by Table")

        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

        chart.legend().setVisible(False)

        self.table_chart_view.setChart(chart)

    def update_user_chart(self, most_active_users):
        series = QBarSeries()
        bar_set = QBarSet("Actions")

        categories = []
        for user in most_active_users:
            bar_set.append(user.total_actions)
            categories.append(user.username)

        series.append(bar_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Most Active Users")

        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

        chart.legend().setVisible(False)

        self.user_chart_view.setChart(chart)
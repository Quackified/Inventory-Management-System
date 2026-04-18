"""
dashboard_handler.py — Business logic for the dashboard screen.
"""

from models import dashboard_model


class DashboardHandler:
    """Fetches summary stats and recent transactions, pushes data to the screen."""

    def __init__(self, view):
        self.view = view  # DashboardScreen instance

    def refresh(self):
        """Pull fresh data from the database and update the screen."""
        stats = dashboard_model.get_summary()
        self.view.update_cards(stats)

        recent = dashboard_model.get_recent_transactions(limit=10)
        self.view.populate_recent(recent)

        wh_summary = dashboard_model.get_warehouse_summary()
        self.view.populate_warehouse_summary(wh_summary)

        chart_data = dashboard_model.get_chart_data(
            period=self.view._chart_period
        )
        self.view.update_chart(chart_data)

    def refresh_chart(self, period):
        """Reload only the chart data for the given period."""
        chart_data = dashboard_model.get_chart_data(period=period)
        self.view.update_chart(chart_data)

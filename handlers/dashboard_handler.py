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

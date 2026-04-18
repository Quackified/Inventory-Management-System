"""
transactions_handler.py — Business logic for transaction log viewing and export.
"""

from tkinter import filedialog
from gui.dialogs import show_success, show_error
from models import transaction_model, warehouse_model, export_model


class TransactionsHandler:
    """Loads and filters transaction logs for the transactions screen."""

    def __init__(self, view, controller):
        self.view = view
        self.controller = controller

    def refresh(self):
        """Load warehouses for the filter dropdown and all transactions."""
        wh_rows = warehouse_model.get_all_active()
        self.view.populate_warehouses(wh_rows)

        self.apply_filters()

    def apply_filters(self, page=None, page_size=None):
        """Get filter values from the view and reload filtered data."""
        filters = self.view.get_filters()

        if page is None:
            page, page_size = self.view.pager.get_state()

        # Get total count for pagination
        total = transaction_model.get_total_count(
            warehouse_id=filters["warehouse_id"],
            search_term=filters["search_term"],
            txn_type=filters["txn_type"],
            date_from=filters["date_from"],
            date_to=filters["date_to"],
        )
        self.view.pager.set_total(total)

        # Get page of data
        transactions = transaction_model.get_all(
            warehouse_id=filters["warehouse_id"],
            search_term=filters["search_term"],
            txn_type=filters["txn_type"],
            date_from=filters["date_from"],
            date_to=filters["date_to"],
            page=page,
            page_size=page_size,
        )
        self.view.populate_table(transactions)

    def export(self, fmt):
        """Export current filtered transaction logs to CSV or Excel."""
        root = self.view.winfo_toplevel()
        filters = self.view.get_filters()

        if fmt == "csv":
            filetypes = [("CSV files", "*.csv")]
            default_ext = ".csv"
        else:
            filetypes = [("Excel files", "*.xlsx")]
            default_ext = ".xlsx"

        filepath = filedialog.asksaveasfilename(
            title="Export Transactions",
            defaultextension=default_ext,
            filetypes=filetypes
        )
        if not filepath:
            return

        if fmt == "csv":
            success, msg = export_model.export_transactions_csv(
                filepath,
                warehouse_id=filters["warehouse_id"],
                search_term=filters["search_term"],
                txn_type=filters["txn_type"],
                date_from=filters["date_from"],
                date_to=filters["date_to"],
            )
        else:
            success, msg = export_model.export_transactions_xlsx(
                filepath,
                warehouse_id=filters["warehouse_id"],
                search_term=filters["search_term"],
                txn_type=filters["txn_type"],
                date_from=filters["date_from"],
                date_to=filters["date_to"],
            )

        if success:
            show_success(root, "Export Complete", msg)
        else:
            show_error(root, "Export Error", msg)

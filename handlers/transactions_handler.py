"""
transactions_handler.py — Business logic for transaction log viewing and export.
"""

from tkinter import messagebox, filedialog
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

        transactions = transaction_model.get_all()
        self.view.populate_table(transactions)

    def apply_filters(self):
        """Get filter values from the view and reload filtered data."""
        filters = self.view.get_filters()

        transactions = transaction_model.get_all(
            warehouse_id=filters["warehouse_id"],
            search_term=filters["search_term"],
            txn_type=filters["txn_type"],
            date_from=filters["date_from"],
            date_to=filters["date_to"],
        )
        self.view.populate_table(transactions)

    def export(self, fmt):
        """Export current filtered transaction logs to CSV or Excel."""
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
            messagebox.showinfo("Export Complete", msg)
        else:
            messagebox.showerror("Export Error", msg)

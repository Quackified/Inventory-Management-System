"""
transactions_handler.py — Business logic for inventory transactions.
"""

from tkinter import messagebox
from models import transaction_model


class TransactionsHandler:
    """Validates transaction input, enforces stock guard, records via model."""

    def __init__(self, view, controller):
        self.view = view              # TransactionsScreen instance
        self.controller = controller  # App instance (for current_user)

    def refresh(self):
        """Reload the product dropdown and transaction history."""
        products = transaction_model.get_products_for_dropdown()
        self.view.populate_products(products)

        transactions = transaction_model.get_all()
        self.view.populate_table(transactions)

    def record(self):
        """Validate input, check stock, and record the transaction."""
        data = self.view.get_form_data()

        # --- Input validation ---
        if not data["product_id"]:
            messagebox.showwarning("Validation", "Please select a product.")
            return

        qty_str = data["quantity"]
        if not qty_str.isdigit() or int(qty_str) <= 0:
            messagebox.showwarning("Validation",
                                   "Quantity must be a positive integer.")
            return

        product_id = data["product_id"]
        txn_type = data["txn_type"]
        quantity = int(qty_str)
        remarks = data["remarks"]

        # Get user_id from current session
        user = self.controller.current_user
        user_id = user["user_id"] if user else 1

        # --- Stock guard for Stock-Out ---
        if txn_type == "Stock-Out":
            current_stock = transaction_model.get_current_stock(product_id)
            if current_stock is None:
                messagebox.showerror("Error", "Product not found.")
                return
            if quantity > current_stock:
                messagebox.showwarning(
                    "Insufficient Stock",
                    f"Only {current_stock} unit(s) available. "
                    f"Cannot stock-out {quantity}."
                )
                return

        # --- Record via model ---
        success, msg = transaction_model.record(
            product_id, user_id, txn_type, quantity, remarks
        )

        if success:
            messagebox.showinfo("Success", msg)
            self.view.clear_form()
            self.refresh()
        else:
            messagebox.showerror("DB Error", msg)

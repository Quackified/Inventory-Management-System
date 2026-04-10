"""
products_handler.py — Business logic for product CRUD operations.
"""

from tkinter import messagebox
from models import product_model


class ProductsHandler:
    """Validates form input, calls product model, refreshes the screen table."""

    def __init__(self, view):
        self.view = view  # ProductsScreen instance

    def refresh(self):
        """Reload all products into the Treeview."""
        rows = product_model.get_all()
        self.view.populate_table(rows)

    def search(self):
        """Filter products based on the search bar text."""
        term = self.view.get_search_term()
        rows = product_model.get_all(search_term=term if term else None)
        self.view.populate_table(rows)

    def add(self):
        """Validate and add a new product."""
        data = self._validate()
        if not data:
            return

        success, msg = product_model.add(
            data["name"], data["description"], data["stock"], data["unit"]
        )
        if success:
            messagebox.showinfo("Success", msg)
            self.view.clear_fields()
            self.refresh()
        else:
            messagebox.showerror("DB Error", msg)

    def update(self):
        """Validate and update the selected product."""
        product_id = self.view.get_selected_id()
        if not product_id:
            messagebox.showwarning("Selection",
                                   "Select a product from the table first.")
            return

        data = self._validate()
        if not data:
            return

        success, msg = product_model.update(
            product_id, data["name"], data["description"],
            data["stock"], data["unit"]
        )
        if success:
            messagebox.showinfo("Success", msg)
            self.view.clear_fields()
            self.refresh()
        else:
            messagebox.showerror("DB Error", msg)

    def delete(self):
        """Delete the selected product after confirmation."""
        product_id = self.view.get_selected_id()
        if not product_id:
            messagebox.showwarning("Selection",
                                   "Select a product from the table first.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete product #{product_id}?"
        )
        if not confirm:
            return

        success, msg = product_model.delete(product_id)
        if success:
            messagebox.showinfo("Success", msg)
            self.view.clear_fields()
            self.refresh()
        else:
            messagebox.showerror("DB Error", msg)

    # ── Input validation ─────────────────────────────────────
    def _validate(self):
        """
        Validate form data.

        Returns:
            dict with 'name', 'description', 'stock', 'unit' or None on failure.
        """
        data = self.view.get_form_data()

        if not data["name"]:
            messagebox.showwarning("Validation", "Product name is required.")
            return None

        if not data["stock"].isdigit():
            messagebox.showwarning("Validation",
                                   "Stock must be a non-negative integer.")
            return None

        data["stock"] = int(data["stock"])
        data["unit"] = data["unit"] if data["unit"] else "pcs"
        return data

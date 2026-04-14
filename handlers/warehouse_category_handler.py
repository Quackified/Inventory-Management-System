"""
warehouse_category_handler.py — Business logic for warehouse & category CRUD.
"""

from tkinter import messagebox
from models import warehouse_model, category_model


class WarehouseCategoryHandler:
    """Orchestrates CRUD for both warehouses and categories."""

    def __init__(self, view):
        self.view = view

    def refresh(self):
        """Reload both tables."""
        wh_rows = warehouse_model.get_all()
        self.view.populate_warehouses(wh_rows)

        cat_rows = category_model.get_all()
        self.view.populate_categories(cat_rows)

    # ── Warehouse CRUD ───────────────────────────────────────
    def add_warehouse(self, name, location):
        if not name:
            messagebox.showwarning("Validation", "Warehouse name is required.")
            return
        success, msg = warehouse_model.add(name, location)
        if success:
            messagebox.showinfo("Success", msg)
            self.refresh()
        else:
            messagebox.showerror("DB Error", msg)

    def update_warehouse(self, wh_id, name, location, is_active):
        if not name:
            messagebox.showwarning("Validation", "Warehouse name is required.")
            return
        success, msg = warehouse_model.update(wh_id, name, location, is_active)
        if success:
            messagebox.showinfo("Success", msg)
            self.refresh()
        else:
            messagebox.showerror("DB Error", msg)

    def delete_warehouse(self):
        sel = self.view.get_selected_warehouse()
        if not sel:
            messagebox.showwarning("Selection", "Select a warehouse first.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete warehouse '{sel[1]}'?\n"
            "Products under this warehouse will be unlinked."
        )
        if not confirm:
            return

        success, msg = warehouse_model.delete(sel[0])
        if success:
            messagebox.showinfo("Success", msg)
            self.refresh()
        else:
            messagebox.showerror("DB Error", msg)

    # ── Category CRUD ────────────────────────────────────────
    def add_category(self, name, description):
        if not name:
            messagebox.showwarning("Validation", "Category name is required.")
            return
        success, msg = category_model.add(name, description)
        if success:
            messagebox.showinfo("Success", msg)
            self.refresh()
        else:
            messagebox.showerror("DB Error", msg)

    def update_category(self, cat_id, name, description):
        if not name:
            messagebox.showwarning("Validation", "Category name is required.")
            return
        success, msg = category_model.update(cat_id, name, description)
        if success:
            messagebox.showinfo("Success", msg)
            self.refresh()
        else:
            messagebox.showerror("DB Error", msg)

    def delete_category(self):
        sel = self.view.get_selected_category()
        if not sel:
            messagebox.showwarning("Selection", "Select a category first.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete category '{sel[1]}'?\n"
            "Products under this category will be unlinked."
        )
        if not confirm:
            return

        success, msg = category_model.delete(sel[0])
        if success:
            messagebox.showinfo("Success", msg)
            self.refresh()
        else:
            messagebox.showerror("DB Error", msg)

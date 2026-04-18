"""
warehouse_category_handler.py — Business logic for warehouse & category CRUD.
"""

from gui.dialogs import show_success, show_warning, show_error, show_confirm
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
        root = self.view.winfo_toplevel()
        if not name:
            show_warning(root, "Validation", "Warehouse name is required.")
            return
        success, msg = warehouse_model.add(name, location)
        if success:
            show_success(root, "Warehouse Added", msg)
            self.refresh()
        else:
            show_error(root, "Database Error", msg)

    def update_warehouse(self, wh_id, name, location, is_active):
        root = self.view.winfo_toplevel()
        if not name:
            show_warning(root, "Validation", "Warehouse name is required.")
            return
        success, msg = warehouse_model.update(wh_id, name, location, is_active)
        if success:
            show_success(root, "Warehouse Updated", msg)
            self.refresh()
        else:
            show_error(root, "Database Error", msg)

    def delete_warehouse(self):
        root = self.view.winfo_toplevel()
        sel = self.view.get_selected_warehouse()
        if not sel:
            show_warning(root, "Selection", "Select a warehouse first.")
            return

        confirm = show_confirm(
            root, "Confirm Delete",
            f"Delete warehouse '{sel[1]}'?\n"
            "Products under this warehouse will be unlinked."
        )
        if not confirm:
            return

        success, msg = warehouse_model.delete(sel[0])
        if success:
            show_success(root, "Warehouse Deleted", msg)
            self.refresh()
        else:
            show_error(root, "Database Error", msg)

    # ── Category CRUD ────────────────────────────────────────
    def add_category(self, name, description):
        root = self.view.winfo_toplevel()
        if not name:
            show_warning(root, "Validation", "Category name is required.")
            return
        success, msg = category_model.add(name, description)
        if success:
            show_success(root, "Category Added", msg)
            self.refresh()
        else:
            show_error(root, "Database Error", msg)

    def update_category(self, cat_id, name, description):
        root = self.view.winfo_toplevel()
        if not name:
            show_warning(root, "Validation", "Category name is required.")
            return
        success, msg = category_model.update(cat_id, name, description)
        if success:
            show_success(root, "Category Updated", msg)
            self.refresh()
        else:
            show_error(root, "Database Error", msg)

    def delete_category(self):
        root = self.view.winfo_toplevel()
        sel = self.view.get_selected_category()
        if not sel:
            show_warning(root, "Selection", "Select a category first.")
            return

        confirm = show_confirm(
            root, "Confirm Delete",
            f"Delete category '{sel[1]}'?\n"
            "Products under this category will be unlinked."
        )
        if not confirm:
            return

        success, msg = category_model.delete(sel[0])
        if success:
            show_success(root, "Category Deleted", msg)
            self.refresh()
        else:
            show_error(root, "Database Error", msg)

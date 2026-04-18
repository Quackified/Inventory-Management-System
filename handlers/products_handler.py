"""
products_handler.py — Business logic for product CRUD and stock transactions.
"""

from tkinter import filedialog
from gui.dialogs import show_success, show_warning, show_error, show_confirm
from models import product_model, transaction_model, warehouse_model, category_model
from models import export_model
from gui.popover import Popover


class ProductsHandler:
    """Validates form input, calls product model, manages popovers."""

    def __init__(self, view, controller):
        self.view = view
        self.controller = controller

    def refresh(self, page=None, page_size=None):
        """Load products with optional pagination."""
        term = self.view.get_search_term() or None

        if page is None:
            page, page_size = self.view.pager.get_state()

        total = product_model.get_total_count(search_term=term)
        self.view.pager.set_total(total)

        rows = product_model.get_page(page=page, page_size=page_size,
                                       search_term=term)
        self.view.populate_table(rows)

    def search(self):
        self.view.pager.reset()
        self.refresh()

    def delete(self):
        pid = self.view.get_selected_id()
        root = self.view.winfo_toplevel()

        if not pid:
            show_warning(root, "Selection",
                         "Select a product from the table first.")
            return

        confirm = show_confirm(
            root, "Confirm Delete",
            f"Are you sure you want to delete product #{pid}?"
        )
        if not confirm:
            return

        success, msg = product_model.delete(pid)
        if success:
            show_success(root, "Deleted", msg)
            self.refresh()
        else:
            show_error(root, "Database Error", msg)

    # ── Popover: Add ─────────────────────────────────────────
    def open_add_popover(self):
        root = self.view.winfo_toplevel()
        pop = Popover(root, title="Add Product", width=520, height=540)

        e_name = pop.add_field("Name:")
        e_desc = pop.add_field("Description:")
        e_stock = pop.add_field("Initial Stock:", default="0")
        e_unit = pop.add_field("Unit:", default="pcs")

        # Warehouse dropdown
        wh_rows = warehouse_model.get_all_active()
        wh_names = [f"{r[0]}:{r[1]}" for r in wh_rows]
        cmb_wh = pop.add_dropdown("Warehouse:", values=["(None)"] + wh_names)

        # Category dropdown
        cat_rows = category_model.get_all()
        cat_names = [f"{r[0]}:{r[1]}" for r in cat_rows]
        cmb_cat = pop.add_dropdown("Category:", values=["(None)"] + cat_names)

        e_threshold = pop.add_field("Low Stock Alert:", default="10")
        e_expiry = pop.add_field("Expiry Date:", default="YYYY-MM-DD")
        e_mfg = pop.add_field("Manufactured:", default="YYYY-MM-DD")
        e_batch = pop.add_field("Batch Number:")

        def on_save():
            data = self._collect_popover_data(
                e_name, e_desc, e_stock, e_unit,
                cmb_wh, cmb_cat, e_threshold, e_expiry, e_mfg, e_batch
            )
            if not data:
                return

            success, msg = product_model.add(**data)
            if success:
                show_success(root, "Product Added", msg)
                pop.close()
                self.refresh()
            else:
                show_error(root, "Database Error", msg)

        pop.add_button("Save", command=on_save, style="success")
        pop.add_button("Cancel", command=pop.close, style="secondary")

    # ── Popover: Edit ────────────────────────────────────────
    def open_edit_popover(self):
        pid = self.view.get_selected_id()
        root = self.view.winfo_toplevel()

        if not pid:
            show_warning(root, "Selection",
                         "Select a product from the table first.")
            return

        product = product_model.get_by_id(pid)
        if not product:
            show_error(root, "Error", "Product not found.")
            return

        pop = Popover(root, title=f"Edit Product #{pid}", width=520, height=540)

        e_name = pop.add_field("Name:", default=product["name"])
        e_desc = pop.add_field("Description:",
                               default=product.get("description") or "")
        e_stock = pop.add_field("Stock:", default=str(product["current_stock"]))
        e_unit = pop.add_field("Unit:", default=product.get("unit") or "pcs")

        # Warehouse dropdown
        wh_rows = warehouse_model.get_all_active()
        wh_names = [f"{r[0]}:{r[1]}" for r in wh_rows]
        wh_default = ""
        if product.get("warehouse_id"):
            for r in wh_rows:
                if r[0] == product["warehouse_id"]:
                    wh_default = f"{r[0]}:{r[1]}"
        cmb_wh = pop.add_dropdown("Warehouse:",
                                   values=["(None)"] + wh_names,
                                   default=wh_default or "(None)")

        # Category dropdown
        cat_rows = category_model.get_all()
        cat_names = [f"{r[0]}:{r[1]}" for r in cat_rows]
        cat_default = ""
        if product.get("category_id"):
            for r in cat_rows:
                if r[0] == product["category_id"]:
                    cat_default = f"{r[0]}:{r[1]}"
        cmb_cat = pop.add_dropdown("Category:",
                                    values=["(None)"] + cat_names,
                                    default=cat_default or "(None)")

        e_threshold = pop.add_field("Low Stock Alert:",
                                     default=str(product.get("low_stock_threshold", 10)))
        e_expiry = pop.add_field("Expiry Date:",
                                  default=str(product["expiry_date"]) if product.get("expiry_date") else "")
        e_mfg = pop.add_field("Manufactured:",
                               default=str(product["manufactured_date"]) if product.get("manufactured_date") else "")
        e_batch = pop.add_field("Batch Number:",
                                 default=product.get("batch_number") or "")

        def on_save():
            data = self._collect_popover_data(
                e_name, e_desc, e_stock, e_unit,
                cmb_wh, cmb_cat, e_threshold, e_expiry, e_mfg, e_batch
            )
            if not data:
                return

            success, msg = product_model.update(pid, **data)
            if success:
                show_success(root, "Product Updated", msg)
                pop.close()
                self.refresh()
            else:
                show_error(root, "Database Error", msg)

        pop.add_button("Save", command=on_save, style="success")
        pop.add_button("Cancel", command=pop.close, style="secondary")

    # ── Popover: Stock-In / Stock-Out ────────────────────────
    def open_stock_popover(self, txn_type):
        pid = self.view.get_selected_id()
        if not pid:
            return

        root = self.view.winfo_toplevel()
        current_stock = product_model.get_current_stock(pid)
        pop = Popover(root, title=f"{txn_type} — Product #{pid}",
                      width=440, height=300)

        e_qty = pop.add_field("Quantity:")

        wh_rows = warehouse_model.get_all_active()
        wh_names = [f"{r[0]}:{r[1]}" for r in wh_rows]
        cmb_wh = pop.add_dropdown("Warehouse:", values=["(None)"] + wh_names)

        e_remarks = pop.add_field("Remarks:")

        import tkinter as tk
        from config import FONT_FAMILY, WHITE, TEXT_MUTED
        tk.Label(pop.body, text=f"Current stock: {current_stock}",
                 font=(FONT_FAMILY, 9), fg=TEXT_MUTED,
                 bg=WHITE).pack(anchor="w", pady=(6, 0))

        def on_record():
            qty_str = e_qty.get().strip()
            if not qty_str.isdigit() or int(qty_str) <= 0:
                show_warning(root, "Validation",
                             "Quantity must be a positive integer.")
                return

            quantity = int(qty_str)

            if txn_type == "Stock-Out":
                if current_stock is None:
                    show_error(root, "Error", "Product not found.")
                    return
                if quantity > current_stock:
                    show_warning(root, "Insufficient Stock",
                                 f"Only {current_stock} unit(s) available.")
                    return

            wh_val = cmb_wh.get()
            wh_id = None
            if wh_val and wh_val != "(None)":
                wh_id = int(wh_val.split(":")[0])

            user = self.controller.current_user
            user_id = user["user_id"] if user else 1
            remarks = e_remarks.get().strip()

            success, msg = transaction_model.record(
                pid, user_id, txn_type, quantity, remarks, wh_id
            )
            if success:
                show_success(root, "Transaction Recorded", msg)
                pop.close()
                self.refresh()
            else:
                show_error(root, "Database Error", msg)

        pop.add_button("Record", command=on_record, style="success")
        pop.add_button("Cancel", command=pop.close, style="secondary")

    # ── Data collection helper ───────────────────────────────
    def _collect_popover_data(self, e_name, e_desc, e_stock, e_unit,
                               cmb_wh, cmb_cat, e_threshold,
                               e_expiry, e_mfg, e_batch):
        """Validate and return dict of product fields, or None on failure."""
        root = self.view.winfo_toplevel()

        name = e_name.get().strip()
        if not name:
            show_warning(root, "Validation", "Product name is required.")
            return None

        stock_str = e_stock.get().strip()
        if not stock_str.isdigit():
            show_warning(root, "Validation",
                         "Stock must be a non-negative integer.")
            return None

        threshold_str = e_threshold.get().strip()
        if not threshold_str.isdigit():
            show_warning(root, "Validation",
                         "Low stock threshold must be a number.")
            return None

        # Resolve warehouse_id
        wh_val = cmb_wh.get()
        wh_id = None
        if wh_val and wh_val != "(None)":
            try:
                wh_id = int(wh_val.split(":")[0])
            except ValueError:
                pass

        # Resolve category_id
        cat_val = cmb_cat.get()
        cat_id = None
        if cat_val and cat_val != "(None)":
            try:
                cat_id = int(cat_val.split(":")[0])
            except ValueError:
                pass

        # Dates
        expiry = e_expiry.get().strip()
        if expiry in ("", "YYYY-MM-DD"):
            expiry = None

        mfg = e_mfg.get().strip()
        if mfg in ("", "YYYY-MM-DD"):
            mfg = None

        batch = e_batch.get().strip() or None

        return {
            "name": name,
            "description": e_desc.get().strip(),
            "stock": int(stock_str),
            "unit": e_unit.get().strip() or "pcs",
            "warehouse_id": wh_id,
            "category_id": cat_id,
            "low_stock_threshold": int(threshold_str),
            "expiry_date": expiry,
            "manufactured_date": mfg,
            "batch_number": batch,
        }

    # ── Export ───────────────────────────────────────────────
    def export(self, fmt):
        root = self.view.winfo_toplevel()

        if fmt == "csv":
            filetypes = [("CSV files", "*.csv")]
            default_ext = ".csv"
        else:
            filetypes = [("Excel files", "*.xlsx")]
            default_ext = ".xlsx"

        filepath = filedialog.asksaveasfilename(
            title="Export Products",
            defaultextension=default_ext,
            filetypes=filetypes
        )
        if not filepath:
            return

        if fmt == "csv":
            success, msg = export_model.export_products_csv(filepath)
        else:
            success, msg = export_model.export_products_xlsx(filepath)

        if success:
            show_success(root, "Export Complete", msg)
        else:
            show_error(root, "Export Error", msg)

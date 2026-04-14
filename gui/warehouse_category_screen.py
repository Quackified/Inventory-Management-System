"""
warehouse_category_screen.py — Warehouse & Category management UI.
Two-panel layout: Warehouses (top) + Categories (bottom).
Admin + Manager access only.
"""

import tkinter as tk
from tkinter import ttk
from config import BG, CARD_BG, BTN_SUCCESS, BTN_WARNING, BTN_DANGER, FONT_FAMILY
from gui.popover import Popover


class WarehouseCategoryScreen(tk.Frame):
    """Two-panel screen for managing warehouses and categories."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self.handler = None

        # ── Header ───────────────────────────────────────────
        tk.Label(self, text="Warehouses & Categories",
                 font=(FONT_FAMILY, 18, "bold"),
                 bg=BG, fg="#2c3e50").pack(anchor="w", padx=24, pady=(20, 10))

        # ── Warehouses Panel ─────────────────────────────────
        self._build_warehouse_panel()

        # ── Categories Panel ─────────────────────────────────
        self._build_category_panel()

    # ── Warehouse panel ──────────────────────────────────────
    def _build_warehouse_panel(self):
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=24, pady=(4, 2))

        tk.Label(header, text="Warehouses / Stores",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=BG, fg="#34495e").pack(side="left")

        btn_style = dict(font=(FONT_FAMILY, 9, "bold"), fg="white",
                         relief="flat", cursor="hand2", bd=0, padx=10)

        tk.Button(header, text="+ Add", bg=BTN_SUCCESS,
                  activebackground="#219a52",
                  command=self._open_add_warehouse, **btn_style
                  ).pack(side="right", ipady=2, padx=(4, 0))

        tk.Button(header, text="Edit", bg=BTN_WARNING,
                  activebackground="#cf6d17",
                  command=self._open_edit_warehouse, **btn_style
                  ).pack(side="right", ipady=2, padx=(4, 0))

        tk.Button(header, text="Delete", bg=BTN_DANGER,
                  activebackground="#c0392b",
                  command=self._delete_warehouse, **btn_style
                  ).pack(side="right", ipady=2, padx=(4, 0))

        tree_frame = tk.Frame(self, bg=BG)
        tree_frame.pack(fill="both", expand=True, padx=24, pady=(2, 6))

        cols = ("ID", "Name", "Location", "Active")
        self.wh_tree = ttk.Treeview(tree_frame, columns=cols,
                                     show="headings", height=6,
                                     selectmode="browse")
        widths = {"ID": 50, "Name": 200, "Location": 300, "Active": 60}
        for c in cols:
            self.wh_tree.heading(c, text=c)
            self.wh_tree.column(c, width=widths.get(c, 100), anchor="center")

        scroll = ttk.Scrollbar(tree_frame, orient="vertical",
                                command=self.wh_tree.yview)
        self.wh_tree.configure(yscrollcommand=scroll.set)
        self.wh_tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    # ── Category panel ───────────────────────────────────────
    def _build_category_panel(self):
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=24, pady=(4, 2))

        tk.Label(header, text="Categories",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=BG, fg="#34495e").pack(side="left")

        btn_style = dict(font=(FONT_FAMILY, 9, "bold"), fg="white",
                         relief="flat", cursor="hand2", bd=0, padx=10)

        tk.Button(header, text="+ Add", bg=BTN_SUCCESS,
                  activebackground="#219a52",
                  command=self._open_add_category, **btn_style
                  ).pack(side="right", ipady=2, padx=(4, 0))

        tk.Button(header, text="Edit", bg=BTN_WARNING,
                  activebackground="#cf6d17",
                  command=self._open_edit_category, **btn_style
                  ).pack(side="right", ipady=2, padx=(4, 0))

        tk.Button(header, text="Delete", bg=BTN_DANGER,
                  activebackground="#c0392b",
                  command=self._delete_category, **btn_style
                  ).pack(side="right", ipady=2, padx=(4, 0))

        tree_frame = tk.Frame(self, bg=BG)
        tree_frame.pack(fill="both", expand=True, padx=24, pady=(2, 20))

        cols = ("ID", "Name", "Description")
        self.cat_tree = ttk.Treeview(tree_frame, columns=cols,
                                      show="headings", height=6,
                                      selectmode="browse")
        widths = {"ID": 50, "Name": 200, "Description": 400}
        for c in cols:
            self.cat_tree.heading(c, text=c)
            self.cat_tree.column(c, width=widths.get(c, 100), anchor="center")

        scroll = ttk.Scrollbar(tree_frame, orient="vertical",
                                command=self.cat_tree.yview)
        self.cat_tree.configure(yscrollcommand=scroll.set)
        self.cat_tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    # ── View interface methods ───────────────────────────────
    def populate_warehouses(self, rows):
        for item in self.wh_tree.get_children():
            self.wh_tree.delete(item)
        for row in rows:
            active_text = "Yes" if row[3] else "No"
            self.wh_tree.insert("", "end", values=(row[0], row[1], row[2] or "", active_text))

    def populate_categories(self, rows):
        for item in self.cat_tree.get_children():
            self.cat_tree.delete(item)
        for row in rows:
            self.cat_tree.insert("", "end", values=row)

    def get_selected_warehouse(self):
        sel = self.wh_tree.selection()
        if not sel:
            return None
        return self.wh_tree.item(sel[0], "values")

    def get_selected_category(self):
        sel = self.cat_tree.selection()
        if not sel:
            return None
        return self.cat_tree.item(sel[0], "values")

    def on_show(self):
        if self.handler:
            self.handler.refresh()

    # ── Popover dialogs ──────────────────────────────────────
    def _open_add_warehouse(self):
        pop = Popover(self.winfo_toplevel(), title="Add Warehouse",
                      width=420, height=220)
        e_name = pop.add_field("Name:")
        e_loc = pop.add_field("Location:")

        def on_save():
            if self.handler:
                self.handler.add_warehouse(
                    e_name.get().strip(), e_loc.get().strip()
                )
            pop.close()

        pop.add_button("Save", command=on_save, style="success")
        pop.add_button("Cancel", command=pop.close, style="secondary")

    def _open_edit_warehouse(self):
        sel = self.get_selected_warehouse()
        if not sel:
            from tkinter import messagebox
            messagebox.showwarning("Selection", "Select a warehouse first.")
            return

        pop = Popover(self.winfo_toplevel(), title="Edit Warehouse",
                      width=420, height=260)
        e_name = pop.add_field("Name:", default=sel[1])
        e_loc = pop.add_field("Location:", default=sel[2])
        e_active = pop.add_dropdown("Active:", values=["Yes", "No"],
                                     default=sel[3])

        def on_save():
            if self.handler:
                self.handler.update_warehouse(
                    sel[0], e_name.get().strip(), e_loc.get().strip(),
                    1 if e_active.get() == "Yes" else 0
                )
            pop.close()

        pop.add_button("Save", command=on_save, style="success")
        pop.add_button("Cancel", command=pop.close, style="secondary")

    def _delete_warehouse(self):
        if self.handler:
            self.handler.delete_warehouse()

    def _open_add_category(self):
        pop = Popover(self.winfo_toplevel(), title="Add Category",
                      width=420, height=220)
        e_name = pop.add_field("Name:")
        e_desc = pop.add_field("Description:")

        def on_save():
            if self.handler:
                self.handler.add_category(
                    e_name.get().strip(), e_desc.get().strip()
                )
            pop.close()

        pop.add_button("Save", command=on_save, style="success")
        pop.add_button("Cancel", command=pop.close, style="secondary")

    def _open_edit_category(self):
        sel = self.get_selected_category()
        if not sel:
            from tkinter import messagebox
            messagebox.showwarning("Selection", "Select a category first.")
            return

        pop = Popover(self.winfo_toplevel(), title="Edit Category",
                      width=420, height=220)
        e_name = pop.add_field("Name:", default=sel[1])
        e_desc = pop.add_field("Description:", default=sel[2])

        def on_save():
            if self.handler:
                self.handler.update_category(
                    sel[0], e_name.get().strip(), e_desc.get().strip()
                )
            pop.close()

        pop.add_button("Save", command=on_save, style="success")
        pop.add_button("Cancel", command=pop.close, style="secondary")

    def _delete_category(self):
        if self.handler:
            self.handler.delete_category()

"""
products_screen.py — Product management screen with popover CRUD and stock-in/out.
"""

import tkinter as tk
from tkinter import ttk
from config import (BG, CARD_BG, BTN_SUCCESS, BTN_WARNING, BTN_DANGER,
                    BTN_PRIMARY, FONT_FAMILY, ROW_LOW_STOCK, ROW_EXPIRED)
from gui.popover import Popover


class ProductsScreen(tk.Frame):
    """Product list with Treeview, popover CRUD, search, and stock-in/out."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self.handler = None

        # ── Header + toolbar ─────────────────────────────────
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=24, pady=(20, 10))

        tk.Label(header, text="Product Management",
                 font=(FONT_FAMILY, 18, "bold"),
                 bg=BG, fg="#2c3e50").pack(side="left")

        # Toolbar buttons (right side)
        toolbar = tk.Frame(header, bg=BG)
        toolbar.pack(side="right")

        btn_style = dict(font=(FONT_FAMILY, 9, "bold"), fg="white",
                         relief="flat", cursor="hand2", bd=0, padx=10)

        tk.Button(toolbar, text="+ Add Product", bg=BTN_SUCCESS,
                  activebackground="#219a52",
                  command=self._open_add, **btn_style
                  ).pack(side="left", ipady=3, padx=2)

        tk.Button(toolbar, text="Edit", bg=BTN_WARNING,
                  activebackground="#cf6d17",
                  command=self._open_edit, **btn_style
                  ).pack(side="left", ipady=3, padx=2)

        tk.Button(toolbar, text="Delete", bg=BTN_DANGER,
                  activebackground="#c0392b",
                  command=self._on_delete, **btn_style
                  ).pack(side="left", ipady=3, padx=2)

        # Spacer
        tk.Frame(toolbar, bg=BG, width=12).pack(side="left")

        tk.Button(toolbar, text="▲ Stock In", bg="#27ae60",
                  activebackground="#219a52",
                  command=lambda: self._open_stock("Stock-In"), **btn_style
                  ).pack(side="left", ipady=3, padx=2)

        tk.Button(toolbar, text="▼ Stock Out", bg="#e74c3c",
                  activebackground="#c0392b",
                  command=lambda: self._open_stock("Stock-Out"), **btn_style
                  ).pack(side="left", ipady=3, padx=2)

        # Spacer
        tk.Frame(toolbar, bg=BG, width=12).pack(side="left")

        tk.Button(toolbar, text="Export CSV", bg="#7f8c8d",
                  activebackground="#6c7a7d",
                  command=lambda: self._on_export("csv"), **btn_style
                  ).pack(side="left", ipady=3, padx=2)

        tk.Button(toolbar, text="Export Excel", bg="#2c3e50",
                  activebackground="#1a252f",
                  command=lambda: self._on_export("xlsx"), **btn_style
                  ).pack(side="left", ipady=3, padx=2)

        # ── Search bar ──────────────────────────────────────
        search_frame = tk.Frame(self, bg=BG)
        search_frame.pack(fill="x", padx=24, pady=(0, 6))

        tk.Label(search_frame, text="Search:",
                 font=(FONT_FAMILY, 10), bg=BG, fg="#555").pack(side="left")
        self.entry_search = tk.Entry(search_frame, font=(FONT_FAMILY, 10),
                                     width=28, relief="solid", bd=1)
        self.entry_search.pack(side="left", padx=(6, 6), ipady=2)
        self.entry_search.bind("<KeyRelease>", lambda e: self._on_search())

        tk.Button(search_frame, text="Clear", font=(FONT_FAMILY, 9),
                  bg="#95a5a6", fg="white", relief="flat", cursor="hand2",
                  command=self._on_clear_search).pack(side="left", ipady=1)

        # ── Treeview ─────────────────────────────────────────
        tree_frame = tk.Frame(self, bg=BG)
        tree_frame.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        cols = ("ID", "Name", "Stock", "Unit", "Warehouse", "Category",
                "Threshold", "Expiry", "Status", "Batch")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                 show="headings", height=16,
                                 selectmode="browse")

        col_widths = {"ID": 40, "Name": 150, "Stock": 55, "Unit": 50,
                      "Warehouse": 110, "Category": 100, "Threshold": 65,
                      "Expiry": 90, "Status": 65, "Batch": 90}
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=col_widths.get(c, 80), anchor="center")

        # Row tags for highlighting
        self.tree.tag_configure("low_stock", background=ROW_LOW_STOCK)
        self.tree.tag_configure("expired", background=ROW_EXPIRED)

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical",
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self._selected_id = None
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    # ── View interface methods ───────────────────────────────
    def get_selected_id(self):
        return self._selected_id

    def get_search_term(self):
        return self.entry_search.get().strip()

    def populate_table(self, rows):
        """
        Clear and repopulate the Treeview.
        rows: list of (id, name, desc, stock, unit, warehouse, category,
                       threshold, expiry_date, expiry_status, mfg_date, batch)
        """
        self._selected_id = None
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in rows:
            # row indices: 0=id, 1=name, 2=desc, 3=stock, 4=unit,
            #   5=warehouse, 6=category, 7=threshold,
            #   8=expiry_date, 9=expiry_status, 10=mfg_date, 11=batch
            display = (
                row[0], row[1], row[3], row[4],     # ID, Name, Stock, Unit
                row[5], row[6],                       # Warehouse, Category
                row[7],                               # Threshold
                row[8] if row[8] else "—",            # Expiry Date
                row[9],                               # Status
                row[11] if row[11] else "—",           # Batch
            )

            tags = ()
            if row[9] == "Expired":
                tags = ("expired",)
            elif row[3] < row[7]:  # stock < threshold
                tags = ("low_stock",)

            self.tree.insert("", "end", values=display, tags=tags)

    def on_show(self):
        if self.handler:
            self.handler.refresh()

    # ── Internal callbacks ───────────────────────────────────
    def _on_tree_select(self, _event):
        sel = self.tree.selection()
        if sel:
            self._selected_id = self.tree.item(sel[0], "values")[0]

    def _on_search(self):
        if self.handler:
            self.handler.search()

    def _on_clear_search(self):
        self.entry_search.delete(0, tk.END)
        if self.handler:
            self.handler.refresh()

    def _on_delete(self):
        if self.handler:
            self.handler.delete()

    # ── Popover: Add / Edit product ──────────────────────────
    def _open_add(self):
        if self.handler:
            self.handler.open_add_popover()

    def _open_edit(self):
        if self.handler:
            self.handler.open_edit_popover()

    # ── Popover: Stock-In / Stock-Out ────────────────────────
    def _open_stock(self, txn_type):
        if not self._selected_id:
            from tkinter import messagebox
            messagebox.showwarning("Selection",
                                   "Select a product from the table first.")
            return

        if self.handler:
            self.handler.open_stock_popover(txn_type)

    # ── Export ───────────────────────────────────────────────
    def _on_export(self, fmt):
        if self.handler:
            self.handler.export(fmt)

"""
transactions_screen.py — Transaction log viewer with filters and date picker.
"""

import tkinter as tk
from tkinter import ttk
from datetime import date, timedelta
from config import BG, CARD_BG, BTN_PRIMARY, FONT_FAMILY


class TransactionsScreen(tk.Frame):
    """Read-only transaction log viewer with date picker, filters, and export."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self.handler = None

        # ── Header ───────────────────────────────────────────
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=24, pady=(20, 10))

        tk.Label(header, text="Transaction Logs",
                 font=(FONT_FAMILY, 18, "bold"),
                 bg=BG, fg="#2c3e50").pack(side="left")

        # ── Filter toolbar ───────────────────────────────────
        filters = tk.Frame(self, bg=CARD_BG, bd=0,
                           highlightbackground="#ddd", highlightthickness=1)
        filters.pack(fill="x", padx=24, pady=(0, 8))

        # Row 1 — Date range + quick picks
        r1 = tk.Frame(filters, bg=CARD_BG)
        r1.pack(fill="x", padx=12, pady=(10, 4))

        tk.Label(r1, text="From:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.entry_date_from = tk.Entry(r1, font=(FONT_FAMILY, 10),
                                         width=12, relief="solid", bd=1)
        self.entry_date_from.pack(side="left", padx=(4, 10))

        tk.Label(r1, text="To:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.entry_date_to = tk.Entry(r1, font=(FONT_FAMILY, 10),
                                       width=12, relief="solid", bd=1)
        self.entry_date_to.pack(side="left", padx=(4, 14))

        # Quick date buttons
        quick_style = dict(font=(FONT_FAMILY, 8), bg="#ecf0f1", fg="#2c3e50",
                           relief="flat", cursor="hand2", bd=0, padx=6)

        tk.Button(r1, text="Today",
                  command=self._set_today, **quick_style
                  ).pack(side="left", ipady=2, padx=2)
        tk.Button(r1, text="Yesterday",
                  command=self._set_yesterday, **quick_style
                  ).pack(side="left", ipady=2, padx=2)
        tk.Button(r1, text="This Week",
                  command=self._set_this_week, **quick_style
                  ).pack(side="left", ipady=2, padx=2)
        tk.Button(r1, text="This Month",
                  command=self._set_this_month, **quick_style
                  ).pack(side="left", ipady=2, padx=2)
        tk.Button(r1, text="All Time",
                  command=self._set_all_time, **quick_style
                  ).pack(side="left", ipady=2, padx=2)

        # Row 2 — Warehouse + Type + Search + Apply
        r2 = tk.Frame(filters, bg=CARD_BG)
        r2.pack(fill="x", padx=12, pady=(4, 10))

        tk.Label(r2, text="Warehouse:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.cmb_warehouse = ttk.Combobox(r2, font=(FONT_FAMILY, 10),
                                           width=16, state="readonly")
        self.cmb_warehouse.pack(side="left", padx=(4, 10))

        tk.Label(r2, text="Type:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.cmb_type = ttk.Combobox(r2, font=(FONT_FAMILY, 10),
                                      width=10, state="readonly",
                                      values=["All", "Stock-In", "Stock-Out"])
        self.cmb_type.set("All")
        self.cmb_type.pack(side="left", padx=(4, 10))

        tk.Label(r2, text="Search:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.entry_search = tk.Entry(r2, font=(FONT_FAMILY, 10),
                                      width=18, relief="solid", bd=1)
        self.entry_search.pack(side="left", padx=(4, 10))

        tk.Button(r2, text="Apply Filters",
                  font=(FONT_FAMILY, 9, "bold"),
                  bg=BTN_PRIMARY, fg="white",
                  activebackground="#3b6baa",
                  relief="flat", cursor="hand2",
                  command=self._on_apply_filters
                  ).pack(side="left", ipady=3, padx=(4, 4))

        tk.Button(r2, text="Clear",
                  font=(FONT_FAMILY, 9),
                  bg="#95a5a6", fg="white",
                  relief="flat", cursor="hand2",
                  command=self._on_clear_filters
                  ).pack(side="left", ipady=3)

        # Export buttons
        tk.Frame(r2, bg=CARD_BG, width=10).pack(side="left")

        tk.Button(r2, text="Export CSV",
                  font=(FONT_FAMILY, 8, "bold"),
                  bg="#7f8c8d", fg="white",
                  relief="flat", cursor="hand2",
                  command=lambda: self._on_export("csv")
                  ).pack(side="left", ipady=2, padx=2)

        tk.Button(r2, text="Export Excel",
                  font=(FONT_FAMILY, 8, "bold"),
                  bg="#2c3e50", fg="white",
                  relief="flat", cursor="hand2",
                  command=lambda: self._on_export("xlsx")
                  ).pack(side="left", ipady=2, padx=2)

        # ── Treeview ─────────────────────────────────────────
        tree_frame = tk.Frame(self, bg=BG)
        tree_frame.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        cols = ("ID", "Product", "Type", "Qty", "Date",
                "Warehouse", "Category", "Batch", "Remarks", "User")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                 show="headings", height=14,
                                 selectmode="browse")

        col_widths = {"ID": 40, "Product": 130, "Type": 75, "Qty": 45,
                      "Date": 115, "Warehouse": 100, "Category": 90,
                      "Batch": 80, "Remarks": 130, "User": 70}
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=col_widths.get(c, 80), anchor="center")

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical",
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # Warehouse map for filter dropdown
        self._warehouse_map = {}

    # ── View interface methods ───────────────────────────────
    def populate_warehouses(self, wh_rows):
        """Fill warehouse filter dropdown. wh_rows: list of (id, name)."""
        self._warehouse_map.clear()
        display = ["All Warehouses"]
        for wid, name in wh_rows:
            display.append(name)
            self._warehouse_map[name] = wid
        self.cmb_warehouse["values"] = display
        self.cmb_warehouse.set("All Warehouses")

    def populate_table(self, rows):
        """Clear and repopulate the log table."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", "end", values=row)

    def get_filters(self):
        """Return current filter values as a dict."""
        wh_name = self.cmb_warehouse.get()
        wh_id = self._warehouse_map.get(wh_name)  # None for "All Warehouses"

        return {
            "warehouse_id": wh_id,
            "search_term": self.entry_search.get().strip() or None,
            "txn_type": self.cmb_type.get(),
            "date_from": self.entry_date_from.get().strip() or None,
            "date_to": self.entry_date_to.get().strip() or None,
        }

    def on_show(self):
        if self.handler:
            self.handler.refresh()

    # ── Quick date setters ───────────────────────────────────
    def _set_date_range(self, d_from, d_to):
        self.entry_date_from.delete(0, tk.END)
        self.entry_date_from.insert(0, d_from)
        self.entry_date_to.delete(0, tk.END)
        self.entry_date_to.insert(0, d_to)
        self._on_apply_filters()

    def _set_today(self):
        today = date.today().isoformat()
        self._set_date_range(today, today)

    def _set_yesterday(self):
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        self._set_date_range(yesterday, yesterday)

    def _set_this_week(self):
        today = date.today()
        start = (today - timedelta(days=today.weekday())).isoformat()
        self._set_date_range(start, today.isoformat())

    def _set_this_month(self):
        today = date.today()
        start = today.replace(day=1).isoformat()
        self._set_date_range(start, today.isoformat())

    def _set_all_time(self):
        self.entry_date_from.delete(0, tk.END)
        self.entry_date_to.delete(0, tk.END)
        self._on_apply_filters()

    # ── Internal callbacks ───────────────────────────────────
    def _on_apply_filters(self):
        if self.handler:
            self.handler.apply_filters()

    def _on_clear_filters(self):
        self.entry_date_from.delete(0, tk.END)
        self.entry_date_to.delete(0, tk.END)
        self.entry_search.delete(0, tk.END)
        self.cmb_type.set("All")
        self.cmb_warehouse.set("All Warehouses")
        if self.handler:
            self.handler.refresh()

    def _on_export(self, fmt):
        if self.handler:
            self.handler.export(fmt)

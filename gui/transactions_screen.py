"""
transactions_screen.py — Transaction log viewer using ttkbootstrap.
Date range: single ttkbootstrap DateEntry widget (inline calendar icon, like the reference).
Same Products-style: toolbar card + table + pagination.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import date, timedelta
from config import (BG, BEIGE, WHITE, DARK_BROWN, OLIVE, GOLD, AMBER,
                    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
                    BORDER_LIGHT, INPUT_BORDER,
                    ROW_EVEN, ROW_ODD, STATUS_ACTIVE, STATUS_EXPIRED,
                    FONT_FAMILY, ICON_FONT, PAD_SM, PAD_MD, PAD_LG, PAD_XL)
from gui.icons import get_icon
from gui.pagination import PaginationBar


class TransactionsScreen(tk.Frame):
    """Transaction log — Products-style with inline DateEntry widgets."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self.handler = None

        # ── Header ───────────────────────────────────────────
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=PAD_XL, pady=(PAD_LG, PAD_SM))

        tk.Label(header, text="Transaction Logs",
                 font=(FONT_FAMILY, 20, "bold"),
                 bg=BG, fg=DARK_BROWN).pack(side="left")

        # ── Toolbar card ─────────────────────────────────────
        filter_card = tk.Frame(self, bg=WHITE, bd=0,
                               highlightbackground=BORDER_LIGHT,
                               highlightthickness=1)
        filter_card.pack(fill="x", padx=PAD_XL, pady=(0, PAD_SM))

        toolbar = tk.Frame(filter_card, bg=WHITE, padx=16, pady=10)
        toolbar.pack(fill="x")

        # Left side: Date entries (inline with calendar icon) + dropdowns
        left = tk.Frame(toolbar, bg=WHITE)
        left.pack(side="left")

        # From DateEntry (ttkbootstrap DateEntry — inline calendar selector)
        tk.Label(left, text="From:", font=(FONT_FAMILY, 10),
                 bg=WHITE, fg=TEXT_SECONDARY).pack(side="left")
        self.date_from = ttk.DateEntry(left, dateformat="%Y-%m-%d",
                                       width=12)
        self.date_from.pack(side="left", padx=(4, 12))

        # To DateEntry
        tk.Label(left, text="To:", font=(FONT_FAMILY, 10),
                 bg=WHITE, fg=TEXT_SECONDARY).pack(side="left")
        self.date_to = ttk.DateEntry(left, dateformat="%Y-%m-%d",
                                     width=12)
        self.date_to.pack(side="left", padx=(4, 12))

        # Warehouse dropdown
        tk.Label(left, text="Warehouse:", font=(FONT_FAMILY, 10),
                 bg=WHITE, fg=TEXT_SECONDARY).pack(side="left", padx=(4, 0))
        self.cmb_warehouse = ttk.Combobox(left, font=(FONT_FAMILY, 10),
                                          width=14, state="readonly")
        self.cmb_warehouse.pack(side="left", padx=(4, 12))

        # Type dropdown
        tk.Label(left, text="Type:", font=(FONT_FAMILY, 10),
                 bg=WHITE, fg=TEXT_SECONDARY).pack(side="left")
        self.cmb_type = ttk.Combobox(left, font=(FONT_FAMILY, 10),
                                     width=10, state="readonly",
                                     values=["All", "Stock-In", "Stock-Out"])
        self.cmb_type.set("All")
        self.cmb_type.pack(side="left", padx=(4, 0))

        # Clear button sits next to the Type dropdown.
        ttk.Button(left, text="Clear", bootstyle="secondary-outline",
               command=self._on_clear_filters
               ).pack(side="left", padx=(6, 12))

        # Right side: buttons
        right = tk.Frame(toolbar, bg=WHITE)
        right.pack(side="right")

        # Export (plain dropdown — tight labels)
        export_mb = ttk.Menubutton(right, text="Export",
                                   bootstyle="secondary-outline")
        export_menu = tk.Menu(export_mb, tearoff=0,
                              font=(FONT_FAMILY, 10), bg=WHITE,
                              fg=DARK_BROWN, activebackground=BEIGE,
                              borderwidth=1, relief="solid")
        export_menu.add_command(label="CSV", command=lambda: self._on_export("csv"))
        export_menu.add_command(label="Excel", command=lambda: self._on_export("xlsx"))
        export_mb["menu"] = export_menu
        export_mb.pack(side="right", padx=(6, 0))

        # ── Date preset row ──────────────────────────────────
        preset_row = tk.Frame(filter_card, bg=WHITE, padx=16)
        preset_row.pack(fill="x", pady=(0, 8))

        tk.Label(preset_row, text="Quick:", font=(FONT_FAMILY, 9),
                 bg=WHITE, fg=TEXT_MUTED).pack(side="left", padx=(0, 6))

        for label, cmd in [
            ("Today",      self._preset_today),
            ("This Week",  self._preset_week),
            ("This Month", self._preset_month),
            ("All Time",   self._preset_all_time),
        ]:
            ttk.Button(preset_row, text=label, bootstyle="secondary-outline",
                       command=cmd
                       ).pack(side="left", padx=(0, 4))

        self.cmb_warehouse.bind("<<ComboboxSelected>>", self._on_filter_change)
        self.cmb_type.bind("<<ComboboxSelected>>", self._on_filter_change)

        # ── Treeview ─────────────────────────────────────────
        tree_frame = tk.Frame(self, bg=WHITE, bd=0, highlightbackground=BORDER_LIGHT, highlightthickness=1)
        tree_frame.pack(fill="both", expand=True, padx=PAD_XL, pady=(0, PAD_SM))

        cols = ("ID", "Product", "Type", "Qty", "Date",
                "Warehouse", "Category", "Batch", "Remarks", "User")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                 show="headings", height=14,
                                 selectmode="browse")

        col_widths = {"ID": 44, "Product": 140, "Type": 80, "Qty": 50,
                      "Date": 120, "Warehouse": 100, "Category": 90,
                      "Batch": 80, "Remarks": 130, "User": 70}
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=col_widths.get(c, 80),
                             anchor="center", stretch=True)

        self.tree.tag_configure("stock_in",  foreground=STATUS_ACTIVE)
        self.tree.tag_configure("stock_out", foreground=STATUS_EXPIRED)
        self.tree.tag_configure("evenrow",   background=ROW_EVEN)
        self.tree.tag_configure("oddrow",    background=ROW_ODD)

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical",
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self._warehouse_map = {}

        # ── Pagination (bottom) ──────────────────────────────
        pager_frame = tk.Frame(self, bg=WHITE, bd=0,
                               highlightbackground=BORDER_LIGHT,
                               highlightthickness=1)
        pager_frame.pack(fill="x", padx=PAD_XL, pady=(0, PAD_LG))

        self.pager = PaginationBar(pager_frame,
                                   on_page_change=self._on_page_change,
                                   bg=WHITE)
        self.pager.pack(fill="x", padx=12, pady=6)
        self.pager.cmb_size.set("50")
        self.pager._page_size = 50

    # ── View interface ───────────────────────────────────────
    def populate_warehouses(self, wh_rows):
        self._warehouse_map.clear()
        display = ["All Warehouses"]
        for wid, name in wh_rows:
            display.append(name)
            self._warehouse_map[name] = wid
        self.cmb_warehouse["values"] = display
        self.cmb_warehouse.set("All Warehouses")

    def populate_table(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, row in enumerate(rows):
            txn_type = row[2]
            base_tag = "stock_in" if txn_type == "Stock-In" else "stock_out"
            alt_tag  = "evenrow" if i % 2 == 0 else "oddrow"

            display = (
                row[0], row[1], row[2], row[3], row[4],
                row[7], row[8], row[9], row[5], row[6],
            )
            self.tree.insert("", "end", values=display,
                             tags=(base_tag, alt_tag))

    def get_filters(self):
        wh_name = self.cmb_warehouse.get()
        wh_id = self._warehouse_map.get(wh_name)

        date_from_val = self.date_from.entry.get().strip()
        date_to_val = self.date_to.entry.get().strip()

        return {
            "warehouse_id": wh_id,
            "search_term":  None,
            "txn_type":     self.cmb_type.get(),
            "date_from":    date_from_val if date_from_val else None,
            "date_to":      date_to_val if date_to_val else None,
        }

    def on_show(self):
        if self.handler:
            self.handler.refresh()

    # ── Date presets ─────────────────────────────────────────
    def _set_date_range(self, from_date, to_date):
        """Helper: set both DateEntry widgets to specific dates."""
        self.pager.reset()
        self.date_from.entry.delete(0, tk.END)
        self.date_from.entry.insert(0, from_date.strftime("%Y-%m-%d"))
        self.date_to.entry.delete(0, tk.END)
        self.date_to.entry.insert(0, to_date.strftime("%Y-%m-%d"))
        self._on_apply_filters()

    def _preset_today(self):
        today = date.today()
        self._set_date_range(today, today)

    def _preset_week(self):
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)
        self._set_date_range(monday, sunday)

    def _preset_month(self):
        today = date.today()
        first_of_month = today.replace(day=1)
        self._set_date_range(first_of_month, today)

    def _preset_all_time(self):
        self.pager.reset()
        self.date_from.entry.delete(0, tk.END)
        self.date_to.entry.delete(0, tk.END)
        self._on_apply_filters()

    def _on_filter_change(self, _event=None):
        self.pager.reset()
        self._on_apply_filters()

    # ── Internal callbacks ───────────────────────────────────
    def _on_apply_filters(self):
        if self.handler:
            self.handler.apply_filters()

    def _on_clear_filters(self):
        self.pager.reset()
        self.cmb_type.set("All")
        self.cmb_warehouse.set("All Warehouses")
        # Clear date pickers
        self.date_from.entry.delete(0, tk.END)
        self.date_to.entry.delete(0, tk.END)
        self._on_apply_filters()

    def _on_export(self, fmt):
        if self.handler:
            self.handler.export(fmt)

    def _on_page_change(self, page, page_size):
        if self.handler:
            self.handler.apply_filters(page=page, page_size=page_size)

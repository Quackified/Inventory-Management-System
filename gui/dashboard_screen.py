"""
dashboard_screen.py — Dashboard with summary cards, date header,
                      recent transactions (View All >), warehouse summary, chart.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
from config import (BG, BEIGE, WHITE, DARK_BROWN, OLIVE, GOLD, AMBER,
                    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
                    BORDER_LIGHT, FONT_FAMILY, ICON_FONT,
                    STATUS_ACTIVE, STATUS_LOW_STOCK, STATUS_EXPIRED,
                    PAD_SM, PAD_MD, PAD_LG, PAD_XL)
from gui.icons import get_icon
from gui.chart_widget import BarChart


class DashboardScreen(tk.Frame):
    """Dashboard screen with cards, transactions, warehouse overview, chart."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self.handler = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ── Header row: title (left) + date (right) ─────────
        header = tk.Frame(self, bg=BG)
        header.grid(row=0, column=0, columnspan=2, sticky="ew",
                    padx=PAD_XL, pady=(PAD_LG, PAD_SM))

        tk.Label(header, text="Dashboard",
                 font=(FONT_FAMILY, 20, "bold"),
                 bg=BG, fg=DARK_BROWN).pack(side="left")

        now = datetime.now()
        date_str = now.strftime("%A, %B %d")
        self.lbl_date = tk.Label(
            header, text=date_str,
            font=(FONT_FAMILY, 11), bg=BG, fg=TEXT_SECONDARY,
        )
        self.lbl_date.pack(side="right")

        # ── Summary cards ────────────────────────────────────
        cards_frame = tk.Frame(self, bg=BG)
        cards_frame.grid(row=1, column=0, columnspan=2, sticky="ew",
                         padx=PAD_XL, pady=(0, PAD_MD))
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="card")

        self.cards = {}
        card_defs = [
            ("total_products",  "Total Products",  OLIVE,           "\uE719"),
            ("total_stock",     "Total Stock",      "#4A6FA5",       "\uE74A"),
            ("low_stock_count", "Low Stock Items",  STATUS_LOW_STOCK, "\uE7BA"),
            ("expired_count",   "Expired Items",    STATUS_EXPIRED,  "\uE783"),
        ]

        for idx, (key, label, color, icon_char) in enumerate(card_defs):
            px_l = 0 if idx == 0 else 6
            px_r = 0 if idx == 3 else 6

            card = tk.Frame(cards_frame, bg=WHITE, bd=0,
                            highlightbackground=BORDER_LIGHT,
                            highlightthickness=1)
            card.grid(row=0, column=idx, sticky="nsew",
                      padx=(px_l, px_r), ipady=4)

            tk.Frame(card, bg=color, height=3).pack(fill="x")

            inner = tk.Frame(card, bg=WHITE, padx=16, pady=12)
            inner.pack(fill="both", expand=True)

            tk.Label(inner, text=icon_char,
                     font=(ICON_FONT, 18), fg=color,
                     bg=WHITE).pack(anchor="e")

            lbl_val = tk.Label(inner, text="0",
                               font=(FONT_FAMILY, 28, "bold"),
                               bg=WHITE, fg=DARK_BROWN)
            lbl_val.pack(anchor="w")

            tk.Label(inner, text=label,
                     font=(FONT_FAMILY, 10),
                     bg=WHITE, fg=TEXT_MUTED).pack(anchor="w", pady=(2, 0))

            self.cards[key] = lbl_val

        # ── Middle row: Transactions (left) + Warehouse (right) ──
        # Recent Transactions panel
        txn_panel = tk.Frame(self, bg=WHITE, bd=0,
                             highlightbackground=BORDER_LIGHT,
                             highlightthickness=1)
        txn_panel.grid(row=2, column=0, sticky="nsew",
                       padx=(PAD_XL, 6), pady=(0, PAD_MD))

        txn_header = tk.Frame(txn_panel, bg=WHITE, padx=16, pady=6)
        txn_header.pack(fill="x")
        tk.Label(txn_header, text="Recent Transactions",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=WHITE, fg=DARK_BROWN).pack(side="left")

        # "View All >" button (replaces scrollbar)
        view_all_txn = tk.Label(txn_header, text="View All  ›",
                                font=(FONT_FAMILY, 10), fg=OLIVE,
                                bg=WHITE, cursor="hand2")
        view_all_txn.pack(side="right")
        view_all_txn.bind("<Button-1>",
                          lambda e: self.controller.show_frame("TransactionsScreen"))
        view_all_txn.bind("<Enter>", lambda e: view_all_txn.config(fg=DARK_BROWN))
        view_all_txn.bind("<Leave>", lambda e: view_all_txn.config(fg=OLIVE))

        tk.Frame(txn_panel, bg=BORDER_LIGHT, height=1).pack(fill="x")

        # Transaction list (NO scroll, just show top items)
        self.txn_inner = tk.Frame(txn_panel, bg=WHITE)
        self.txn_inner.pack(fill="both", expand=True)

        # Warehouse panel (right)
        wh_panel = tk.Frame(self, bg=WHITE, bd=0,
                            highlightbackground=BORDER_LIGHT,
                            highlightthickness=1)
        wh_panel.grid(row=2, column=1, sticky="nsew",
                      padx=(6, PAD_XL), pady=(0, PAD_MD))

        wh_header = tk.Frame(wh_panel, bg=WHITE, padx=16, pady=12)
        wh_header.pack(fill="x")
        tk.Label(wh_header, text="Warehouse Overview",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=WHITE, fg=DARK_BROWN).pack(side="left")

        view_all_wh = tk.Label(wh_header, text="View All  ›",
                               font=(FONT_FAMILY, 10), fg=OLIVE,
                               bg=WHITE, cursor="hand2")
        view_all_wh.pack(side="right")
        view_all_wh.bind("<Button-1>",
                         lambda e: self.controller.show_frame("WarehouseCategoryScreen"))
        view_all_wh.bind("<Enter>", lambda e: view_all_wh.config(fg=DARK_BROWN))
        view_all_wh.bind("<Leave>", lambda e: view_all_wh.config(fg=OLIVE))

        tk.Frame(wh_panel, bg=BORDER_LIGHT, height=1).pack(fill="x")

        self.wh_container = tk.Frame(wh_panel, bg=WHITE, padx=16, pady=8)
        self.wh_container.pack(fill="both", expand=True)

        # ── Bottom: Analytics chart ──────────────────────────
        chart_panel = tk.Frame(self, bg=WHITE, bd=0,
                               highlightbackground=BORDER_LIGHT,
                               highlightthickness=1)
        chart_panel.grid(row=3, column=0, columnspan=2, sticky="ew",
                         padx=PAD_XL, pady=(0, PAD_LG))

        chart_header = tk.Frame(chart_panel, bg=WHITE, padx=16, pady=10)
        chart_header.pack(fill="x")

        tk.Label(chart_header, text="Transaction Analytics",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=WHITE, fg=DARK_BROWN).pack(side="left")

        toggle = tk.Frame(chart_header, bg=WHITE)
        toggle.pack(side="right")

        self._chart_period = "weekly"

        self.btn_weekly = ttk.Button(
            toggle, text="Weekly", bootstyle="success",
            command=lambda: self._set_chart_period("weekly"),
        )
        self.btn_weekly.pack(side="left", padx=(0, 4))

        self.btn_monthly = ttk.Button(
            toggle, text="Monthly", bootstyle="secondary-outline",
            command=lambda: self._set_chart_period("monthly"),
        )
        self.btn_monthly.pack(side="left")

        tk.Frame(chart_panel, bg=BORDER_LIGHT, height=1).pack(fill="x")

        self.chart = BarChart(chart_panel, bg=WHITE)
        self.chart.pack(fill="x", padx=16, pady=(8, 12))

    # ── View interface ───────────────────────────────────────
    def update_cards(self, stats):
        for key, lbl in self.cards.items():
            val = stats.get(key, 0)
            lbl.config(text=f"{val:,}" if isinstance(val, int) else str(val))

    def populate_recent(self, rows):
        for w in self.txn_inner.winfo_children():
            w.destroy()

        if not rows:
            tk.Label(self.txn_inner, text="No recent transactions",
                     font=(FONT_FAMILY, 10), fg=TEXT_MUTED,
                     bg=WHITE, pady=20).pack(fill="x")
            return

        # Show max 8 items (no scroll)
        for i, row in enumerate(rows[:8]):
            bg = WHITE if i % 2 == 0 else "#F8F5F0"
            item = tk.Frame(self.txn_inner, bg=bg, padx=16, pady=8)
            item.pack(fill="x")

            type_color = STATUS_ACTIVE if row[2] == "Stock-In" else STATUS_EXPIRED
            tk.Label(item, text="●", font=(FONT_FAMILY, 8),
                     fg=type_color, bg=bg).pack(side="left", padx=(0, 8))

            tk.Label(item, text=row[1],
                     font=(FONT_FAMILY, 10, "bold"),
                     fg=DARK_BROWN, bg=bg, anchor="w").pack(side="left")

            tk.Label(item, text=row[4],
                     font=(FONT_FAMILY, 9), fg=TEXT_MUTED,
                     bg=bg).pack(side="right")

            type_text = f"{row[2]}  ×{row[3]}"
            tk.Label(item, text=type_text,
                     font=(FONT_FAMILY, 9), fg=TEXT_SECONDARY,
                     bg=bg).pack(side="right", padx=(0, 16))

            if i < len(rows[:8]) - 1:
                tk.Frame(self.txn_inner, bg=BORDER_LIGHT, height=1).pack(fill="x")

    def populate_warehouse_summary(self, data):
        for w in self.wh_container.winfo_children():
            w.destroy()

        if not data:
            tk.Label(self.wh_container, text="No warehouses found",
                     font=(FONT_FAMILY, 10), fg=TEXT_MUTED,
                     bg=WHITE, pady=20).pack(fill="x")
            return

        for i, wh in enumerate(data):
            bg = WHITE if i % 2 == 0 else "#F8F5F0"
            row = tk.Frame(self.wh_container, bg=bg, padx=8, pady=8)
            row.pack(fill="x", pady=(0, 2))

            tk.Label(row, text=wh["name"],
                     font=(FONT_FAMILY, 10, "bold"),
                     fg=DARK_BROWN, bg=bg, anchor="w").pack(anchor="w")

            stats_frame = tk.Frame(row, bg=bg)
            stats_frame.pack(fill="x", pady=(4, 0))

            stat_items = [
                (f"{wh['product_count']} products", TEXT_SECONDARY),
                (f"{wh['total_stock']} stock", OLIVE),
            ]
            if wh.get("low_stock_count", 0) > 0:
                stat_items.append(
                    (f"{wh['low_stock_count']} low", STATUS_LOW_STOCK))
            if wh.get("expired_count", 0) > 0:
                stat_items.append(
                    (f"{wh['expired_count']} expired", STATUS_EXPIRED))

            for text, color in stat_items:
                tk.Label(stats_frame, text=text,
                         font=(FONT_FAMILY, 9), fg=color,
                         bg=bg).pack(side="left", padx=(0, 12))

    def update_chart(self, data):
        self.chart.set_data(data)

    def _set_chart_period(self, period):
        self._chart_period = period
        if period == "weekly":
            self.btn_weekly.config(bootstyle="success")
            self.btn_monthly.config(bootstyle="secondary-outline")
        else:
            self.btn_weekly.config(bootstyle="secondary-outline")
            self.btn_monthly.config(bootstyle="success")

        if self.handler:
            self.handler.refresh_chart(period)

    def on_show(self):
        now = datetime.now()
        self.lbl_date.config(text=now.strftime("%A, %B %d"))
        if self.handler:
            self.handler.refresh()

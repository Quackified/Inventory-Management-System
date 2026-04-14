"""
dashboard_screen.py — Dashboard overview with summary cards and recent transactions.
"""

import tkinter as tk
from tkinter import ttk
from config import BG, CARD_BG, FONT_FAMILY


class DashboardScreen(tk.Frame):
    """Dashboard with summary stat cards and recent transaction list."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self.handler = None

        # ── Header ───────────────────────────────────────────
        tk.Label(self, text="Dashboard",
                 font=(FONT_FAMILY, 18, "bold"),
                 bg=BG, fg="#2c3e50").pack(anchor="w", padx=24, pady=(20, 10))

        # ── Summary cards ────────────────────────────────────
        cards_frame = tk.Frame(self, bg=BG)
        cards_frame.pack(fill="x", padx=24, pady=(0, 10))

        self.cards = {}
        card_defs = [
            ("total_products", "Total Products",  "#3498db"),
            ("total_stock",    "Total Stock",      "#2ecc71"),
            ("low_stock_count","Low Stock Items",   "#e67e22"),
            ("expired_count",  "Expired Items",     "#e74c3c"),
        ]

        for key, label, color in card_defs:
            card = tk.Frame(cards_frame, bg=CARD_BG, bd=0,
                            highlightbackground="#ddd", highlightthickness=1)
            card.pack(side="left", fill="both", expand=True, padx=(0, 10))

            # Color bar at top
            tk.Frame(card, bg=color, height=4).pack(fill="x")

            lbl_val = tk.Label(card, text="0",
                               font=(FONT_FAMILY, 26, "bold"),
                               bg=CARD_BG, fg=color)
            lbl_val.pack(pady=(12, 2))

            tk.Label(card, text=label,
                     font=(FONT_FAMILY, 10),
                     bg=CARD_BG, fg="#7f8c8d").pack(pady=(0, 12))

            self.cards[key] = lbl_val

        # ── Recent transactions ──────────────────────────────
        tk.Label(self, text="Recent Transactions",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=BG, fg="#2c3e50").pack(anchor="w", padx=24, pady=(6, 4))

        tree_frame = tk.Frame(self, bg=BG)
        tree_frame.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        cols = ("ID", "Product", "Type", "Qty", "Date")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                 show="headings", height=8,
                                 selectmode="browse")
        col_widths = {"ID": 50, "Product": 200, "Type": 90,
                      "Qty": 60, "Date": 140}
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=col_widths.get(c, 100), anchor="center")

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical",
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

    # ── View interface methods ───────────────────────────────
    def update_cards(self, stats):
        """Update card values from stats dict."""
        for key, lbl in self.cards.items():
            lbl.config(text=str(stats.get(key, 0)))

    def populate_recent(self, rows):
        """Clear and repopulate the recent transactions table."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", "end", values=row)

    def on_show(self):
        if self.handler:
            self.handler.refresh()

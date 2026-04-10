"""
dashboard_screen.py — Dashboard screen UI (no business logic).
"""

import tkinter as tk
from tkinter import ttk
from config import BG, CARD_BG, BTN_SUCCESS, BTN_WARNING, FONT_FAMILY


class DashboardScreen(tk.Frame):
    """Dashboard with summary cards and recent transactions table."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller

        # ── Dashboard handler reference (set by App) ─────────
        self.handler = None

        # ── Header ───────────────────────────────────────────
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=24, pady=(20, 0))

        tk.Label(header, text="Dashboard",
                 font=(FONT_FAMILY, 18, "bold"),
                 bg=BG, fg="#2c3e50").pack(side="left")

        # ── Summary cards ────────────────────────────────────
        cards_frame = tk.Frame(self, bg=BG)
        cards_frame.pack(fill="x", padx=24, pady=20)

        self.card_labels = {}
        card_defs = [
            ("total_products", "Total Products",    "0", BTN_SUCCESS),
            ("low_stock",      "Low Stock (< 10)",  "0", BTN_WARNING),
            ("txn_today",      "Transactions Today", "0", "#2980b9"),
        ]

        for key, title, val, color in card_defs:
            card = tk.Frame(cards_frame, bg=CARD_BG, bd=0,
                            highlightbackground="#ddd", highlightthickness=1)
            card.pack(side="left", padx=10, ipadx=28, ipady=14)

            tk.Label(card, text=title, font=(FONT_FAMILY, 10),
                     bg=CARD_BG, fg="#888").pack()
            lbl = tk.Label(card, text=val, font=(FONT_FAMILY, 28, "bold"),
                           bg=CARD_BG, fg=color)
            lbl.pack()
            self.card_labels[key] = lbl

        # ── Recent transactions table ────────────────────────
        tk.Label(self, text="Recent Transactions",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=BG, fg="#2c3e50").pack(anchor="w", padx=24, pady=(10, 6))

        cols = ("ID", "Product", "Type", "Qty", "Date", "User")
        self.tree_recent = ttk.Treeview(self, columns=cols,
                                        show="headings", height=8)
        for c in cols:
            self.tree_recent.heading(c, text=c)
            self.tree_recent.column(c, width=110, anchor="center")
        self.tree_recent.pack(fill="x", padx=24)

    # ── View interface methods ───────────────────────────────
    def update_cards(self, stats):
        """Update summary card labels from a stats dict."""
        for key, lbl in self.card_labels.items():
            lbl.config(text=str(stats.get(key, 0)))

    def populate_recent(self, rows):
        """Clear and repopulate the recent transactions table."""
        for item in self.tree_recent.get_children():
            self.tree_recent.delete(item)
        for row in rows:
            self.tree_recent.insert("", "end", values=row)

    def on_show(self):
        """Called when this screen becomes visible."""
        if self.handler:
            self.handler.refresh()

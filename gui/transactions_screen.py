"""
transactions_screen.py — Transaction recording screen UI (no business logic).
"""

import tkinter as tk
from tkinter import ttk
from config import BG, CARD_BG, BTN_PRIMARY, FONT_FAMILY


class TransactionsScreen(tk.Frame):
    """Transaction form with product dropdown, type selector, and history table."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller

        # ── Transactions handler reference (set by App) ──────
        self.handler = None

        # ── Header ───────────────────────────────────────────
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=24, pady=(20, 10))

        tk.Label(header, text="Inventory Transactions",
                 font=(FONT_FAMILY, 18, "bold"),
                 bg=BG, fg="#2c3e50").pack(side="left")

        # ── Input form card ──────────────────────────────────
        form = tk.Frame(self, bg=CARD_BG, bd=0,
                        highlightbackground="#ddd", highlightthickness=1)
        form.pack(fill="x", padx=24, pady=(0, 10))

        # Row 1 — Product selector + Type
        r1 = tk.Frame(form, bg=CARD_BG)
        r1.pack(fill="x", padx=16, pady=(12, 4))

        tk.Label(r1, text="Product:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.cmb_product = ttk.Combobox(r1, font=(FONT_FAMILY, 10),
                                         width=30, state="readonly")
        self.cmb_product.pack(side="left", padx=(6, 20))

        tk.Label(r1, text="Type:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.txn_type = tk.StringVar(value="Stock-In")
        tk.Radiobutton(r1, text="Stock-In", variable=self.txn_type,
                       value="Stock-In", font=(FONT_FAMILY, 10),
                       bg=CARD_BG, activebackground=CARD_BG,
                       fg="#27ae60", selectcolor=CARD_BG
                       ).pack(side="left", padx=(6, 4))
        tk.Radiobutton(r1, text="Stock-Out", variable=self.txn_type,
                       value="Stock-Out", font=(FONT_FAMILY, 10),
                       bg=CARD_BG, activebackground=CARD_BG,
                       fg="#e74c3c", selectcolor=CARD_BG
                       ).pack(side="left")

        # Row 2 — Quantity + Remarks
        r2 = tk.Frame(form, bg=CARD_BG)
        r2.pack(fill="x", padx=16, pady=(4, 8))

        tk.Label(r2, text="Quantity:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.entry_qty = tk.Entry(r2, font=(FONT_FAMILY, 10), width=8,
                                  relief="solid", bd=1)
        self.entry_qty.pack(side="left", padx=(6, 20))

        tk.Label(r2, text="Remarks:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.entry_remarks = tk.Entry(r2, font=(FONT_FAMILY, 10), width=40,
                                      relief="solid", bd=1)
        self.entry_remarks.pack(side="left", padx=(6, 0), fill="x", expand=True)

        # Row 3 — Buttons
        r3 = tk.Frame(form, bg=CARD_BG)
        r3.pack(fill="x", padx=16, pady=(4, 12))

        btn_style = dict(font=(FONT_FAMILY, 10, "bold"), fg="white",
                         relief="flat", cursor="hand2", bd=0, padx=16)

        tk.Button(r3, text="Record Transaction", bg=BTN_PRIMARY,
                  activebackground="#3b6baa",
                  command=self._on_record_click, **btn_style
                  ).pack(side="left", ipady=4, padx=(0, 8))

        tk.Button(r3, text="Clear", bg="#95a5a6",
                  activebackground="#7f8c8d",
                  command=self.clear_form, **btn_style
                  ).pack(side="left", ipady=4)

        # ── Transaction history Treeview ─────────────────────
        tk.Label(self, text="Transaction History",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=BG, fg="#2c3e50").pack(anchor="w", padx=24, pady=(6, 4))

        tree_frame = tk.Frame(self, bg=BG)
        tree_frame.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        cols = ("ID", "Product", "Type", "Qty", "Date", "Remarks", "User")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                 show="headings", height=10,
                                 selectmode="browse")

        col_widths = {"ID": 50, "Product": 160, "Type": 90, "Qty": 60,
                      "Date": 120, "Remarks": 180, "User": 60}
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=col_widths.get(c, 100), anchor="center")

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical",
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # Product map: display_text -> product_id
        self._product_map = {}

    # ── View interface methods ───────────────────────────────
    def get_form_data(self):
        """Return dict with form values and resolved product_id."""
        selected = self.cmb_product.get()
        return {
            "product_label": selected,
            "product_id": self._product_map.get(selected),
            "txn_type": self.txn_type.get(),
            "quantity": self.entry_qty.get().strip(),
            "remarks": self.entry_remarks.get().strip(),
        }

    def populate_products(self, product_rows):
        """
        Fill the product dropdown from a list of (id, name, stock) tuples.
        """
        self._product_map.clear()
        display_list = []
        for pid, name, stock in product_rows:
            label = f"{name}  (ID:{pid}, Stock:{stock})"
            display_list.append(label)
            self._product_map[label] = pid
        self.cmb_product["values"] = display_list

    def populate_table(self, rows):
        """Clear and repopulate the transaction history table."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", "end", values=row)

    def clear_form(self):
        """Reset all form fields."""
        self.cmb_product.set("")
        self.txn_type.set("Stock-In")
        self.entry_qty.delete(0, tk.END)
        self.entry_remarks.delete(0, tk.END)

    def on_show(self):
        """Called when this screen becomes visible."""
        if self.handler:
            self.handler.refresh()

    # ── Internal ─────────────────────────────────────────────
    def _on_record_click(self):
        if self.handler:
            self.handler.record()

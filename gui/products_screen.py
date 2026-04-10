"""
products_screen.py — Product management screen UI (no business logic).
"""

import tkinter as tk
from tkinter import ttk
from config import BG, CARD_BG, BTN_SUCCESS, BTN_WARNING, BTN_DANGER, FONT_FAMILY


class ProductsScreen(tk.Frame):
    """Product list with Treeview, CRUD form, and search bar."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller

        # ── Products handler reference (set by App) ──────────
        self.handler = None

        # ── Header + search ──────────────────────────────────
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=24, pady=(20, 10))

        tk.Label(header, text="Product Management",
                 font=(FONT_FAMILY, 18, "bold"),
                 bg=BG, fg="#2c3e50").pack(side="left")

        # Search bar (right side)
        search_frame = tk.Frame(header, bg=BG)
        search_frame.pack(side="right")

        tk.Label(search_frame, text="Search:",
                 font=(FONT_FAMILY, 10), bg=BG, fg="#555").pack(side="left")
        self.entry_search = tk.Entry(search_frame, font=(FONT_FAMILY, 10),
                                     width=22, relief="solid", bd=1)
        self.entry_search.pack(side="left", padx=(6, 6), ipady=2)
        self.entry_search.bind("<KeyRelease>", lambda e: self._on_search())

        tk.Button(search_frame, text="Clear", font=(FONT_FAMILY, 9),
                  bg="#95a5a6", fg="white", relief="flat", cursor="hand2",
                  command=self._on_clear_search).pack(side="left", ipady=1)

        # ── Treeview ─────────────────────────────────────────
        tree_frame = tk.Frame(self, bg=BG)
        tree_frame.pack(fill="both", expand=True, padx=24)

        cols = ("ID", "Name", "Description", "Stock", "Unit")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                 show="headings", height=12,
                                 selectmode="browse")

        col_widths = {"ID": 50, "Name": 180, "Description": 260,
                      "Stock": 80, "Unit": 70}
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=col_widths.get(c, 100), anchor="center")

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical",
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # Clicking a row populates the form
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # ── Entry fields panel ───────────────────────────────
        form = tk.Frame(self, bg=CARD_BG, bd=0,
                        highlightbackground="#ddd", highlightthickness=1)
        form.pack(fill="x", padx=24, pady=(10, 20))

        # Row 1 — Name, Unit, Stock
        r1 = tk.Frame(form, bg=CARD_BG)
        r1.pack(fill="x", padx=16, pady=(12, 4))

        tk.Label(r1, text="Name:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.entry_name = tk.Entry(r1, font=(FONT_FAMILY, 10), width=28,
                                   relief="solid", bd=1)
        self.entry_name.pack(side="left", padx=(6, 20))

        tk.Label(r1, text="Unit:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.entry_unit = tk.Entry(r1, font=(FONT_FAMILY, 10), width=10,
                                   relief="solid", bd=1)
        self.entry_unit.insert(0, "pcs")
        self.entry_unit.pack(side="left", padx=(6, 20))

        tk.Label(r1, text="Stock:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.entry_stock = tk.Entry(r1, font=(FONT_FAMILY, 10), width=8,
                                    relief="solid", bd=1)
        self.entry_stock.pack(side="left", padx=(6, 0))

        # Row 2 — Description
        r2 = tk.Frame(form, bg=CARD_BG)
        r2.pack(fill="x", padx=16, pady=(4, 8))

        tk.Label(r2, text="Description:", font=(FONT_FAMILY, 10),
                 bg=CARD_BG, fg="#555").pack(side="left")
        self.entry_desc = tk.Entry(r2, font=(FONT_FAMILY, 10), width=60,
                                   relief="solid", bd=1)
        self.entry_desc.pack(side="left", padx=(6, 0), fill="x", expand=True)

        # Row 3 — Buttons
        r3 = tk.Frame(form, bg=CARD_BG)
        r3.pack(fill="x", padx=16, pady=(4, 12))

        btn_style = dict(font=(FONT_FAMILY, 10, "bold"), fg="white",
                         relief="flat", cursor="hand2", bd=0, padx=16)

        tk.Button(r3, text="Add Product", bg=BTN_SUCCESS,
                  activebackground="#219a52",
                  command=lambda: self._delegate("add"), **btn_style
                  ).pack(side="left", ipady=4, padx=(0, 8))

        tk.Button(r3, text="Update Product", bg=BTN_WARNING,
                  activebackground="#cf6d17",
                  command=lambda: self._delegate("update"), **btn_style
                  ).pack(side="left", ipady=4, padx=(0, 8))

        tk.Button(r3, text="Delete Product", bg=BTN_DANGER,
                  activebackground="#c0392b",
                  command=lambda: self._delegate("delete"), **btn_style
                  ).pack(side="left", ipady=4, padx=(0, 8))

        tk.Button(r3, text="Clear Fields", bg="#95a5a6",
                  activebackground="#7f8c8d",
                  command=self.clear_fields, **btn_style
                  ).pack(side="right", ipady=4)

        # Track selected product ID
        self._selected_id = None

    # ── View interface methods ───────────────────────────────
    def get_form_data(self):
        """Return dict with current form field values."""
        return {
            "name": self.entry_name.get().strip(),
            "description": self.entry_desc.get().strip(),
            "stock": self.entry_stock.get().strip(),
            "unit": self.entry_unit.get().strip(),
        }

    def get_selected_id(self):
        """Return the currently selected product ID."""
        return self._selected_id

    def get_search_term(self):
        """Return the current search field text."""
        return self.entry_search.get().strip()

    def populate_table(self, rows):
        """Clear and repopulate the product Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", "end", values=row)

    def clear_fields(self):
        """Clear all form fields and deselect the Treeview row."""
        self._selected_id = None
        for entry in (self.entry_name, self.entry_desc,
                      self.entry_stock, self.entry_unit):
            entry.delete(0, tk.END)
        self.entry_unit.insert(0, "pcs")
        for sel in self.tree.selection():
            self.tree.selection_remove(sel)

    def clear_search(self):
        """Clear the search field."""
        self.entry_search.delete(0, tk.END)

    def on_show(self):
        """Called when this screen becomes visible."""
        if self.handler:
            self.handler.refresh()

    # ── Internal callbacks ───────────────────────────────────
    def _on_tree_select(self, _event):
        """Populate form from selected Treeview row."""
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0], "values")
        self._selected_id = values[0]

        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, values[1])

        self.entry_desc.delete(0, tk.END)
        self.entry_desc.insert(0, values[2] if values[2] else "")

        self.entry_stock.delete(0, tk.END)
        self.entry_stock.insert(0, values[3])

        self.entry_unit.delete(0, tk.END)
        self.entry_unit.insert(0, values[4])

    def _on_search(self):
        if self.handler:
            self.handler.search()

    def _on_clear_search(self):
        self.clear_search()
        if self.handler:
            self.handler.refresh()

    def _delegate(self, action):
        """Forward button click to handler."""
        if self.handler:
            getattr(self.handler, action)()

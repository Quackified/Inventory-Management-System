"""
products_screen.py — Product management with ttkbootstrap.
Status tags: left-aligned with rounded colored background (like products_example.png).
Buttons: all plain/secondary except "Add Product" which is highlighted.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from config import (BG, BEIGE, WHITE, DARK_BROWN, OLIVE, GOLD, AMBER,
                    BTN_SUCCESS,
                    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
                    BORDER_LIGHT, INPUT_BORDER,
                    ROW_LOW_STOCK, ROW_EXPIRED, ROW_EVEN, ROW_ODD,
                    STATUS_ACTIVE, STATUS_LOW_STOCK, STATUS_EXPIRED,
                    FONT_FAMILY, ICON_FONT, PAD_SM, PAD_MD, PAD_LG, PAD_XL)
from gui.icons import get_icon
from gui.pagination import PaginationBar
from gui.context_menu import ContextMenu
from gui.action_button import ActionButtonMixin


class ProductsScreen(tk.Frame, ActionButtonMixin):
    """Product list — strict reference image replication."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self.handler = None

        # ── Header ───────────────────────────────────────────
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=PAD_XL, pady=(PAD_LG, PAD_SM))

        tk.Label(header, text="Product Management",
                 font=(FONT_FAMILY, 20, "bold"),
                 bg=BG, fg=DARK_BROWN).pack(side="left")

        # ── Toolbar card ─────────────────────────────────────
        toolbar_card = tk.Frame(self, bg=WHITE, bd=0,
                                highlightbackground=BORDER_LIGHT,
                                highlightthickness=1)
        toolbar_card.pack(fill="x", padx=PAD_XL, pady=(0, PAD_SM))

        toolbar = tk.Frame(toolbar_card, bg=WHITE, padx=16, pady=10)
        toolbar.pack(fill="x")

        # Search (left side)
        search_frame = tk.Frame(toolbar, bg=WHITE)
        search_frame.pack(side="left")

        tk.Label(search_frame, text=get_icon("search"),
                 font=(ICON_FONT, 12), fg=TEXT_MUTED,
                 bg=WHITE).pack(side="left", padx=(0, 6))

        self.entry_search = ttk.Entry(search_frame, font=(FONT_FAMILY, 10),
                                      width=24)
        self.entry_search.insert(0, "Search products...")
        self.entry_search.pack(side="left")

        self.entry_search.bind("<FocusIn>", self._search_focus_in)
        self.entry_search.bind("<FocusOut>", self._search_focus_out)
        self.entry_search.bind("<KeyRelease>", lambda e: self._on_search())

        # Buttons (right side) — all secondary except Add Product
        btn_area = tk.Frame(toolbar, bg=WHITE)
        btn_area.pack(side="right")

        # Add Product (highlighted — the ONLY coloured button)
        ttk.Button(btn_area, text="+ Add Product", bootstyle="success",
                   command=self._open_add
                   ).pack(side="right", padx=(6, 0))

        # Stock Out (plain)
        ttk.Button(btn_area, text="▼ Stock Out", bootstyle="secondary-outline",
                   command=lambda: self._open_stock("Stock-Out")
                   ).pack(side="right", padx=(4, 0))

        # Stock In (plain)
        ttk.Button(btn_area, text="▲ Stock In", bootstyle="secondary-outline",
                   command=lambda: self._open_stock("Stock-In")
                   ).pack(side="right", padx=(4, 0))

        # Export (plain dropdown — tight padding)
        export_mb = ttk.Menubutton(btn_area, text="Export",
                                   bootstyle="secondary-outline")
        export_menu = tk.Menu(export_mb, tearoff=0,
                              font=(FONT_FAMILY, 10), bg=WHITE,
                              fg=DARK_BROWN, activebackground=BEIGE,
                              borderwidth=1, relief="solid")
        export_menu.add_command(label="CSV", command=lambda: self._on_export("csv"))
        export_menu.add_command(label="Excel", command=lambda: self._on_export("xlsx"))
        export_mb["menu"] = export_menu
        export_mb.pack(side="right", padx=(4, 0))

        # ── Treeview ─────────────────────────────────────────
        tree_frame = tk.Frame(self, bg=WHITE, bd=0, highlightbackground=BORDER_LIGHT, highlightthickness=1)
        tree_frame.pack(fill="both", expand=True, padx=PAD_XL, pady=(0, PAD_SM))

        cols = ("ID", "Name", "Stock", "Unit", "Warehouse", "Category",
                "Threshold", "Expiry", "Status", "Batch", "")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                 show="headings", height=16,
                                 selectmode="browse")

        col_widths = {"ID": 44, "Name": 160, "Stock": 58, "Unit": 50,
                      "Warehouse": 110, "Category": 100, "Threshold": 68,
                      "Expiry": 90, "Status": 90, "Batch": 90, "": 40}
        for c in cols:
            self.tree.heading(c, text=c if c else "")
            # Status column aligned left; Actions column centred
            anchor_val = "w" if c == "Status" else "center"
            self.tree.column(c, width=col_widths.get(c, 80),
                             anchor=anchor_val, stretch=True)

        # Row tags for alternating + status coloring
        self.tree.tag_configure("evenrow", background=ROW_EVEN)
        self.tree.tag_configure("oddrow",  background=ROW_ODD)
        self.tree.tag_configure("status_active",    foreground=STATUS_ACTIVE)
        self.tree.tag_configure("status_low_stock", foreground=STATUS_LOW_STOCK)
        self.tree.tag_configure("status_expired",   foreground=STATUS_EXPIRED)

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical",
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self._selected_id = None
        self._action_col = "#11"
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self._init_action_buttons()

        # ── Pagination (bottom) ──────────────────────────────
        pager_frame = tk.Frame(self, bg=WHITE, bd=0,
                               highlightbackground=BORDER_LIGHT,
                               highlightthickness=1)
        pager_frame.pack(fill="x", padx=PAD_XL, pady=(0, PAD_LG))

        self.pager = PaginationBar(pager_frame,
                                   on_page_change=self._on_page_change,
                                   bg=WHITE)
        self.pager.pack(fill="x", padx=12, pady=6)

    # ── View interface ───────────────────────────────────────
    def get_selected_id(self):
        return self._selected_id

    def get_search_term(self):
        val = self.entry_search.get().strip()
        if val == "Search products...":
            return ""
        return val

    def populate_table(self, rows):
        self._selected_id = None
        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, row in enumerate(rows):
            status = row[9]
            stock, threshold = row[3], row[7]

            # Status — plain text, colored via tags
            if status == "Expired":
                display_status = "      Expired"
                status_tag = "status_expired"
            elif stock < threshold:
                display_status = "      Low Stock"
                status_tag = "status_low_stock"
            else:
                display_status = "      Active"
                status_tag = "status_active"

            display = (
                row[0], row[1], row[3], row[4],
                row[5], row[6], row[7],
                row[8] if row[8] else "—",
                display_status,
                row[11] if row[11] else "—",
                "",
            )

            alt_tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=display,
                             tags=(alt_tag, status_tag))

        self.after(50, self._refresh_action_buttons)

    def on_show(self):
        if self.handler:
            self.handler.refresh()

    # ── Internal callbacks ───────────────────────────────────
    def _on_tree_select(self, _event):
        sel = self.tree.selection()
        if sel:
            self._selected_id = self.tree.item(sel[0], "values")[0]

    def _on_action(self, item_id, x_root, y_root):
        """Called by ActionButtonMixin when an action button is clicked."""
        self._selected_id = self.tree.item(item_id, "values")[0]
        ContextMenu(
            self.winfo_toplevel(),
            x_root, y_root,
            on_edit=self._open_edit,
            on_delete=self._on_delete,
        )

    def _search_focus_in(self, _e):
        if self.entry_search.get() == "Search products...":
            self.entry_search.delete(0, tk.END)

    def _search_focus_out(self, _e):
        if not self.entry_search.get().strip():
            self.entry_search.insert(0, "Search products...")

    def _on_search(self):
        if self.handler:
            self.handler.search()

    def _on_delete(self):
        if self.handler:
            self.handler.delete()

    def _open_add(self):
        if self.handler:
            self.handler.open_add_popover()

    def _open_edit(self):
        if self.handler:
            self.handler.open_edit_popover()

    def _open_stock(self, txn_type):
        if not self._selected_id:
            from gui.dialogs import show_warning
            show_warning(self.winfo_toplevel(), "Selection",
                         "Select a product from the table first.")
            return
        if self.handler:
            self.handler.open_stock_popover(txn_type)

    def _on_export(self, fmt):
        if self.handler:
            self.handler.export(fmt)

    def _on_page_change(self, page, page_size):
        if self.handler:
            self.handler.refresh(page=page, page_size=page_size)

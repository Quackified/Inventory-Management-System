"""
warehouse_category_screen.py — Warehouse & Category management.
Same Products-style with pagination on BOTH panels.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from config import (BG, BEIGE, WHITE, DARK_BROWN, OLIVE, GOLD,
                    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
                    BORDER_LIGHT, ROW_EVEN, ROW_ODD,
                    FONT_FAMILY, ICON_FONT, PAD_SM, PAD_MD, PAD_LG, PAD_XL)
from gui.icons import get_icon
from gui.popover import Popover
from gui.context_menu import ContextMenu
from gui.pagination import PaginationBar
from gui.action_button import _ActionLabel, _BTN_SIZE


class WarehouseCategoryScreen(tk.Frame):
    """Two-panel screen for warehouses and categories — with pagination."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self.handler = None

        # ── Header ───────────────────────────────────────────
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=PAD_XL, pady=(PAD_LG, PAD_SM))

        tk.Label(header, text="Warehouses & Categories",
                 font=(FONT_FAMILY, 20, "bold"),
                 bg=BG, fg=DARK_BROWN).pack(side="left")

        # ── Warehouses Panel ─────────────────────────────────
        self._build_warehouse_panel()

        # ── Categories Panel ─────────────────────────────────
        self._build_category_panel()

    def _build_warehouse_panel(self):
        # ── Toolbar ──────────────────────────────────────────
        toolbar = tk.Frame(self, bg=WHITE, bd=0,
                           highlightbackground=BORDER_LIGHT,
                           highlightthickness=1)
        toolbar.pack(fill="x", padx=PAD_XL, pady=(0, PAD_SM))

        toolbar_inner = tk.Frame(toolbar, bg=WHITE, padx=16, pady=10)
        toolbar_inner.pack(fill="x")

        tk.Label(toolbar_inner, text=get_icon("warehouse"),
                 font=(ICON_FONT, 14), fg=OLIVE,
                 bg=WHITE).pack(side="left", padx=(0, 8))
        tk.Label(toolbar_inner, text="Warehouses / Stores",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=WHITE, fg=DARK_BROWN).pack(side="left")

        ttk.Button(toolbar_inner, text="+ Add", bootstyle="success",
                   command=self._open_add_warehouse
                   ).pack(side="right")

        # ── Treeview ─────────────────────────────────────────
        tree_frame = tk.Frame(self, bg=WHITE, bd=0,
                              highlightbackground=BORDER_LIGHT,
                              highlightthickness=1)
        tree_frame.pack(fill="both", expand=True, padx=PAD_XL, pady=(0, PAD_SM))

        cols = ("ID", "Name", "Location", "Active", "")
        self.wh_tree = ttk.Treeview(tree_frame, columns=cols,
                                    show="headings", height=5,
                                    selectmode="browse")
        widths = {"ID": 50, "Name": 200, "Location": 280, "Active": 60, "": 40}
        for c in cols:
            self.wh_tree.heading(c, text=c if c else "")
            self.wh_tree.column(c, width=widths.get(c, 100), anchor="center")

        self.wh_tree.tag_configure("evenrow", background=ROW_EVEN)
        self.wh_tree.tag_configure("oddrow",  background=ROW_ODD)

        scroll = ttk.Scrollbar(tree_frame, orient="vertical",
                               command=self.wh_tree.yview)
        self.wh_tree.configure(yscrollcommand=scroll.set)
        self.wh_tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Action button overlays for warehouse tree
        self._wh_action_btns = []
        self.wh_tree.bind("<MouseWheel>",
                          lambda e: self.after(30, self._refresh_wh_actions))

        # ── Pagination ───────────────────────────────────────
        wh_pager_frame = tk.Frame(self, bg=WHITE, bd=0,
                                  highlightbackground=BORDER_LIGHT,
                                  highlightthickness=1)
        wh_pager_frame.pack(fill="x", padx=PAD_XL, pady=(0, PAD_LG))
        
        self.wh_pager = PaginationBar(wh_pager_frame, bg=WHITE)
        self.wh_pager.pack(fill="x", padx=12, pady=4)

    def _build_category_panel(self):
        # ── Toolbar ──────────────────────────────────────────
        toolbar = tk.Frame(self, bg=WHITE, bd=0,
                           highlightbackground=BORDER_LIGHT,
                           highlightthickness=1)
        toolbar.pack(fill="x", padx=PAD_XL, pady=(0, PAD_SM))

        toolbar_inner = tk.Frame(toolbar, bg=WHITE, padx=16, pady=10)
        toolbar_inner.pack(fill="x")

        tk.Label(toolbar_inner, text=get_icon("products"),
                 font=(ICON_FONT, 14), fg=OLIVE,
                 bg=WHITE).pack(side="left", padx=(0, 8))
        tk.Label(toolbar_inner, text="Categories",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=WHITE, fg=DARK_BROWN).pack(side="left")

        ttk.Button(toolbar_inner, text="+ Add", bootstyle="success",
                   command=self._open_add_category
                   ).pack(side="right")

        # ── Treeview ─────────────────────────────────────────
        tree_frame = tk.Frame(self, bg=WHITE, bd=0,
                              highlightbackground=BORDER_LIGHT,
                              highlightthickness=1)
        tree_frame.pack(fill="both", expand=True, padx=PAD_XL, pady=(0, PAD_SM))

        cols = ("ID", "Name", "Description", "")
        self.cat_tree = ttk.Treeview(tree_frame, columns=cols,
                                     show="headings", height=5,
                                     selectmode="browse")
        widths = {"ID": 50, "Name": 200, "Description": 380, "": 40}
        for c in cols:
            self.cat_tree.heading(c, text=c if c else "")
            self.cat_tree.column(c, width=widths.get(c, 100), anchor="center")

        self.cat_tree.tag_configure("evenrow", background=ROW_EVEN)
        self.cat_tree.tag_configure("oddrow",  background=ROW_ODD)

        scroll = ttk.Scrollbar(tree_frame, orient="vertical",
                               command=self.cat_tree.yview)
        self.cat_tree.configure(yscrollcommand=scroll.set)
        self.cat_tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Action button overlays for category tree
        self._cat_action_btns = []
        self.cat_tree.bind("<MouseWheel>",
                           lambda e: self.after(30, self._refresh_cat_actions))

        # ── Pagination ───────────────────────────────────────
        cat_pager_frame = tk.Frame(self, bg=WHITE, bd=0,
                                   highlightbackground=BORDER_LIGHT,
                                   highlightthickness=1)
        cat_pager_frame.pack(fill="x", padx=PAD_XL, pady=(0, PAD_LG))
        
        self.cat_pager = PaginationBar(cat_pager_frame, bg=WHITE)
        self.cat_pager.pack(fill="x", padx=12, pady=4)

    # ── View interface ───────────────────────────────────────
    def populate_warehouses(self, rows):
        for item in self.wh_tree.get_children():
            self.wh_tree.delete(item)
        for i, row in enumerate(rows):
            active_text = "Yes" if row[3] else "No"
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.wh_tree.insert("", "end",
                                values=(row[0], row[1], row[2] or "", active_text, ""),
                                tags=(tag,))
        self.wh_pager.set_total(len(rows))
        self.after(50, self._refresh_wh_actions)

    def populate_categories(self, rows):
        for item in self.cat_tree.get_children():
            self.cat_tree.delete(item)
        for i, row in enumerate(rows):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.cat_tree.insert("", "end",
                                 values=(*row, ""),
                                 tags=(tag,))
        self.cat_pager.set_total(len(rows))
        self.after(50, self._refresh_cat_actions)

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

    # ── Action button overlays ────────────────────────────────
    def _make_action_btn(self, tree, item_id, col_id, callback):
        bbox = tree.bbox(item_id, column=col_id)
        if not bbox:
            return None
        x, y, w, h = bbox
        btn = _ActionLabel(tree, item_id, callback)
        bx = x + (w - _BTN_SIZE) // 2
        by = y + (h - _BTN_SIZE) // 2
        btn.place(x=bx, y=by, width=_BTN_SIZE, height=_BTN_SIZE)
        return btn

    def _refresh_wh_actions(self):
        for b in self._wh_action_btns:
            b.destroy()
        self._wh_action_btns.clear()
        for item_id in self.wh_tree.get_children():
            btn = self._make_action_btn(
                self.wh_tree, item_id, "#5", self._on_wh_action)
            if btn:
                self._wh_action_btns.append(btn)

    def _refresh_cat_actions(self):
        for b in self._cat_action_btns:
            b.destroy()
        self._cat_action_btns.clear()
        for item_id in self.cat_tree.get_children():
            btn = self._make_action_btn(
                self.cat_tree, item_id, "#4", self._on_cat_action)
            if btn:
                self._cat_action_btns.append(btn)

    def _on_wh_action(self, item_id, x_root, y_root):
        self.wh_tree.selection_set(item_id)
        ContextMenu(
            self.winfo_toplevel(), x_root, y_root,
            on_edit=self._open_edit_warehouse,
            on_delete=self._delete_warehouse,
        )

    def _on_cat_action(self, item_id, x_root, y_root):
        self.cat_tree.selection_set(item_id)
        ContextMenu(
            self.winfo_toplevel(), x_root, y_root,
            on_edit=self._open_edit_category,
            on_delete=self._delete_category,
        )

    # ── Popovers ─────────────────────────────────────────────
    def _open_add_warehouse(self):
        pop = Popover(self.winfo_toplevel(), title="Add Warehouse",
                      width=440, height=220)
        e_name = pop.add_field("Name:")
        e_loc  = pop.add_field("Location:")

        def on_save():
            if self.handler:
                self.handler.add_warehouse(
                    e_name.get().strip(), e_loc.get().strip())
            pop.close()

        pop.add_button("Save", command=on_save, style="success")
        pop.add_button("Cancel", command=pop.close, style="secondary-outline")

    def _open_edit_warehouse(self):
        sel = self.get_selected_warehouse()
        if not sel:
            from gui.dialogs import show_warning
            show_warning(self.winfo_toplevel(), "Selection",
                         "Select a warehouse first.")
            return

        pop = Popover(self.winfo_toplevel(), title="Edit Warehouse",
                      width=440, height=260)
        e_name   = pop.add_field("Name:", default=sel[1])
        e_loc    = pop.add_field("Location:", default=sel[2])
        e_active = pop.add_dropdown("Active:", values=["Yes", "No"],
                                    default=sel[3])

        def on_save():
            if self.handler:
                self.handler.update_warehouse(
                    sel[0], e_name.get().strip(), e_loc.get().strip(),
                    1 if e_active.get() == "Yes" else 0)
            pop.close()

        pop.add_button("Save", command=on_save, style="success")
        pop.add_button("Cancel", command=pop.close, style="secondary-outline")

    def _delete_warehouse(self):
        if self.handler:
            self.handler.delete_warehouse()

    def _open_add_category(self):
        pop = Popover(self.winfo_toplevel(), title="Add Category",
                      width=440, height=220)
        e_name = pop.add_field("Name:")
        e_desc = pop.add_field("Description:")

        def on_save():
            if self.handler:
                self.handler.add_category(
                    e_name.get().strip(), e_desc.get().strip())
            pop.close()

        pop.add_button("Save", command=on_save, style="success")
        pop.add_button("Cancel", command=pop.close, style="secondary-outline")

    def _open_edit_category(self):
        sel = self.get_selected_category()
        if not sel:
            from gui.dialogs import show_warning
            show_warning(self.winfo_toplevel(), "Selection",
                         "Select a category first.")
            return

        pop = Popover(self.winfo_toplevel(), title="Edit Category",
                      width=440, height=220)
        e_name = pop.add_field("Name:", default=sel[1])
        e_desc = pop.add_field("Description:", default=sel[2])

        def on_save():
            if self.handler:
                self.handler.update_category(
                    sel[0], e_name.get().strip(), e_desc.get().strip())
            pop.close()

        pop.add_button("Save", command=on_save, style="success")
        pop.add_button("Cancel", command=pop.close, style="secondary-outline")

    def _delete_category(self):
        if self.handler:
            self.handler.delete_category()
